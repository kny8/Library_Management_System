from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Create extension instances without binding them to a Flask app.
db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
