from datetime import datetime

from app.extensions import db


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    authors = db.Column(db.String(255))
    section_id = db.Column(
        db.Integer,
        db.ForeignKey('section.id'),
        nullable=False
    )
    date_issued = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime)
    pdf_file = db.Column(db.String(255))
    content_text = db.Column(db.Text)

    section = db.relationship(
        'Section',
        backref=db.backref('books', lazy=True)
    )

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
            'date_issued': (
                self.date_issued.isoformat()
                if self.date_issued else None
            ),
            'return_date': (
                self.return_date.isoformat()
                if self.return_date else None
            ),
            'pdf_file': self.pdf_file,
            'content_text': self.content_text
        }