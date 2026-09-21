from flask import Flask, request, jsonify, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt
import os
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

# Initialize Flask app, SQLAlchemy, and JWTManager
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///librarymanagmentsystem.db'
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_secret_key_here')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

db = SQLAlchemy(app)  # Create SQLAlchemy instance with app
jwt = JWTManager(app)
CORS(app)

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    permission_granted_at = db.Column(db.DateTime)  # Add permission_granted_at attribute

    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role
        self.permission_granted_at = None  # Initialize permission_granted_at attribute to None

    def has_permission_expired(self):
        if self.permission_granted_at:
            # Calculate the current date and time
            current_time = datetime.utcnow()
            # Check if 7 days have passed since the permission was granted
            if current_time > self.permission_granted_at + timedelta(days=7):
                return True
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'permission_granted_at': self.permission_granted_at.isoformat() if self.permission_granted_at else None
        }
    
class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

from datetime import datetime

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    authors = db.Column(db.String(255))
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    date_issued = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime)
    pdf_file = db.Column(db.String(255))
    content_text = db.Column(db.Text)

    section = db.relationship('Section', backref=db.backref('books', lazy=True))

    def is_issued(self):
        return self.date_issued is not None

    def is_overdue(self):
        if self.return_date and self.return_date < datetime.now():
            return True
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'content': self.content,
            'authors': self.authors,
            'section_id': self.section_id,
            'date_issued': self.date_issued.isoformat() if self.date_issued else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'pdf_file': self.pdf_file,
            'content_text': self.content_text
        }

class BookRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Pending')  # Add status attribute with a default value

    user = db.relationship('User', backref=db.backref('book_requests', lazy=True))
    book = db.relationship('Book', backref=db.backref('book_requests', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'status': self.status,
            'timestamp': self.timestamp.isoformat(),
            'book_name': self.book.name if self.book else None,
            'user_name': self.user.username if self.user else None,
            'days_since_accepted': getattr(self, 'days_since_accepted', None)
        }


with app.app_context():
    db.create_all()

# Define routes
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    
    if not username or not password or not role:
        return jsonify({'msg': 'Invalid input'}), 400

    # Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'msg': 'User already exists'}), 400

    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Create new user
    new_user = User(username=username, password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'msg': 'Registration successful'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
        access_token = create_access_token(identity={'username': user.username, 'role': user.role})
        return jsonify({
            'access_token': access_token,
            'role': user.role
        }), 200
    else:
        return jsonify({'msg': 'Invalid credentials'}), 401

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({'msg': f'Hello {current_user["username"]}, you are a {current_user["role"]}'}), 200



@app.route('/librarian/delete_book/<int:book_id>', methods=['POST'])
@jwt_required()
def delete_book(book_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'msg': 'Access denied'}), 403

    book = Book.query.get(book_id)
    if book:
        if book.pdf_file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], book.pdf_file + '.pdf')
            if os.path.exists(file_path):
                os.remove(file_path)
        db.session.delete(book)
        db.session.commit()
        return jsonify({'msg': 'Book deleted successfully'}), 200

    return jsonify({'msg': 'Book not found'}), 404

@app.route('/librarian/dashboard', methods=['GET'])
@jwt_required()
def librarian_dashboard():
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'msg': 'Access denied'}), 403

    sections = Section.query.all()
    books = Book.query.all()

    return jsonify({
        'username': current_user['username'],
        'sections': [s.to_dict() for s in sections],
        'books': [b.to_dict() for b in books]
    }), 200

@app.route('/librarian/add_section', methods=['POST'])
@jwt_required()
def add_section():
    current_user = get_jwt_identity()
    print(f"Current User: {current_user}")  # Debug line
    if current_user['role'] != 'librarian':
        return jsonify({'msg': 'Access denied'}), 403

    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if not name or not description:
        return jsonify({'msg': 'Invalid input'}), 400

    section = Section(name=name, description=description)
    db.session.add(section)
    db.session.commit()

    return jsonify({'msg': 'Section added successfully'}), 201


ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/librarian/add_book', methods=['POST'])
@jwt_required()
def add_book():
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'msg': 'Access denied'}), 403

    name = request.form.get('name')
    authors = request.form.get('authors')
    section_id = request.form.get('section')

    pdf_file = request.files.get('pdf_file')
    if pdf_file and allowed_file(pdf_file.filename):
        filename = secure_filename(pdf_file.filename)
        pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        pdf_filename_without_extension = os.path.splitext(filename)[0]
    else:
        pdf_filename_without_extension = ''

    book = Book(name=name, authors=authors, section_id=section_id, pdf_file=pdf_filename_without_extension)
    db.session.add(book)
    db.session.commit()

    return jsonify({'msg': 'Book added successfully'}), 201

@app.route('/librarian/book_requests', methods=['GET'])
@jwt_required()
def book_requests():
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'msg': 'Access denied'}), 403

    requests = BookRequest.query.all()
    for request in requests:
        if request.status == 'Accepted':
            request.days_since_accepted = (datetime.utcnow() - request.timestamp).days
        else:
            request.days_since_accepted = None

    return jsonify({
        'requests': [r.to_dict() for r in requests]
    }), 200

@app.route('/librarian/accept_request/<int:request_id>', methods=['POST'])
@jwt_required()
def accept_request(request_id):
    current_user = get_jwt_identity()
    
    # Ensure only librarians can access this endpoint
    if current_user['role'] != 'librarian':
        return jsonify({'msg': 'Access denied'}), 403

    request = BookRequest.query.get(request_id)
    if request:
        request.status = 'Read'
        db.session.commit()
        return jsonify({'msg': 'Book request accepted and updated to Read status'}), 200

    return jsonify({'msg': 'Book request not found'}), 404


@app.route('/librarian/deny_request/<int:request_id>', methods=['POST'])
@jwt_required()
def deny_request(request_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'msg': 'Access denied'}), 403

    request = BookRequest.query.get(request_id)
    if request:
        request.status = 'Denied'
        db.session.commit()
        return jsonify({'msg': 'Book request denied'}), 200

    return jsonify({'msg': 'Book request not found'}), 404



@app.route('/librarian/update_book/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'msg': 'Access denied'}), 403

    book = Book.query.get(book_id)
    if book:
        data = request.get_json()
        book.name = data.get('name')
        book.authors = data.get('authors')
        book.section_id = data.get('section')
        db.session.commit()
        return jsonify({'msg': 'Book updated successfully'}), 200

    return jsonify({'msg': 'Book not found'}), 404

@app.route('/librarian/delete_section/<int:section_id>', methods=['POST'])
@jwt_required()
def delete_section(section_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'msg': 'Access denied'}), 403

    section = Section.query.get(section_id)
    if section:
        db.session.delete(section)
        db.session.commit()
        return jsonify({'msg': 'Section deleted successfully'}), 200

    return jsonify({'msg': 'Section not found'}), 404


@app.route('/librarian/sections', methods=['GET'])
@jwt_required()
def get_sections():
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'msg': 'Access denied'}), 403

    sections = Section.query.all()

    return jsonify({
        'sections': [s.to_dict() for s in sections]
    }), 200
@app.route('/librarian/section/<int:section_id>', methods=['GET'])
@jwt_required()
def get_section(section_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'msg': 'Access denied'}), 403

    section = Section.query.get_or_404(section_id)
    return jsonify(section.to_dict()), 200

@app.route('/librarian/update_section/<int:section_id>', methods=['PUT'])
@jwt_required()
def update_section(section_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'librarian':
        return jsonify({'msg': 'Access denied'}), 403

    section = Section.query.get_or_404(section_id)
    
    data = request.get_json()
    if not data.get('name') or not data.get('description'):
        return jsonify({'msg': 'Invalid input'}), 400

    section.name = data['name']
    section.description = data['description']
    db.session.commit()

    return jsonify({'msg': 'Section updated successfully'}), 200



# User


@app.route('/user/dashboard', methods=['GET'])
@jwt_required()
def user_dashboard():
    current_user = get_jwt_identity()
    if current_user['role'] != 'user':
        return jsonify({'msg': 'Access denied'}), 403

    # Fetch the user's book requests
    user = User.query.filter_by(username=current_user['username']).first()
    requests = BookRequest.query.filter_by(user_id=user.id).all()

    # Fetch all sections and books
    sections = Section.query.all()
    books_by_section = {}

    for section in sections:
        books = Book.query.filter_by(section_id=section.id).all()
        books_by_section[section.name] = []

        for book in books:
            # Check if this book has been requested and get its request status
            request_status = next((req.status for req in requests if req.book_id == book.id), None)

            books_by_section[section.name].append({
                'id': book.id,
                'name': book.name,
                'authors': book.authors,
                'pdf_file': book.pdf_file,
                'requestStatus': request_status
            })

    return jsonify({
        'username': current_user['username'],
        'message': 'Welcome User',
        'sections': books_by_section
    }), 200




@app.route('/user/request_book/<int:book_id>', methods=['POST'])
@jwt_required()
def request_book(book_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'user':
        return jsonify({'msg': 'Access denied'}), 403

    user = User.query.filter_by(username=current_user['username'], role='user').first()
    if user:
        if len(user.book_requests) >= 5:
            return jsonify({'msg': 'You have reached the limit of 5 book requests.'}), 403
        else:
            book = Book.query.get(book_id)
            if book:
                existing_request = BookRequest.query.filter_by(user_id=user.id, book_id=book_id).first()
                if existing_request:
                    return jsonify({'msg': 'You have already requested this book'}), 400
                if user.has_permission_expired():
                    return jsonify({'msg': 'Your permission to request books has expired.'}), 403

                book_request = BookRequest(user_id=user.id, book_id=book_id)
                db.session.add(book_request)
                db.session.commit()
                return jsonify({'msg': 'Book request sent successfully'}), 200
            return jsonify({'msg': 'Book not found'}), 404
    return jsonify({'msg': 'User not found'}), 404




from flask_jwt_extended import jwt_required, get_jwt_identity





@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
