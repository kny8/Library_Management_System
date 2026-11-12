import bcrypt
import os

from datetime import datetime, timedelta

from flask import (
    Blueprint,
    request,
    jsonify,
    send_from_directory,
    current_app
)

from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import User, Section, Book, BookRequest


api = Blueprint('api', __name__)


# Authentication routes

@api.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if not username or not password or not role:
        return jsonify({'msg': 'Invalid input'}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'msg': 'User already exists'}), 400

    hashed_password = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    )

    new_user = User(
        username=username,
        password=hashed_password,
        role=role
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'msg': 'Registration successful'}), 201


@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
        access_token = create_access_token(
            identity={'username': user.username, 'role': user.role}
        )

        return jsonify({
            'access_token': access_token,
            'role': user.role
        }), 200

    return jsonify({'msg': 'Invalid credentials'}), 401


@api.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()

    return jsonify({
        'msg': f'Hello {current_user["username"]}, you are a {current_user["role"]}'
    }), 200


# Librarian routes

@api.route('/librarian/delete_book/<int:book_id>', methods=['POST'])
@jwt_required()
def delete_book(book_id):
    current_user = get_jwt_identity()

    if current_user['role'] != 'librarian':
        return jsonify({'msg': 'Access denied'}), 403

    book = Book.query.get(book_id)

    if book:
        if book.pdf_file:
            file_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                book.pdf_file + '.pdf'
            )

            if os.path.exists(file_path):
                os.remove(file_path)

        db.session.delete(book)
        db.session.commit()

        return jsonify({'msg': 'Book deleted successfully'}), 200

    return jsonify({'msg': 'Book not found'}), 404


@api.route('/librarian/dashboard', methods=['GET'])
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


@api.route('/librarian/add_section', methods=['POST'])
@jwt_required()
def add_section():
    current_user = get_jwt_identity()

    print(f"Current User: {current_user}")

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
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@api.route('/librarian/add_book', methods=['POST'])
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

        pdf_file.save(
            os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        )

        pdf_filename_without_extension = os.path.splitext(filename)[0]
    else:
        pdf_filename_without_extension = ''

    book = Book(
        name=name,
        authors=authors,
        section_id=section_id,
        pdf_file=pdf_filename_without_extension
    )

    db.session.add(book)
    db.session.commit()

    return jsonify({'msg': 'Book added successfully'}), 201


@api.route('/librarian/book_requests', methods=['GET'])
@jwt_required()
def book_requests():
    current_user = get_jwt_identity()

    if current_user['role'] != 'librarian':
        return jsonify({'msg': 'Access denied'}), 403

    requests = BookRequest.query.all()

    for book_request in requests:
        if book_request.status == 'Accepted':
            book_request.days_since_accepted = (
                datetime.utcnow() - book_request.timestamp
            ).days
        else:
            book_request.days_since_accepted = None

    return jsonify({
        'requests': [r.to_dict() for r in requests]
    }), 200


@api.route('/librarian/accept_request/<int:request_id>', methods=['POST'])
@jwt_required()
def accept_request(request_id):
    current_user = get_jwt_identity()

    if current_user['role'] != 'librarian':
        return jsonify({'msg': 'Access denied'}), 403

    book_request = BookRequest.query.get(request_id)

    if book_request:
        book_request.status = 'Read'
        db.session.commit()

        return jsonify({
            'msg': 'Book request accepted and updated to Read status'
        }), 200

    return jsonify({'msg': 'Book request not found'}), 404


@api.route('/librarian/deny_request/<int:request_id>', methods=['POST'])
@jwt_required()
def deny_request(request_id):
    current_user = get_jwt_identity()

    if current_user['role'] != 'librarian':
        return jsonify({'msg': 'Access denied'}), 403

    book_request = BookRequest.query.get(request_id)

    if book_request:
        book_request.status = 'Denied'
        db.session.commit()

        return jsonify({'msg': 'Book request denied'}), 200

    return jsonify({'msg': 'Book request not found'}), 404


@api.route('/librarian/update_book/<int:book_id>', methods=['PUT'])
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


@api.route('/librarian/delete_section/<int:section_id>', methods=['POST'])
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


@api.route('/librarian/sections', methods=['GET'])
@jwt_required()
def get_sections():
    current_user = get_jwt_identity()

    if current_user['role'] != 'librarian':
        return jsonify({'msg': 'Access denied'}), 403

    sections = Section.query.all()

    return jsonify({
        'sections': [s.to_dict() for s in sections]
    }), 200


@api.route('/librarian/section/<int:section_id>', methods=['GET'])
@jwt_required()
def get_section(section_id):
    current_user = get_jwt_identity()

    if current_user['role'] != 'librarian':
        return jsonify({'msg': 'Access denied'}), 403

    section = Section.query.get_or_404(section_id)

    return jsonify(section.to_dict()), 200


@api.route('/librarian/update_section/<int:section_id>', methods=['PUT'])
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


# User routes

@api.route('/user/dashboard', methods=['GET'])
@jwt_required()
def user_dashboard():
    current_user = get_jwt_identity()

    if current_user['role'] != 'user':
        return jsonify({'msg': 'Access denied'}), 403

    user = User.query.filter_by(
        username=current_user['username']
    ).first()

    requests = BookRequest.query.filter_by(user_id=user.id).all()

    sections = Section.query.all()
    books_by_section = {}

    for section in sections:
        books = Book.query.filter_by(section_id=section.id).all()
        books_by_section[section.name] = []

        for book in books:
            request_status = next(
                (
                    req.status
                    for req in requests
                    if req.book_id == book.id
                ),
                None
            )

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


@api.route('/user/request_book/<int:book_id>', methods=['POST'])
@jwt_required()
def request_book(book_id):
    current_user = get_jwt_identity()

    if current_user['role'] != 'user':
        return jsonify({'msg': 'Access denied'}), 403

    user = User.query.filter_by(
        username=current_user['username'],
        role='user'
    ).first()

    if user:
        if len(user.book_requests) >= 5:
            return jsonify({
                'msg': 'You have reached the limit of 5 book requests.'
            }), 403

        book = Book.query.get(book_id)

        if book:
            existing_request = BookRequest.query.filter_by(
                user_id=user.id,
                book_id=book_id
            ).first()

            if existing_request:
                return jsonify({
                    'msg': 'You have already requested this book'
                }), 400

            if user.has_permission_expired():
                return jsonify({
                    'msg': 'Your permission to request books has expired.'
                }), 403

            book_request = BookRequest(
                user_id=user.id,
                book_id=book_id
            )

            db.session.add(book_request)
            db.session.commit()

            return jsonify({
                'msg': 'Book request sent successfully'
            }), 200

        return jsonify({'msg': 'Book not found'}), 404

    return jsonify({'msg': 'User not found'}), 404


# Uploaded files

@api.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        filename
    )