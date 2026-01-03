import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

class FileService:
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileService.ALLOWED_EXTENSIONS
    
    @staticmethod
    def save_image(file, folder='uploads'):
        """
        Save uploaded image with a unique filename
        Args:
            file: FileStorage object from request.files
            folder: subfolder name (e.g., 'users', 'products')
        Returns:
            filename: The saved filename or None if failed
        """
        if not file or file.filename == '':
            return None
            
        if not FileService.allowed_file(file.filename):
            raise ValueError("Invalid file type. Allowed: png, jpg, jpeg, gif, webp")
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer
        
        if file_size > FileService.MAX_FILE_SIZE:
            raise ValueError("File too large. Maximum size: 5MB")
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{extension}"
        
        # Create upload directory if it doesn't exist
        upload_path = os.path.join(current_app.root_path, 'static', folder)
        os.makedirs(upload_path, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        
        return unique_filename
    
    @staticmethod
    def delete_image(filename, folder='uploads'):
        """Delete an image file"""
        if not filename:
            return
            
        file_path = os.path.join(current_app.root_path, 'static', folder, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
    
    @staticmethod
    def get_image_url(filename, folder='uploads'):
        """Generate URL for accessing the image"""
        if not filename:
            return None
        return f"/static/{folder}/{filename}"