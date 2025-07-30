import os
from flask import render_template, redirect, url_for, flash, send_from_directory, make_response
from text_extractor import app, login_manager, db
from flask import send_from_directory, make_response
from text_extractor.config import Config
from text_extractor.routes import AdvancedOCRView
from text_extractor.routes import (
    ImageViewerView, 
    GalleryView, 
    LoginView,
    LogoutView, DashboardView,
    CaptureImageView,
    DeleteImageView,
    UserCreationView,
    EHRView,  
    PatientInformationView,
    HealthRecordsView,
    AnalyticsReportsView,
    HospitalFormsView,
    InpatientTreatmentSheetView, LaboratoryRequestFormView, OperationReportView, ReferralNoteView
)
from text_extractor.forms import UserCreationForm
from flask_wtf.csrf import CSRFProtect
from text_extractor.models import User
from datetime import datetime, time

operation_report_view = OperationReportView.as_view('operation_report_view')
inpatient_treatment_sheet_view = InpatientTreatmentSheetView.as_view('inpatient_treatment_sheet')
referral_note_view = ReferralNoteView.as_view('referral_note_view')

with open('text_extractor/secret.key', 'r') as f:
    app.secret_key = f.read().strip()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Register routes
app.add_url_rule('/login', view_func=LoginView.as_view('login'))
app.add_url_rule('/index', view_func=ImageViewerView.as_view('index'))  
app.add_url_rule('/gallery', view_func=GalleryView.as_view('gallery'))
app.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))
app.add_url_rule('/dashboard', view_func=DashboardView.as_view('dashboard'))
app.add_url_rule('/capture_image', view_func=CaptureImageView.as_view('capture_image'))
app.add_url_rule('/delete_image/<int:image_id>', view_func=DeleteImageView.as_view('delete_image'))
app.add_url_rule('/ehr', view_func=EHRView.as_view('ehr'))
app.add_url_rule('/patient_information', view_func=PatientInformationView.as_view('patient_information'), methods=['GET', 'POST'])
app.add_url_rule('/patient_information/<int:patient_id>', view_func=PatientInformationView.as_view('patient_information_edit'), methods=['GET', 'POST'])
app.add_url_rule('/patient_information/delete/<int:patient_id>', view_func=PatientInformationView.as_view('patient_information_delete'), methods=['DELETE'])
app.add_url_rule('/health_records', view_func=HealthRecordsView.as_view('health_records'))
app.add_url_rule('/analytics_reports', view_func=AnalyticsReportsView.as_view('analytics_reports'))
app.add_url_rule('/hospital_forms', view_func=HospitalFormsView.as_view('hospital_forms'))
app.add_url_rule('/inpatient_treatment_sheet', view_func=inpatient_treatment_sheet_view, methods=['GET', 'POST'])
app.add_url_rule('/laboratory_request_form', view_func=LaboratoryRequestFormView.as_view('laboratory_request_form'), methods=['GET', 'POST'])
app.add_url_rule('/laboratory_request_form/<int:id>', view_func=LaboratoryRequestFormView.as_view('laboratory_request_form_detail'), methods=['GET', 'POST', 'PUT'])
app.add_url_rule('/laboratory_request_form/delete/<int:id>', view_func=LaboratoryRequestFormView.as_view('laboratory_request_form_delete'), methods=['POST', 'DELETE'])
app.add_url_rule('/referral_note', view_func=ReferralNoteView.as_view('referral_note'))
app.add_url_rule('/operation_report/', defaults={'report_id': None, 'action': None}, view_func=operation_report_view, methods=['GET', 'POST'])
app.add_url_rule('/operation_report/<int:report_id>', defaults={'action': None}, view_func=operation_report_view, methods=['GET', 'POST', 'DELETE'])
app.add_url_rule('/operation_report/<int:report_id>/<string:action>', view_func=operation_report_view, methods=['GET'])
app.add_url_rule('/operation_report/new', defaults={'report_id': None, 'action': 'create'}, view_func=operation_report_view, methods=['GET', 'POST'])
app.add_url_rule('/referral_note/', defaults={'report_id': None, 'action': None}, view_func=referral_note_view, methods=['GET', 'POST'])
app.add_url_rule('/referral_note/<int:report_id>', defaults={'action': None}, view_func=referral_note_view, methods=['GET', 'POST', 'DELETE'])
app.add_url_rule('/referral_note/<int:report_id>/<string:action>', view_func=referral_note_view, methods=['GET'])
app.add_url_rule('/referral_note/new', defaults={'report_id': None, 'action': 'create'}, view_func=referral_note_view, methods=['GET', 'POST'])
app.add_url_rule('/advanced_ocr', view_func=AdvancedOCRView.as_view('advanced_ocr'), methods=['GET', 'POST'])

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    form = UserCreationForm()
    if form.validate_on_submit():
        user = User(
            employee_id=form.employee_id.data,
            email=form.email.data,
            job_title=form.job_title.data,
            department=form.department.data,
            username=form.username.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('create_user.html', title='Create User', form=form)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    upload_folder = os.path.join(app.root_path, 'static/uploads')
    file_path = os.path.join(upload_folder, filename)

    if not os.path.exists(file_path):
        app.logger.error(f"File not found: {file_path}")
        return "File not found", 404
    else:
        app.logger.info(f"Serving file: {file_path}")

    file_extension = os.path.splitext(filename)[1].lower()
    mimetype = 'application/octet-stream'  # Default MIME type

    if file_extension == '.pdf':
        mimetype = 'application/pdf'
    elif file_extension == '.doc':
        mimetype = 'application/msword'
    elif file_extension == '.docx':
        mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif file_extension == '.ppt':
        mimetype = 'application/vnd.ms-powerpoint'
    elif file_extension == '.pptx':
        mimetype = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    elif file_extension == '.xls':
        mimetype = 'application/vnd.ms-excel'
    elif file_extension == '.xlsx':
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif file_extension == '.txt':
        mimetype = 'text/plain'
    elif file_extension in ['.jpg', '.jpeg']:
        mimetype = 'image/jpeg'
    elif file_extension == '.png':
        mimetype = 'image/png'
    elif file_extension == '.gif':
        mimetype = 'image/gif'

    response = make_response(send_from_directory(upload_folder, filename, mimetype=mimetype))
    response.headers['Content-Disposition'] = f'inline; filename="{filename}"'
    return response

@app.route('/print/<filename>')
def print_file(filename):
    file_url = url_for('uploaded_file', filename=filename)
    return render_template('print.html', file_url=file_url)

if __name__ == '__main__':
    with app.app_context():
        app.config.from_object(Config)
        db.create_all()
    app.run(debug=True)
