import os

from flask import Flask

from app.config import Config
from app.extensions import db, jwt, cors


def create_app(config_class=Config):

    # Preserve the existing project-level instance directory
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..')
    )

    instance_path = os.path.join(project_root, 'instance')
    os.makedirs(instance_path, exist_ok=True)

    app = Flask(__name__, instance_path=instance_path)

    # Load application configuration
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Import models so SQLAlchemy registers them
    from app.models import User, Section, Book, BookRequest

    # Register API blueprint
    from app.routes import api
    app.register_blueprint(api)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app