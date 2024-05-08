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
)
from flask_wtf.csrf import CSRFProtect
from text_extractor.models import User
from flask import render_template, redirect, url_for, flash
from text_extractor.forms import UserCreationForm  # Import the UserCreationForm

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

if __name__ == '__main__':
    with app.app_context():
        app.config.from_object(Config)
        db.create_all()
    app.run(debug=True)
