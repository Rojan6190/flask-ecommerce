import os
from datetime import timedelta
from flask import Flask, jsonify, send_from_directory
from dotenv import load_dotenv
from marshmallow import ValidationError

# Import Models and Extensions
from models import db, Category, User
from schemas import ma
from services.auth_service import bcrypt
from flask_jwt_extended import JWTManager

# Import Blueprints
from routes.auth_routes import auth_bp
from routes.product_routes import prod_bp
from routes.cart_routes import cart_bp
from routes.image_routes import image_bp

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # --- Configuration ---
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ecommerce.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # File Upload Configuration
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
    
    # --- Initialize Extensions ---
    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt = JWTManager(app)
    
    # --- Global Error Handlers ---
    @app.errorhandler(ValidationError)
    def handle_marshmallow_validation(err):
        return jsonify({"errors": err.messages}), 400
    
    @app.errorhandler(404)
    def resource_not_found(e):
        return jsonify({"error": "Resource not found"}), 404
    
    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"error": "File too large. Maximum size: 5MB"}), 413
    
    # --- Serve Static Files (Images) ---
    @app.route('/static/<folder>/<filename>')
    def serve_image(folder, filename):
        """Serve uploaded images"""
        return send_from_directory(os.path.join(app.root_path, 'static', folder), filename)
    
    # --- Register Blueprints ---
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(prod_bp, url_prefix='/api')
    app.register_blueprint(cart_bp, url_prefix='/api')
    app.register_blueprint(image_bp, url_prefix='/api')
    
    # --- Database Setup & Seeding ---
    with app.app_context():
        db.create_all()
        seed_categories()
        seed_admin()
    
    return app

def seed_categories():
    """Initializes the database with standard categories if empty."""
    if not Category.query.first():
        cats = ["Electronics", "Fashion", "Home", "Beauty", "Sports", "Books", 
                "Toys", "Groceries", "Automotive", "Tools", "Pets", "Jewelry", 
                "Music", "Movies", "Gaming", "Health", "Baby", "Office", 
                "Industrial", "Software"]
        db.session.add_all([Category(name=c) for c in cats])
        db.session.commit()
        print("Database seeded: 20 Categories created.")

def seed_admin():
    """creating default admin user if doesn't exist"""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        admin = User(
            username='admin',
            password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created - Username: 'admin', Password: 'admin123'")
        print("IMPORTANT: Change this password in production!")
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)