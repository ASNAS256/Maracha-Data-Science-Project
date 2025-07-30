import os
# Read the secret key from a file
with open('text_extractor/secret.key', 'r') as f:
    secret_key = f.read().strip()

class Config:
    # Define the upload folder path
    UPLOAD_FOLDER = os.path.join('text_extractor', 'static', 'uploads')
    
    # Define allowed file extensions for images and common document formats
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'wps', "txt"}
    
    # Secret key for session management
    SECRET_KEY = secret_key
