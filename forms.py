from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField, FileField
from text_extractor.config import Config
from wtforms import StringField, SubmitField, DateField, SelectField, MultipleFileField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError, InputRequired
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