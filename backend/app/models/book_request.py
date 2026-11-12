from datetime import datetime

from app.extensions import db


class BookRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )
    book_id = db.Column(
        db.Integer,
        db.ForeignKey('book.id'),
        nullable=False
    )
    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    status = db.Column(
        db.String(20),
        nullable=False,
        default='Pending'
    )

    user = db.relationship(
        'User',
        backref=db.backref('book_requests', lazy=True)
    )
    book = db.relationship(
        'Book',
        backref=db.backref('book_requests', lazy=True)
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'status': self.status,
            'timestamp': self.timestamp.isoformat(),
            'book_name': self.book.name if self.book else None,
            'user_name': self.user.username if self.user else None,
            'days_since_accepted': getattr(
                self,
                'days_since_accepted',
                None
            )
        }