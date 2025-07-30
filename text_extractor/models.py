from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from text_extractor import db
import sqlalchemy as sa
from datetime import datetime, time


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
    # In User class
extracted_texts = db.relationship('ExtractedTextRecord', backref='user', lazy=True)

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
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ward = db.Column(db.String(50), nullable=True)  # Adding the ward attribute

class LaboratoryRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    ward = db.Column(db.String(100), nullable=False)
    material = db.Column(db.String(100), nullable=False)
    time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    ip_no = db.Column(db.String(50), nullable=False)
    examination_required = db.Column(db.String(200), nullable=False)
    clinical_notes = db.Column(db.Text, nullable=True)
    rec_in_lab_time = db.Column(db.Time, nullable=False)
    lab_no = db.Column(db.String(50), nullable=False)
    results = db.Column(db.Text, nullable=True)
    rec_by = db.Column(db.String(100), nullable=False)
    examined_by = db.Column(db.String(100), nullable=False)
    
class InpatientTreatmentSheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ward = db.Column(db.String(100), nullable=False)
    bed_number = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    inpatient_number = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    next_of_kin = db.Column(db.Text)
    admission_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    admission_time = db.Column(db.Time, nullable=False)
    referred_from = db.Column(db.String(200))
    discharge_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    discharge_status = db.Column(db.String(100), nullable=False)
    final_diagnosis = db.Column(db.Text, nullable=False)
    surgical_procedure = db.Column(db.Text)
    follow_up_date = db.Column(db.Date)
    follow_up_place = db.Column(db.String(200))
    treatment_instructions = db.Column(db.Text)
    clinical_notes = db.Column(db.Text)
    provisional_diagnosis = db.Column(db.Text, nullable=False)

class OperationReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ward = db.Column(db.String(50), nullable=False)
    bed_no = db.Column(db.String(10), nullable=False)
    register_no = db.Column(db.String(50), nullable=False)
    operation = db.Column(db.String(200), nullable=False)
    class_no = db.Column(db.String(50), nullable=False)
    surgeon = db.Column(db.String(100), nullable=False)
    anaesthesia = db.Column(db.String(100), nullable=False)
    incision = db.Column(db.Text, nullable=False)
    findings_procedure = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    operation_fee = db.Column(db.Float, nullable=False)
    signature = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)

class ReferralNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_of_referral = db.Column(db.Date, nullable=False)
    to = db.Column(db.String(200), nullable=False)
    from_health_unit = db.Column(db.String(200), nullable=False)
    referral_number = db.Column(db.String(100), nullable=False)
    reference_patient_name = db.Column(db.String(200), nullable=False)
    patient_number = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    date_of_first_visit = db.Column(db.Date, nullable=False)
    history_and_symptoms = db.Column(db.Text, nullable=False)
    investigations_done = db.Column(db.Text, nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    treatment_given = db.Column(db.Text, nullable=False)
    reason_for_referral = db.Column(db.Text, nullable=False)
    clinician_name = db.Column(db.String(200), nullable=False)
    clinician_contact = db.Column(db.String(20), nullable=False)
    date_of_arrival = db.Column(db.Date)
    date_of_discharge = db.Column(db.Date)
    further_investigations_done = db.Column(db.Text)
    further_diagnosis = db.Column(db.Text)
    further_treatments_given = db.Column(db.Text)
    treatment_or_surveillance = db.Column(db.Text)
    remarks = db.Column(db.Text)
    further_clinician_name = db.Column(db.String(200))
    further_clinician_contact = db.Column(db.String(20))

class ExtractedTextRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    extracted_text = db.Column(db.Text, nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Optional link to user
