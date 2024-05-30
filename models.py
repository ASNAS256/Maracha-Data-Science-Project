from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from text_extractor import db
import sqlalchemy as sa
from datetime import datetime

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

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    surname = db.Column(db.String(50), nullable=False)
    given_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    local_address = db.Column(db.String(200), nullable=True)
    emergency_contact = db.Column(db.String(200), nullable=True)
    village = db.Column(db.String(50), nullable=True)
    parish = db.Column(db.String(50), nullable=True)
    sub_county = db.Column(db.String(50), nullable=True)
    district = db.Column(db.String(50), nullable=True)

class FileRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # 'original', 'extracted', 'other_images', 'documents'
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)