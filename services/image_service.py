from services.file_service import FileService
from models import db

class ImageService:
    """Handles all image-related business logic"""
    
    @staticmethod
    def upload_image(entity, file, folder):
        """
        Upload image for any entity (User or Product)
        Args:
            entity: Database model instance
            file: Uploaded file
            folder: Storage folder name
        Returns:
            Updated entity
        Raises:
            ValueError: If file validation fails
        """
        # Determine image field name
        image_field = 'profile_image' if hasattr(entity, 'profile_image') else 'image'
        
        # Delete old image if exists
        old_image = getattr(entity, image_field)
        if old_image:
            FileService.delete_image(old_image, folder)
        
        # Save new image
        filename = FileService.save_image(file, folder)
        setattr(entity, image_field, filename)
        db.session.commit()
        
        return entity
    
    @staticmethod
    def delete_image(entity, folder):
        """
        Delete image for any entity
        Args:
            entity: Database model instance
            folder: Storage folder name
        Returns:
            Updated entity
        Raises:
            ValueError: If no image exists
        """
        image_field = 'profile_image' if hasattr(entity, 'profile_image') else 'image'
        current_image = getattr(entity, image_field)
        
        if not current_image:
            raise ValueError("No image to delete")
        
        FileService.delete_image(current_image, folder)
        setattr(entity, image_field, None)
        db.session.commit()
        
        return entity