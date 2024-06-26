import os
from flask import (
    Flask,
    render_template, 
    request, 
    flash,
    redirect,
    url_for,
    jsonify
)
from flask.views import MethodView
from werkzeug.utils import secure_filename
from .forms import (
    UploadForm, 
    ImageForm, 
    UserCreationForm, 
    LoginForm, 
    ImageCaptureForm
)
from text_extractor import app, db
from .models import User, Image
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
    
# Logout class-based view
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
        #image_files = os.listdir(app.config['UPLOAD_FOLDER'])
        form = ImageForm()
        if current_user.is_authenticated:
            # Retrieve images for the current user only
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
                 # Format the extracted text for each segment
                segment_text = segment['text']
                wrapped_text = textwrap.wrap(segment_text, width=70)  # Adjust line width as needed

                # Add a header for each segment
                formatted_segment_text = f"Segment {i} - Handwritten Text:\n"

                # Indent the text within the segment
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
            # Process the uploaded image data
            image_data = request.form.get('image_data')

            if image_data:
                # Generate a unique identifier
                unique_identifier = str(uuid.uuid4())

                # Get the file extension (assuming it's a JPEG image)
                file_extension = '.jpg'

                # Create a unique filename by combining the identifier and extension
                filename = f"{unique_identifier}{file_extension}"

                # Save the image data to a file with the unique filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                # Decode and save the base64-encoded image data to the file
                with open(file_path, 'wb') as image_file:
                    image_data_bytes = base64.b64decode(image_data.split(',')[1])
                    image_file.write(image_data_bytes)

                # You can perform further processing or database operations here
                # For example, you can save the file path or image metadata in your database
                new_image = Image(filename=filename, user=current_user)
                db.session.add(new_image)
                db.session.commit()

                flash('Image captured and processed successfully!', 'success')
                return redirect(url_for('capture_image'))  # Replace with your desired route
        else:
            flash('Invalid form submission', 'danger')

        # If form submission fails, return to the capture page with the form
        return render_template('capture.html', form=form)


class DeleteImageView(MethodView):
    decorators = [login_required]
    
    def get(self, image_id):
        image = Image.query.get(image_id)

        if image and image.user_id == current_user.id:
            try:
                # Delete image file from the system
                delete_image_file(image.filename)

                # Delete image from the database
                db.session.delete(image)
                db.session.commit()

                flash("Image deleted successfully.", "success")

            except Exception as e:
                flash("An error occured while deleteting the image", "danger")
        
        return redirect(url_for('index'))


    


