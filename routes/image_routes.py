from flask import Blueprint, request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.image_service import ImageService
from models import User, Product
from schemas import user_schema, product_schema

image_bp = Blueprint('images', __name__)


class UserImageUploadAPI(MethodView):
    decorators = [jwt_required()]
    
    def get(self):
        """Get current user's profile"""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        return jsonify(user_schema.dump(user)), 200
    
    def post(self):
        """Upload user profile image"""
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        
        try:
            user = ImageService.upload_image(user, request.files['image'], 'users')
            return jsonify({
                "message": "Profile image uploaded successfully",
                "user": user_schema.dump(user)
            }), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception:
            return jsonify({"error": "Failed to upload image"}), 500
    
    def delete(self):
        """Delete user profile image"""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        
        try:
            user = ImageService.delete_image(user, 'users')
            return jsonify({"message": "Profile image deleted successfully"}), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        except Exception:
            return jsonify({"error": "Failed to delete image"}), 500


class ProductImageUploadAPI(MethodView):
    
    def get(self, product_id):
        """Get product details (Public)"""
        product = Product.query.get_or_404(product_id)
        return jsonify(product_schema.dump(product)), 200
    
    @jwt_required()
    def post(self, product_id):
        """Upload product image (Authenticated)"""
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        product = Product.query.get_or_404(product_id)
        
        try:
            product = ImageService.upload_image(product, request.files['image'], 'products')
            return jsonify({
                "message": "Product image uploaded successfully",
                "product": product_schema.dump(product)
            }), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception:
            return jsonify({"error": "Failed to upload image"}), 500
    
    @jwt_required()
    def delete(self, product_id):
        """Delete product image (Authenticated)"""
        product = Product.query.get_or_404(product_id)
        
        try:
            product = ImageService.delete_image(product, 'products')
            return jsonify({"message": "Product image deleted successfully"}), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        except Exception:
            return jsonify({"error": "Failed to delete image"}), 500


# Register routes
image_bp.add_url_rule('/user/profile-image', view_func=UserImageUploadAPI.as_view('user_image_api'))
image_bp.add_url_rule('/products/<int:product_id>/image', view_func=ProductImageUploadAPI.as_view('product_image_api'))
