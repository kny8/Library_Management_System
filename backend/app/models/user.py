from datetime import datetime, timedelta

from app.extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    permission_granted_at = db.Column(db.DateTime)

    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role
        self.permission_granted_at = None

    def has_permission_expired(self):
        if self.permission_granted_at:
            current_time = datetime.utcnow()

            if current_time > self.permission_granted_at + timedelta(days=7):
                return True

        return False

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'permission_granted_at': (
                self.permission_granted_at.isoformat()
                if self.permission_granted_at else None
            )
        }