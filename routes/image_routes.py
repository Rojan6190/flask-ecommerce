from flask import Blueprint, request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.file_service import FileService
from models import db, User, Product
from schemas import user_schema, product_schema

image_bp = Blueprint('images', __name__)

class UserImageUploadAPI(MethodView):
    decorators = [jwt_required()]
    
    def get(self):
        """Get current user's profile information including image URL"""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        return jsonify(user_schema.dump(user)), 200
    
    def post(self):
        """Upload or update user profile image"""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        
        try:
            if user.profile_image:
                FileService.delete_image(user.profile_image, 'users')
            
            filename = FileService.save_image(file, 'users')
            user.profile_image = filename
            db.session.commit()
            
            return jsonify({
                "message": "Profile image uploaded successfully",
                "user": user_schema.dump(user)
            }), 200
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Failed to upload image"}), 500
    
    def delete(self):
        """Delete user profile image"""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        
        if not user.profile_image:
            return jsonify({"error": "No profile image to delete"}), 404
        
        try:
            FileService.delete_image(user.profile_image, 'users')
            user.profile_image = None
            db.session.commit()
            return jsonify({"message": "Profile image deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Failed to delete image"}), 500

class ProductImageUploadAPI(MethodView):
    # GET is public - anyone can view product details
    def get(self, product_id):
        """Get product details including image URL"""
        product = Product.query.get_or_404(product_id)
        return jsonify(product_schema.dump(product)), 200
    
    @jwt_required()  # Only authenticated users can upload
    def post(self, product_id):
        """Upload or update product image"""
        product = Product.query.get_or_404(product_id)
        
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        
        try:
            if product.image:
                FileService.delete_image(product.image, 'products')
            
            filename = FileService.save_image(file, 'products')
            product.image = filename
            db.session.commit()
            
            return jsonify({
                "message": "Product image uploaded successfully",
                "product": product_schema.dump(product)
            }), 200
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Failed to upload image"}), 500
    
    @jwt_required()  # Only authenticated users can delete
    def delete(self, product_id):
        """Delete product image"""
        product = Product.query.get_or_404(product_id)
        
        if not product.image:
            return jsonify({"error": "No product image to delete"}), 404
        
        try:
            FileService.delete_image(product.image, 'products')
            product.image = None
            db.session.commit()
            return jsonify({"message": "Product image deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Failed to delete image"}), 500

image_bp.add_url_rule('/user/profile-image', view_func=UserImageUploadAPI.as_view('user_image_api'))
image_bp.add_url_rule('/products/<int:product_id>/image', view_func=ProductImageUploadAPI.as_view('product_image_api'))

