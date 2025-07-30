from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField, FileField
from text_extractor.config import Config
from wtforms import StringField, SubmitField, DateField, SelectField, MultipleFileField, IntegerField, TextAreaField, TimeField, FloatField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError, InputRequired, AnyOf
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from .models import User 


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Login')

class UploadForm(FlaskForm):
    file = FileField(
        'Upload Image File', 
        validators=[FileAllowed(Config.ALLOWED_EXTENSIONS, 'Invalid file format.')],
        render_kw={"multiple": True} # This line enables multiple file selection
    )
    submit = SubmitField('Upload')


class ImageForm(FlaskForm):
    image_name = StringField('Image Name', validators=[DataRequired()])
    submit = SubmitField('Extract Text')

class ImageCaptureForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    image_data = HiddenField('Image Data', validators=[InputRequired()])

class UserCreationForm(FlaskForm):
    employee_id = StringField('Employee ID', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    job_title = StringField('Job Title', validators=[DataRequired()])
    department = StringField('Department', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create User')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already exists. Please choose a different username.')

class PatientForm(FlaskForm):
    surname = StringField('Surname', validators=[DataRequired(), Length(max=50)])
    given_name = StringField('Given Name', validators=[DataRequired(), Length(max=50)])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[Length(max=15)])
    email = StringField('Email', validators=[Email(), Length(max=100)])
    local_address = StringField('Local Address', validators=[Length(max=200)])
    emergency_contact = StringField('Emergency Contact', validators=[Length(max=200)])
    village = StringField('Village', validators=[Length(max=50)])
    parish = StringField('Parish', validators=[Length(max=50)])
    sub_county = StringField('Sub County', validators=[Length(max=50)])
    district = StringField('District', validators=[Length(max=50)])
    submit = SubmitField('Submit')

class FileUploadForm(FlaskForm):
    file = FileField('File', validators=[DataRequired()])
    submit = SubmitField('Upload')
    ward = SelectField('Ward', choices=[('maternity', 'Maternity'), ('surgical', 'Surgical'), ('opm', 'OPM')], validators=[DataRequired()])

class LaboratoryRequestForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    sex = StringField('Sex', validators=[DataRequired()])
    age = StringField('Age', validators=[DataRequired()])
    ward = StringField('Ward', validators=[DataRequired()])
    material = StringField('Material', validators=[DataRequired()])
    time = StringField('Time', validators=[DataRequired()])
    date = StringField('Date', validators=[DataRequired()])
    ip_no = StringField('IP No.', validators=[DataRequired()])
    examination_required = StringField('Examination Required', validators=[DataRequired()])
    clinical_notes = StringField('Clinical Notes', validators=[DataRequired()])
    rec_in_lab_time = StringField('Rec. in Lab Time', validators=[DataRequired()])
    lab_no = StringField('Lab No.', validators=[DataRequired()])
    results = StringField('Results', validators=[DataRequired()])
    rec_by = StringField('Rec. By', validators=[DataRequired()])
    examined_by = StringField('Examined By', validators=[DataRequired()])
    submit = SubmitField('Submit')

class InpatientTreatmentSheetForm(FlaskForm):
    ward = StringField('Ward', validators=[DataRequired()])
    bed_number = StringField('Bed Number', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    inpatient_number = StringField('Inpatient Number', validators=[DataRequired()])
    address = StringField('Address')
    age = StringField('Age', validators=[DataRequired()])
    sex = StringField('Sex', validators=[DataRequired()])
    next_of_kin = TextAreaField('Next Of Kin Information')
    admission_date = DateField('Admission Date', validators=[DataRequired()])
    admission_time = TimeField('Time', validators=[DataRequired()])
    referred_from = StringField('Referred From')
    discharge_date = DateField('Discharge Date', validators=[DataRequired()])
    discharge_status = StringField('Status Of Discharge', validators=[DataRequired()])
    final_diagnosis = TextAreaField('Final Diagnosis', validators=[DataRequired()])
    surgical_procedure = TextAreaField('Surgical procedure, special services')
    follow_up_date = DateField('Follow up date')
    follow_up_place = StringField('Place')
    treatment_instructions = TextAreaField('Treatment instructions after discharge')
    clinical_notes = TextAreaField('CLINICAL NOTES')
    provisional_diagnosis = TextAreaField('Provisional Diagnosis', validators=[DataRequired()])
    submit = SubmitField('Submit')

class OperationReportForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    ward = StringField('Ward', validators=[DataRequired()])
    bed_no = StringField('Bed No', validators=[DataRequired()])
    register_no = StringField('Register No', validators=[DataRequired()])
    operation = StringField('Operation', validators=[DataRequired()])
    class_no = StringField('Class No', validators=[DataRequired()])
    surgeon = StringField('Surgeon', validators=[DataRequired()])
    anaesthesia = StringField('Types of Anaesthesia', validators=[DataRequired()])
    incision = TextAreaField('Incision', validators=[DataRequired()])
    findings_procedure = TextAreaField('Findings and Procedure', validators=[DataRequired()])
    instructions = TextAreaField('Instructions to Ward', validators=[DataRequired()])
    operation_fee = FloatField('Operation Fee', validators=[DataRequired()])
    signature = StringField('Signature', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ReferralNoteForm(FlaskForm):
    date_of_referral = DateField('Date of Referral', validators=[DataRequired()])
    to = StringField('To', validators=[DataRequired()])
    from_health_unit = StringField('FROM: Health Unit', validators=[DataRequired()])
    referral_number = StringField('Referral Number', validators=[DataRequired()])
    reference_patient_name = StringField('REFERENCE: Patient name', validators=[DataRequired()])
    patient_number = StringField('Patient Number', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    sex = SelectField('Sex', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[DataRequired()])
    date_of_first_visit = DateField('Date of first visit', validators=[DataRequired()])
    history_and_symptoms = TextAreaField('History and symptoms', validators=[DataRequired()])
    investigations_done = TextAreaField('Investigations done', validators=[DataRequired()])
    diagnosis = TextAreaField('Diagnosis', validators=[DataRequired()])
    treatment_given = TextAreaField('Treatment Given', validators=[DataRequired()])
    reason_for_referral = TextAreaField('Reason For Referral', validators=[DataRequired()])
    clinician_name = StringField('Name of clinician', validators=[DataRequired()])
    clinician_contact = StringField('Telephone Contact', validators=[DataRequired()])
    date_of_arrival = DateField('Date of arrival')
    date_of_discharge = DateField('Date of discharge')
    further_investigations_done = TextAreaField('Further Investigations Done')
    further_diagnosis = TextAreaField('Diagnosis')
    further_treatments_given = TextAreaField('Treatments Given')
    treatment_or_surveillance = TextAreaField('Treatment or surveillance to be continued')
    remarks = TextAreaField('Remarks')
    further_clinician_name = StringField('Name of clinician')
    further_clinician_contact = StringField('Tel. Contact')
    submit = SubmitField('Submit')