import os
from flask import abort
from flask import send_file
from flask import send_from_directory, current_app, send_from_directory, flash, redirect, url_for
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
    FileUploadForm,
    LaboratoryRequestForm,
    InpatientTreatmentSheetForm,
    OperationReportForm,
    ReferralNoteForm
)
from .config import Config
from text_extractor import app, db
from .models import (
    User, 
    Image, 
    Patient, 
    FileRecord, 
    InpatientTreatmentSheet,
    OperationReport,
    ReferralNote,
    LaboratoryRequest as LaboratoryRequestFormModel
    )
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
from datetime import datetime, time

from text_extractor.advanced_ocr import AdvancedOCR
from text_extractor.models import ExtractedTextRecord
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
                return redirect(url_for('dashboard'))

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

class DashboardView(MethodView):
    def get(self):
        return render_template('dashboard.html')
    

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
            'idashboard.html',
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

                formatted_segment_text = f"\n"
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

from flask import render_template, request
from flask.views import MethodView
from flask_login import current_user
import os
from text_extractor.advanced_ocr import AdvancedOCR  # Adjust based on your actual file structure
from text_extractor.models import ExtractedTextRecord, db

class AdvancedOCRView(MethodView):
    def get(self):
        return render_template('advanced_ocr.html')

    def post(self):
        file = request.files.get('image')
        if file:
            file_path = os.path.join('text_extractor/static/uploads', file.filename)
            file.save(file_path)
            ocr = AdvancedOCR()
            extracted_text = ocr.extract_text(file_path)

            # Store result in the database (optional)
            record = ExtractedTextRecord(
                filename=file.filename,
                extracted_text=extracted_text,
                user_id=current_user.id
            )
            db.session.add(record)
            db.session.commit()

            return render_template('advanced_ocr.html', extracted_text=extracted_text, image=file.filename)
        return render_template('advanced_ocr.html', error='No file uploaded')
    
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
        search_query = request.args.get('search_query', '')
        sort_by = request.args.get('sort_by', 'upload_date')
        sort_order = request.args.get('sort_order', 'desc')
        ward = request.args.get('ward', 'all')

        original_form = FileUploadForm(prefix='original')
        extracted_form = FileUploadForm(prefix='extracted')
        other_images_form = FileUploadForm(prefix='other_images')
        documents_form = FileUploadForm(prefix='documents')

        sort_criteria = getattr(FileRecord, sort_by)
        if sort_order == 'desc':
            sort_criteria = sort_criteria.desc()
        else:
            sort_criteria = sort_criteria.asc()

        search_filter = FileRecord.filename.ilike(f'%{search_query}%') | FileRecord.upload_date.ilike(f'%{search_query}%')
        ward_filter = True if ward == 'all' else (FileRecord.ward == ward)

        original_files = FileRecord.query.filter_by(user_id=current_user.id, file_type='original').filter(search_filter).filter(ward_filter).order_by(sort_criteria).all()
        extracted_files = FileRecord.query.filter_by(user_id=current_user.id, file_type='extracted').filter(search_filter).filter(ward_filter).order_by(sort_criteria).all()
        other_images = FileRecord.query.filter_by(user_id=current_user.id, file_type='other_images').filter(search_filter).filter(ward_filter).order_by(sort_criteria).all()
        documents = FileRecord.query.filter_by(user_id=current_user.id, file_type='documents').filter(search_filter).filter(ward_filter).order_by(sort_criteria).all()

        return render_template(
            'health_records.html',
            original_form=original_form,
            extracted_form=extracted_form,
            other_images_form=other_images_form,
            documents_form=documents_form,
            original_files=original_files,
            extracted_files=extracted_files,
            other_images=other_images,
            documents=documents,
            search_query=search_query,
            sort_by=sort_by,
            sort_order=sort_order,
            ward=ward
        )

    def post(self):
        forms = {
            'original': FileUploadForm(prefix='original'),
            'extracted': FileUploadForm(prefix='extracted'),
            'other_images': FileUploadForm(prefix='other_images'),
            'documents': FileUploadForm(prefix='documents')
        }

        for file_type, form in forms.items():
            if form.validate_on_submit() and form.file.data:
                ward = form.ward.data
                files = request.files.getlist(form.file.name)
                for file in files:
                    self._save_and_record_file(file, file_type, ward)
                return redirect(url_for('health_records'))

        flash('Form validation failed, please check your inputs.', 'danger')
        return redirect(url_for('health_records'))

    def _save_and_record_file(self, file, file_type, ward):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(file_path)
            new_file = FileRecord(filename=filename, file_type=file_type, ward=ward, user_id=current_user.id, upload_date=datetime.utcnow())
            db.session.add(new_file)
            db.session.commit()
            flash(f'{file_type.capitalize()} data uploaded successfully to {ward} ward!', 'success')
        except Exception as e:
            flash(f'Failed to save {file_type} data: {str(e)}', 'danger')

    @app.route('/delete_file/<filename>', methods=['POST'])
    @login_required
    def delete_file(filename):
        file_record = FileRecord.query.filter_by(user_id=current_user.id, filename=filename).first()
        if file_record:
            try:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                db.session.delete(file_record)
                db.session.commit()
                return jsonify({'success': True, 'message': f'File {filename} deleted successfully.'}), 200
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error deleting file {filename}: {str(e)}'}), 500
        else:
            return jsonify({'success': False, 'message': f'File {filename} not found.'}), 404

    @app.route('/download_file/<filename>', methods=['GET'])
    @login_required
    def download_file(filename):
        file_record = FileRecord.query.filter_by(user_id=current_user.id, filename=filename).first()
        if file_record:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            print(f"Trying to download file from: {file_path}")  # Debugging line
            if os.path.exists(file_path):
                try:
                    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
                except Exception as e:
                    flash(f'Failed to download file: {str(e)}', 'danger')
                    return redirect(url_for('health_records'))
            else:
                flash(f'File {filename} does not exist at the path {file_path}.', 'danger')
                return redirect(url_for('health_records'))
        else:
            flash(f'File {filename} not found in the database.', 'danger')
            return redirect(url_for('health_records'))
    
    
class AnalyticsReportsView(MethodView):
    decorators = [login_required]

    def get(self):
        return render_template('analytics_reports.html')

class HospitalFormsView(MethodView):
    decorators = [login_required]

    def get(self):
        # Assuming you have a template named 'hospital_forms.html'
        # that displays the available forms at the hospital.
        return render_template('hospital_forms.html')

class InpatientTreatmentSheetView(MethodView):
    decorators = [login_required]

    def get(self):
        form = InpatientTreatmentSheetForm()
        sheets = InpatientTreatmentSheet.query.all()
        return render_template('inpatient_treatment_sheet.html', form=form, sheets=sheets)

    def post(self):
        form = InpatientTreatmentSheetForm()
        if form.validate_on_submit():
            sheet = InpatientTreatmentSheet(
                ward=form.ward.data,
                bed_number=form.bed_number.data,
                name=form.name.data,
                inpatient_number=form.inpatient_number.data,
                address=form.address.data,
                age=form.age.data,
                sex=form.sex.data,
                next_of_kin=form.next_of_kin.data,
                admission_date=form.admission_date.data,
                admission_time=form.admission_time.data,
                referred_from=form.referred_from.data,
                discharge_date=form.discharge_date.data,
                discharge_status=form.discharge_status.data,
                final_diagnosis=form.final_diagnosis.data,
                surgical_procedure=form.surgical_procedure.data,
                follow_up_date=form.follow_up_date.data,
                follow_up_place=form.follow_up_place.data,
                treatment_instructions=form.treatment_instructions.data,
                clinical_notes=form.clinical_notes.data,
                provisional_diagnosis=form.provisional_diagnosis.data,
            )
            db.session.add(sheet)
            db.session.commit()
            flash('Inpatient Treatment Sheet submitted successfully', 'success')
            return redirect(url_for('inpatient_treatment_sheet'))
        sheets = InpatientTreatmentSheet.query.all()
        return render_template('inpatient_treatment_sheet.html', form=form, sheets=sheets)

@app.route('/inpatient_treatment_sheet/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def inpatient_treatment_sheet_edit(id):
    sheet = InpatientTreatmentSheet.query.get_or_404(id)
    form = InpatientTreatmentSheetForm(obj=sheet)
    if request.method == 'POST' and form.validate_on_submit():
        sheet.ward = form.ward.data
        sheet.bed_number = form.bed_number.data
        sheet.name = form.name.data
        sheet.inpatient_number = form.inpatient_number.data
        sheet.address = form.address.data
        sheet.age = form.age.data
        sheet.sex = form.sex.data
        sheet.next_of_kin = form.next_of_kin.data
        sheet.admission_date = form.admission_date.data
        sheet.admission_time = form.admission_time.data
        sheet.referred_from = form.referred_from.data
        sheet.discharge_date = form.discharge_date.data
        sheet.discharge_status = form.discharge_status.data
        sheet.final_diagnosis = form.final_diagnosis.data
        sheet.surgical_procedure = form.surgical_procedure.data
        sheet.follow_up_date = form.follow_up_date.data
        sheet.follow_up_place = form.follow_up_place.data
        sheet.treatment_instructions = form.treatment_instructions.data
        sheet.clinical_notes = form.clinical_notes.data
        sheet.provisional_diagnosis = form.provisional_diagnosis.data

        db.session.commit()
        flash('Inpatient Treatment Sheet updated successfully', 'success')
        return redirect(url_for('inpatient_treatment_sheet'))
    return render_template('inpatient_treatment_sheet.html', form=form, sheet=sheet)

@app.route('/inpatient_treatment_sheet/delete/<int:id>', methods=['POST'])
@login_required
def inpatient_treatment_sheet_delete(id):
    sheet = InpatientTreatmentSheet.query.get_or_404(id)
    db.session.delete(sheet)
    db.session.commit()
    flash('Inpatient Treatment Sheet deleted successfully', 'success')
    return redirect(url_for('inpatient_treatment_sheet'))

@app.route('/inpatient_treatment_sheet/print/<int:id>', methods=['GET'])
@login_required
def print_inpatient_treatment_sheet(id):
    sheet = InpatientTreatmentSheet.query.get_or_404(id)
    return render_template('inpatient_treatment_sheet_print.html', sheet=sheet)


class LaboratoryRequestFormView(MethodView):
    decorators = [login_required]

    def get(self, id=None):
        form = LaboratoryRequestForm()
        if id:
            lab_request = LaboratoryRequestFormModel.query.get_or_404(id)
            form = LaboratoryRequestForm(obj=lab_request)
        lab_requests = LaboratoryRequestFormModel.query.all()
        return render_template('laboratory_request_form.html', form=form, lab_requests=lab_requests)

    def post(self):
        form = LaboratoryRequestForm()
        if form.validate_on_submit():
            try:
                time_obj = datetime.strptime(form.time.data, "%H:%M").time()
                rec_in_lab_time_obj = datetime.strptime(form.rec_in_lab_time.data, "%H:%M").time()
                date_obj = datetime.strptime(form.date.data, "%d/%m/%Y").date()
            except ValueError as e:
                flash('Invalid time or date format. Please use HH:MM format for time and DD/MM/YYYY format for date.', 'danger')
                return render_template('laboratory_request_form.html', form=form)
            
            new_request = LaboratoryRequestFormModel(
                name=form.name.data,
                sex=form.sex.data,
                age=form.age.data,
                ward=form.ward.data,
                material=form.material.data,
                time=time_obj,
                date=date_obj,
                ip_no=form.ip_no.data,
                examination_required=form.examination_required.data,
                clinical_notes=form.clinical_notes.data,
                rec_in_lab_time=rec_in_lab_time_obj,
                lab_no=form.lab_no.data,
                results=form.results.data,
                rec_by=form.rec_by.data,
                examined_by=form.examined_by.data
            )
            db.session.add(new_request)
            db.session.commit()
            flash('Laboratory request submitted successfully.', 'success')
            return redirect(url_for('laboratory_request_form'))
        
        lab_requests = LaboratoryRequestFormModel.query.all()
        return render_template('laboratory_request_form.html', form=form, lab_requests=lab_requests)

    def put(self, id):
        form = LaboratoryRequestForm()
        lab_request = LaboratoryRequestFormModel.query.get_or_404(id)
        if form.validate_on_submit():
            try:
                time_obj = datetime.strptime(form.time.data, "%H:%M").time()
                rec_in_lab_time_obj = datetime.strptime(form.rec_in_lab_time.data, "%H:%M").time()
                date_obj = datetime.strptime(form.date.data, "%d/%m/%Y").date()
            except ValueError as e:
                flash('Invalid time or date format. Please use HH:MM format for time and DD/MM/YYYY format for date.', 'danger')
                return render_template('laboratory_request_form.html', form=form)
            
            lab_request.name = form.name.data
            lab_request.sex = form.sex.data
            lab_request.age = form.age.data
            lab_request.ward = form.ward.data
            lab_request.material = form.material.data
            lab_request.time = time_obj
            lab_request.date = date_obj
            lab_request.ip_no = form.ip_no.data
            lab_request.examination_required = form.examination_required.data
            lab_request.clinical_notes = form.clinical_notes.data
            lab_request.rec_in_lab_time = rec_in_lab_time_obj
            lab_request.lab_no = form.lab_no.data
            lab_request.results = form.results.data
            lab_request.rec_by = form.rec_by.data
            lab_request.examined_by = form.examined_by.data
            
            db.session.commit()
            flash('Laboratory request updated successfully.', 'success')
            return redirect(url_for('laboratory_request_form'))
        
        lab_requests = LaboratoryRequestFormModel.query.all()
        return render_template('laboratory_request_form.html', form=form, lab_requests=lab_requests)

    def delete(self, id):
        lab_request = LaboratoryRequestFormModel.query.get_or_404(id)
        db.session.delete(lab_request)
        db.session.commit()
        flash('Laboratory request deleted successfully.', 'success')
        return redirect(url_for('laboratory_request_form'))


class OperationReportView(MethodView):
    decorators = [login_required]

    def get(self, report_id=None, action=None):
        form = OperationReportForm()
        if report_id and action == 'edit':
            return self.edit_get(report_id)
        elif report_id and action == 'print':
            return self.print_get(report_id)
        elif report_id:
            report = OperationReport.query.get_or_404(report_id)
            return render_template('operation_report_detail.html', report=report)
        else:
            if action == 'create':
                return render_template('operation_report.html', form=form)
            reports = OperationReport.query.all()
            return render_template('operation_reports.html', reports=reports)

    def post(self, report_id=None, action=None):
        form = OperationReportForm()
        if form.validate_on_submit():
            if report_id:
                report = OperationReport.query.get_or_404(report_id)
                form.populate_obj(report)
            else:
                report = OperationReport()
                form.populate_obj(report)
                db.session.add(report)
            db.session.commit()
            return redirect(url_for('operation_report_view'))
        return render_template('operation_report.html', form=form)

    def delete(self, report_id):
        report = OperationReport.query.get_or_404(report_id)
        db.session.delete(report)
        db.session.commit()
        return redirect(url_for('operation_report_view'))

    def edit_get(self, report_id):
        report = OperationReport.query.get_or_404(report_id)
        form = OperationReportForm(obj=report)
        return render_template('operation_report.html', form=form, report=report)

    def print_get(self, report_id):
        report = OperationReport.query.get_or_404(report_id)
        return render_template('operation_report_print.html', report=report)


        
class ReferralNoteView(MethodView):
    decorators = [login_required]

    def get(self, report_id=None, action=None):
        form = ReferralNoteForm()
        if report_id and action == 'edit':
            return self.edit_get(report_id)
        elif report_id and action == 'print':
            return self.print_get(report_id)
        elif report_id:
            report = ReferralNote.query.get_or_404(report_id)
            return render_template('referral_note_detail.html', report=report)
        else:
            if action == 'create':
                return render_template('referral_note.html', form=form)
            reports = ReferralNote.query.all()
            return render_template('referral_notes.html', reports=reports)

    def post(self, report_id=None, action=None):
        form = ReferralNoteForm()
        if form.validate_on_submit():
            if report_id:
                report = ReferralNote.query.get_or_404(report_id)
                form.populate_obj(report)
            else:
                report = ReferralNote()
                form.populate_obj(report)
                db.session.add(report)
            db.session.commit()
            return redirect(url_for('referral_note_view'))
        return render_template('referral_note.html', form=form)

    def delete(self, report_id):
        report = ReferralNote.query.get_or_404(report_id)
        db.session.delete(report)
        db.session.commit()
        return redirect(url_for('referral_note_view'))

    def edit_get(self, report_id):
        report = ReferralNote.query.get_or_404(report_id)
        form = ReferralNoteForm(obj=report)
        return render_template('referral_note.html', form=form, report=report)

    def print_get(self, report_id):
        report = ReferralNote.query.get_or_404(report_id)
        return render_template('referral_note_print.html', report=report)