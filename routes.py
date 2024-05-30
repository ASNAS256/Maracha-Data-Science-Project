import os
from flask import (
    Flask,
    render_template, 
    request, 
    flash,
    redirect,
    url_for,
    jsonify,
    send_from_directory
)
from flask.views import MethodView
from werkzeug.utils import secure_filename
from .forms import (
    UploadForm, 
    ImageForm, 
    UserCreationForm, 
    LoginForm, 
    ImageCaptureForm,
    PatientForm,
    FileUploadForm
)
from .config import Config
from text_extractor import app, db
from .models import User, Image, Patient, FileRecord
from flask_login import (
    login_user, 
    login_required, 
    logout_user, 
    current_user
)
from text_extractor.utils import delete_image_file
import uuid
from  .text_image_fucntionality import TextExtractor
import base64
import textwrap

# Define all view classes here

class LoginView(MethodView):
    def get(self):
        form = LoginForm()
        return render_template('login.html', form=form)

    def post(self):
        form = LoginForm(request.form)
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('index'))

            flash('Invalid credentials! Please try again.', 'error')
        return render_template('login.html', form=form)

class LogoutView(MethodView):
    decorators = [login_required]

    def get(self):
        logout_user()
        flash('You have been logged out successfully!', 'success')
        return redirect(url_for('login'))

class UserCreationView(MethodView):
    def get(self):
        form = UserCreationForm()
        return render_template('create_user.html', form=form)

    def post(self):
        form = UserCreationForm(request.form)
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            # Create a new user
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            flash('User created successfully!', 'success')
            return redirect(url_for('login'))

        return render_template('create_user.html', form=form)

class ImageViewerView(MethodView):
    decorators = [login_required]

    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

    def get(self):
        form = UploadForm()
        image_form = ImageForm()
        user_images = Image.query.filter_by(user_id=current_user.id).all()
        return render_template(
            'dashboard.html',
            form=form, 
            user_images=user_images,
            image_form=image_form,
            hand_written_segments=None
        )

    def post(self):
        form = UploadForm()
        if form.validate_on_submit():
            files = request.files.getlist('file') # Get list of files
            for file in files:
                if file and self.allowed_file(file.filename):
                    # Generate a unique identifier
                    unique_identifier = str(uuid.uuid4())
                    # Get the file extension
                    file_extension = os.path.splitext(file.filename)[1]
                    # Create a unique filename by combining the identifier and extension
                    filename = f"{unique_identifier}{file_extension}"

                    # Save the file with the unique filename
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                    new_image = Image(filename=filename, user=current_user)
                    db.session.add(new_image)

            db.session.commit()
            flash('Files successfully uploaded', 'success')
            return redirect(url_for('gallery'))
        return render_template('upload.html', form=form)

class GalleryView(MethodView):
    decorators = [login_required]
    def get(self):
        form = ImageForm()
        if current_user.is_authenticated:
            user_images = Image.query.filter_by(user_id=current_user.id).all()

            return render_template(
                'gallery.html', 
                image_files=user_images, 
                form=form,
                enumerate=enumerate,
                str=str,
                image_name=None
            )
        else:
            return render_template(
                'gallery.html',
                image_files=None,
                form=form,
                enumerate=enumerate,
                str=str,
                image_name=None
            )

    def post(self):
        form = ImageForm()
        if form.validate_on_submit():
            data = ""
            image_id = form.image_name.data
            image = Image.query.filter_by(id=image_id).first()
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename) 
            text_extractor = TextExtractor(image_path)
            hand_written_segments = text_extractor.extract_handwritten_segments()

            for i, segment in enumerate(hand_written_segments, start=1):
                segment_text = segment['text']
                wrapped_text = textwrap.wrap(segment_text, width=70)

                formatted_segment_text = f"Segment {i} - Handwritten Text:\n"
                formatted_segment_text += '\n'.join(['    ' + line for line in wrapped_text])
                formatted_segment_text += '\n\n'

                data += formatted_segment_text

            user_images = Image.query.filter_by(user_id=current_user.id).all()
            return render_template(
                'gallery.html',
                image_files=user_images,
                form=form,
                hand_written_segments=data,
                enumerate=enumerate,
                str=str,
                image_name=image.filename
            )

        else:
            flash('Invalid form submission', 'danger')

        return redirect(url_for('gallery'))

class CaptureImageView(MethodView):
    decorators = [login_required]

    def get(self):
        form = UploadForm()
        return render_template('capture.html', form=form)

    def post(self):
        form = UploadForm()
        if form.validate_on_submit():
            image_data = request.form.get('image_data')

            if image_data:
                unique_identifier = str(uuid.uuid4())
                file_extension = '.jpg'
                filename = f"{unique_identifier}{file_extension}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                with open(file_path, 'wb') as image_file:
                    image_data_bytes = base64.b64decode(image_data.split(',')[1])
                    image_file.write(image_data_bytes)

                new_image = Image(filename=filename, user=current_user)
                db.session.add(new_image)
                db.session.commit()

                flash('Image captured and processed successfully!', 'success')
                return redirect(url_for('capture_image'))
        else:
            flash('Invalid form submission', 'danger')

        return render_template('capture.html', form=form)

class DeleteImageView(MethodView):
    decorators = [login_required]
    
    def get(self, image_id):
        image = Image.query.get(image_id)

        if image and image.user_id == current_user.id:
            try:
                delete_image_file(image.filename)
                db.session.delete(image)
                db.session.commit()

                flash("Image deleted successfully.", "success")

            except Exception as e:
                flash("An error occurred while deleting the image", "danger")

        return redirect(url_for('index'))

class EHRView(MethodView):
    decorators = [login_required]

    def get(self):
        return render_template('ehr.html')

class PatientInformationView(MethodView):
    decorators = [login_required]

    def get(self, patient_id=None):
        if patient_id:
            patient = Patient.query.get(patient_id)
            if not patient:
                flash('Patient not found.', 'danger')
                return redirect(url_for('patient_information'))
            form = PatientForm(obj=patient)
            return render_template('edit_patient.html', form=form, patient=patient)
        
        form = PatientForm()
        patients = Patient.query.all()
        return render_template('patient_information.html', form=form, patients=patients)

    def post(self, patient_id=None):
        form = PatientForm(request.form)
        if form.validate_on_submit():
            if patient_id:
                patient = Patient.query.get(patient_id)
                if not patient:
                    flash('Patient not found.', 'danger')
                    return redirect(url_for('patient_information'))

                patient.surname = form.surname.data
                patient.given_name = form.given_name.data
                patient.date_of_birth = form.date_of_birth.data
                patient.gender = form.gender.data
                patient.phone_number = form.phone_number.data
                patient.email = form.email.data
                patient.local_address = form.local_address.data
                patient.emergency_contact = form.emergency_contact.data
                patient.village = form.village.data
                patient.parish = form.parish.data
                patient.sub_county = form.sub_county.data
                patient.district = form.district.data

                db.session.commit()
                flash('Patient information updated successfully!', 'success')
            else:
                new_patient = Patient(
                    surname=form.surname.data,
                    given_name=form.given_name.data,
                    date_of_birth=form.date_of_birth.data,
                    gender=form.gender.data,
                    phone_number=form.phone_number.data,
                    email=form.email.data,
                    local_address=form.local_address.data,
                    emergency_contact=form.emergency_contact.data,
                    village=form.village.data,
                    parish=form.parish.data,
                    sub_county=form.sub_county.data,
                    district=form.district.data
                )
                db.session.add(new_patient)
                db.session.commit()
                flash('Patient created successfully!', 'success')

            return redirect(url_for('patient_information'))

        flash('Form validation failed, please check your inputs.', 'danger')
        patients = Patient.query.all()
        return render_template('patient_information.html', form=form, patients=patients)
    def delete(self, patient_id):
        patient = Patient.query.get(patient_id)
        if not patient:
            flash('Patient not found.', 'danger')
            return jsonify({'success': False}), 404

        db.session.delete(patient)
        db.session.commit()
        flash('Patient deleted successfully!', 'success')
        return jsonify({'success': True}), 200

class HealthRecordsView(MethodView):
    decorators = [login_required]

    def get(self):
        original_form = FileUploadForm()
        extracted_form = FileUploadForm()
        other_images_form = FileUploadForm()
        documents_form = FileUploadForm()

        original_files = FileRecord.query.filter_by(user_id=current_user.id, file_type='original').all()
        extracted_files = FileRecord.query.filter_by(user_id=current_user.id, file_type='extracted').all()
        other_images = FileRecord.query.filter_by(user_id=current_user.id, file_type='other_images').all()
        documents = FileRecord.query.filter_by(user_id=current_user.id, file_type='documents').all()

        return render_template(
            'health_records.html',
            original_form=original_form,
            extracted_form=extracted_form,
            other_images_form=other_images_form,
            documents_form=documents_form,
            original_files=original_files,
            extracted_files=extracted_files,
            other_images=other_images,
            documents=documents
        )

    def post(self):
        original_form = FileUploadForm()
        extracted_form = FileUploadForm()
        other_images_form = FileUploadForm()
        documents_form = FileUploadForm()

        forms = {
            'original': FileUploadForm(prefix='original'),
            'extracted': FileUploadForm(prefix='extracted'),
            'other_images': FileUploadForm(prefix='other_images'),
            'documents': FileUploadForm(prefix='documents')
        }

        for file_type, form in forms.items():
            if form.validate_on_submit() and form.file.data:
                self._save_and_record_file(form, file_type)

            if form.validate_on_submit() and form.file.data:
                file = form.file.data
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                new_file = FileRecord(filename=filename, file_type=file_type, user_id=current_user.id)
                db.session.add(new_file)
                db.session.commit()
                
                flash(f'{file_type.capitalize()} data uploaded successfully!', 'success')
                return redirect(url_for('health_records'))

        if original_form.validate_on_submit() and 'file' in request.files:
            file = request.files['file']
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_file = FileRecord(filename=filename, file_type='original', user_id=current_user.id)
                db.session.add(new_file)
                db.session.commit()
                flash('Original data uploaded successfully!', 'success')
                return redirect(url_for('health_records'))

        if extracted_form.validate_on_submit() and 'file' in request.files:
            file = request.files['file']
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_file = FileRecord(filename=filename, file_type='extracted', user_id=current_user.id)
                db.session.add(new_file)
                db.session.commit()
                flash('Extracted data uploaded successfully!', 'success')
                return redirect(url_for('health_records'))

        if other_images_form.validate_on_submit() and 'file' in request.files:
            file = request.files['file']
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_file = FileRecord(filename=filename, file_type='other_images', user_id=current_user.id)
                db.session.add(new_file)
                db.session.commit()
                flash('Other image uploaded successfully!', 'success')
                return redirect(url_for('health_records'))

        if documents_form.validate_on_submit() and 'file' in request.files:
            file = request.files['file']
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_file = FileRecord(filename=filename, file_type='documents', user_id=current_user.id)
                db.session.add(new_file)
                db.session.commit()
                flash('Document uploaded successfully!', 'success')
                return redirect(url_for('health_records'))

        flash('Form validation failed, please check your inputs.', 'danger')
        return redirect(url_for('health_records'))

    def _save_and_record_file(self, form, file_type):
        file = form.file.data
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(file_path)
            new_file = FileRecord(filename=filename, file_type=file_type, user_id=current_user.id)
            db.session.add(new_file)
            db.session.commit()
            flash(f'{file_type.capitalize()} data uploaded successfully!', 'success')
        except Exception as e:
            flash(f'Failed to save {file_type} data: {str(e)}', 'danger')
class AnalyticsReportsView(MethodView):
    decorators = [login_required]

    def get(self):
        return render_template('analytics_reports.html')

class ResearchCiteView(MethodView):
    decorators = [login_required]

    def get(self):
        return render_template('research_cite.html')

