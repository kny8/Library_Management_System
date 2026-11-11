import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-this")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///librarymanagmentsystem.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "dev-jwt-secret-change-this"
    )

    # Keep the existing uploads directory: backend/uploads
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "uploads"
    )
