from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from text_extractor import db
import sqlalchemy as sa

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.String(100), nullable=True)  # Add the employee_id field
    email = db.Column(db.String(100), nullable=True)  # Add the email field
    job_title = db.Column(db.String(100), nullable=True)  # Add the job_title field
    department = db.Column(db.String(100), nullable=True)  # Add the department field

    images = db.relationship('Image', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
