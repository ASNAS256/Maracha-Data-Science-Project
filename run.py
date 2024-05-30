from text_extractor import app, login_manager, db
from text_extractor.config import Config
from text_extractor.routes import (
    ImageViewerView, 
    GalleryView, 
    LoginView,
    LogoutView,
    CaptureImageView,
    DeleteImageView,
    UserCreationView,
    EHRView,  
    PatientInformationView,
    HealthRecordsView,
    AnalyticsReportsView,
    ResearchCiteView
)
from flask_wtf.csrf import CSRFProtect
from text_extractor.models import User
from flask import render_template, redirect, url_for, flash, send_from_directory

with open('text_extractor/secret.key', 'r') as f:
    app.secret_key = f.read().strip()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

csrf = CSRFProtect(app)

# Register routes
app.add_url_rule('/login', view_func=LoginView.as_view('login'))
app.add_url_rule('/index', view_func=ImageViewerView.as_view('index'))  
app.add_url_rule('/gallery', view_func=GalleryView.as_view('gallery'))
app.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))
app.add_url_rule('/capture_image', view_func=CaptureImageView.as_view('capture_image'))
app.add_url_rule('/delete_image/<int:image_id>', view_func=DeleteImageView.as_view('delete_image'))
app.add_url_rule('/ehr', view_func=EHRView.as_view('ehr'))
app.add_url_rule('/patient_information', view_func=PatientInformationView.as_view('patient_information'), methods=['GET', 'POST'])
app.add_url_rule('/patient_information/<int:patient_id>', view_func=PatientInformationView.as_view('patient_information_edit'), methods=['GET', 'POST'])
app.add_url_rule('/patient_information/delete/<int:patient_id>', view_func=PatientInformationView.as_view('patient_information_delete'), methods=['DELETE'])
app.add_url_rule('/health_records', view_func=HealthRecordsView.as_view('health_records'))
app.add_url_rule('/analytics_reports', view_func=AnalyticsReportsView.as_view('analytics_reports'))
app.add_url_rule('/research_cite', view_func=ResearchCiteView.as_view('research_cite'))

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    form = UserCreationForm()
    if form.validate_on_submit():
        # Create the user with the form data
        user = User(
            employee_id=form.employee_id.data,
            email=form.email.data,
            job_title=form.job_title.data,
            department=form.department.data,
            username=form.username.data
        )
        user.set_password(form.password.data)  # Hash the password
        db.session.add(user)
        db.session.commit()
        flash('User created successfully!', 'success')
        return redirect(url_for('login'))  # Redirect to the login page after successful user creation
    return render_template('create_user.html', title='Create User', form=form)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/print/<filename>')
def print_file(filename):
    file_url = url_for('uploaded_file', filename=filename)
    return render_template('print.html', file_url=file_url)

if __name__ == '__main__':
    with app.app_context():
        app.config.from_object(Config)
        db.create_all()
    app.run(debug=True)
