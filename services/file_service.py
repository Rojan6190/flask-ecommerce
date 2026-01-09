import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

class FileService:
    """
    Low-level file handling service for image uploads.
    Handles validation, storage, and deletion of image files.
    """
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    @staticmethod
    def allowed_file(filename):
        """
        Check if file extension is allowed
        Args:
            filename: Name of the uploaded file
        Returns:
            bool: True if extension is allowed, False otherwise
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileService.ALLOWED_EXTENSIONS
    
    @staticmethod
    def save_image(file, folder='uploads'):
        """
        Save uploaded image with a unique filename
        
        Args:
            file: FileStorage object from request.files
            folder: Subfolder name (e.g., 'users', 'products')
            
        Returns:
            str: The saved filename (UUID-based)
            
        Raises:
            ValueError: If file type is invalid or file is too large
        """
        if not file or file.filename == '':
            raise ValueError("No file provided")
            
        if not FileService.allowed_file(file.filename):
            raise ValueError("Invalid file type. Allowed: png, jpg, jpeg, gif, webp")
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer
        
        if file_size > FileService.MAX_FILE_SIZE:
            raise ValueError("File too large. Maximum size: 5MB")
        
        # Generate unique filename to prevent collisions
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
        """
        Delete an image file from storage
        
        Args:
            filename: Name of the file to delete
            folder: Subfolder where the file is stored
            
        Returns:
            bool: True if file was deleted, False if file didn't exist
        """
        if not filename:
            return False
            
        file_path = os.path.join(current_app.root_path, 'static', folder, filename)
        
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except OSError as e:
                # Log error in production
                print(f"Error deleting file {filename}: {e}")
                return False
        return False
    
    @staticmethod
    def get_image_url(filename, folder='uploads'):
        """
        Generate URL for accessing the image
        
        Args:
            filename: Name of the image file
            folder: Subfolder where the file is stored
            
        Returns:
            str: URL path to access the image, or None if no filename
        """
        if not filename:
            return None
        return f"/static/{folder}/{filename}"
    
    @staticmethod
    def file_exists(filename, folder='uploads'):
        """
        Check if a file exists in storage
        
        Args:
            filename: Name of the file
            folder: Subfolder to check
            
        Returns:
            bool: True if file exists, False otherwise
        """
        if not filename:
            return False
        file_path = os.path.join(current_app.root_path, 'static', folder, filename)
        return os.path.exists(file_path)