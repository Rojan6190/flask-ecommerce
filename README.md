# Flask E-Commerce API

A full-featured RESTful API for an e-commerce platform built with Flask, featuring user authentication, product management, shopping cart, offers, and image uploads.

## Features

- **User Authentication**: JWT-based auth with access and refresh tokens
- **Product Management**: CRUD operations with category filtering
- **Shopping Cart**: Add, update, and checkout items
- **Offers & Discounts**: Time-based discount system (up to 20%)
- **Image Uploads**: Profile pictures and product images
- **Admin Panel**: Admin-only endpoints for managing products and offers

## Tech Stack

- **Framework**: Flask 3.x
- **Database**: SQLAlchemy (SQLite for dev, PostgreSQL-ready)
- **Authentication**: Flask-JWT-Extended
- **Validation**: Marshmallow
- **Password Hashing**: Flask-Bcrypt
- **File Handling**: Werkzeug

## Installation

### Prerequisites
- Python 3.8+
- pip
- virtualenv (recommended)

### Setup

1. **Clone the repository**
```bash
   git clone https://github.com/rojan6190/flask-ecommerce.git
   cd flask-ecommerce
```

2. **Create virtual environment**
```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
   # Create .env file
   touch .env
```
   
   Add to `.env`:


apps.py: import os from datetime import timedelta from flask import Flask, jsonify from dotenv import load_dotenv from marshmallow import ValidationError # Import Models and Extensions from models import db, Category from schemas import ma from services.auth_service import bcrypt from flask_jwt_extended import JWTManager # Import Blueprints from routes.auth_routes import auth_bp from routes.product_routes import prod_bp from routes.cart_routes import cart_bp load_dotenv() def create_app(): app = Flask(__name__) # --- Configuration --- app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ecommerce.db') app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key') app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1) app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30) # --- Initialize Extensions --- db.init_app(app) ma.init_app(app) bcrypt.init_app(app) jwt = JWTManager(app) # --- Global Error Handlers (Industry Standard) --- @app.errorhandler(ValidationError) def handle_marshmallow_validation(err): return jsonify({"errors": err.messages}), 400 @app.errorhandler(404) def resource_not_found(e): return jsonify({"error": "Resource not found"}), 404 # --- Register Blueprints --- # Using prefixes helps versioning (e.g., /api/v1) app.register_blueprint(auth_bp, url_prefix='/api') app.register_blueprint(prod_bp, url_prefix='/api') app.register_blueprint(cart_bp, url_prefix='/api') # --- Database Setup & Seeding --- with app.app_context(): db.create_all() seed_categories() return app def seed_categories(): """Initializes the database with standard categories if empty.""" if not Category.query.first(): cats = ["Electronics", "Fashion", "Home", "Beauty", "Sports", "Books", "Toys", "Groceries", "Automotive", "Tools", "Pets", "Jewelry", "Music", "Movies", "Gaming", "Health", "Baby", "Office", "Industrial", "Software"] db.session.add_all([Category(name=c) for c in cats]) db.session.commit() print("Database seeded: 20 Categories created.") if __name__ == '__main__': app = create_app() app.run(debug=True) models.py: from flask_sqlalchemy import SQLAlchemy from datetime import datetime, timezone db = SQLAlchemy() class User(db.Model): id = db.Column(db.Integer, primary_key=True) username = db.Column(db.String(80), unique=True, nullable=False) password = db.Column(db.String(200), nullable=False) is_admin = db.Column(db.Boolean, default=False) class Category(db.Model): id = db.Column(db.Integer, primary_key=True) name = db.Column(db.String(50), unique=True, nullable=False) products = db.relationship('Product', backref='category', lazy=True) class Offer(db.Model): id = db.Column(db.Integer, primary_key=True) name = db.Column(db.String(100), nullable=False) discount_percent = db.Column(db.Float, nullable=False) # e.g. 20.0 start_time = db.Column(db.DateTime, nullable=False) # UTC end_time = db.Column(db.DateTime, nullable=False) # UTC products = db.relationship('Product', backref='offer', lazy=True) class Product(db.Model): id = db.Column(db.Integer, primary_key=True) name = db.Column(db.String, nullable=False) price = db.Column(db.Float, nullable=False) stock = db.Column(db.Integer, default=10) category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False) offer_id = db.Column(db.Integer, db.ForeignKey('offer.id'), nullable=True) class CartItem(db.Model): id = db.Column(db.Integer, primary_key=True) user_id = db.Column(db.Integer, db.ForeignKey('user.id')) product_id = db.Column(db.Integer, db.ForeignKey('product.id')) quantity = db.Column(db.Integer, default=1) product = db.relationship('Product') class Order(db.Model): id = db.Column(db.Integer, primary_key=True) user_id = db.Column(db.Integer, db.ForeignKey('user.id')) total_price = db.Column(db.Float) #Added class OrderItem(db.Model): id = db.Column(db.Integer, primary_key=True) order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False) product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False) quantity = db.Column(db.Integer, nullable=False) # THE SNAPSHOT: This stores the price at the exact second of purchase price_at_purchase = db.Column(db.Numeric(10, 2), nullable=False) schemas.py: from flask_marshmallow import Marshmallow from marshmallow import fields, validate, post_dump from models import User, Product, Category, CartItem, Offer, db from datetime import datetime, timezone ma = Marshmallow() class UserSchema(ma.SQLAlchemyAutoSchema): class Meta: model = User load_instance = True sqla_session = db.session load_only = ["password"] username = fields.String(required=True, validate=validate.Length(min=3)) password = fields.String(required=True, validate=validate.Length(min=6)) class CategorySchema(ma.SQLAlchemyAutoSchema): class Meta: model = Category load_instance = True sqla_session = db.session # We can add a field to show how many products are in this category product_count = fields.Method("get_product_count", dump_only=True) def get_product_count(self, obj): return len(obj.products) class OfferSchema(ma.SQLAlchemyAutoSchema): class Meta: model = Offer load_instance = True sqla_session = db.session discount_percent = fields.Float(required=True, validate=validate.Range(min=0, max=20)) start_time = fields.DateTime(format='iso') end_time = fields.DateTime(format='iso') class ProductSchema(ma.SQLAlchemyAutoSchema): class Meta: model = Product load_instance = True include_fk = True # Shows the category_id sqla_session = db.session price = fields.Float(validate=validate.Range(min=0.01)) # NESTING: This shows category details inside the product JSON category = ma.Nested(CategorySchema, only=("name",), dump_only=True) # 2. ADD THIS: Nest the offer details # We only pull 'name' and 'discount_percent' to keep the JSON small offer = ma.Nested(OfferSchema, only=("name", "discount_percent"), dump_only=True) #3. Calculated Fields current_price = fields.Method("get_current_price", dump_only=True) is_on_offer = fields.Method("check_offer_active", dump_only=True) discount_amount = fields.Method("get_discount_amount", dump_only=True) # Optional: How much they save def check_offer_active(self, obj): if obj.offer: now = datetime.now(timezone.utc) # Standardize DB time to UTC aware for comparison start = obj.offer.start_time.replace(tzinfo=timezone.utc) end = obj.offer.end_time.replace(tzinfo=timezone.utc) return start <= now <= end return False def get_current_price(self, obj): if self.check_offer_active(obj): discount = obj.offer.discount_percent / 100 return round(obj.price * (1 - discount), 2) return obj.price def get_discount_amount(self, obj): """Returns the cash value saved, e.g., $20.00""" if self.check_offer_active(obj): return round(obj.price - self.get_current_price(obj), 2) return 0.0 # Inside ProductSchema @post_dump def remove_expired_offer(self, data, many, **kwargs): if not data.get('is_on_offer'): data['offer'] = None return data class CartItemSchema(ma.SQLAlchemyAutoSchema): class Meta: model = CartItem load_instance = True include_fk = True sqla_session = db.session quantity = fields.Int(validate=validate.Range(min=1)) # Shows product details inside the cart product = ma.Nested(ProductSchema, dump_only=True) line_total = fields.Method("get_line_total", dump_only=True) def get_line_total(self, obj): # Calculates price based on whether an offer is active or not unit_price = ProductSchema().get_current_price(obj.product) return round(unit_price * obj.quantity, 2) # --- Initialize Global Schema Instances --- user_schema = UserSchema() category_schema = CategorySchema() categories_schema = CategorySchema(many=True) offer_schema = OfferSchema() offers_schema = OfferSchema(many=True) product_schema = ProductSchema() products_schema = ProductSchema(many=True) cart_item_schema = CartItemSchema() cart_items_schema = CartItemSchema(many=True) routes/init.py: # routes/__init__.py from .auth_routes import auth_bp from .product_routes import prod_bp from .cart_routes import cart_bp # This allows your app.py to do: # from routes import auth_bp, prod_bp, cart_bp routes/auth_routes.py: # routes/auth_routes.py from flask import Blueprint, request, jsonify from flask.views import MethodView from marshmallow import ValidationError from flask_jwt_extended import jwt_required, get_jwt_identity # Note: Using the Barrel Import from services/__init__.py from services import AuthService from schemas import user_schema auth_bp = Blueprint('auth', __name__) class RegisterAPI(MethodView): def post(self): try: data = request.get_json() user = AuthService.register_user(data) return jsonify({ "message": "User created", "user": user_schema.dump(user) }), 201 except ValidationError as err: return jsonify(err.messages), 400 except ValueError as e: return jsonify({"error": str(e)}), 400 class LoginAPI(MethodView): def post(self): data = request.get_json() tokens = AuthService.login_user(data) # Renamed to 'tokens' for clarity if tokens: # tokens is already a dict: {"access_token": "...", "refresh_token": "..."} # jsonify(tokens) sends that dict directly to the client return jsonify(tokens), 200 return jsonify({"message": "Invalid credentials"}), 401 class RefreshAPI(MethodView): @jwt_required(refresh=True) def post(self): user_id = get_jwt_identity() new_access_token = AuthService.refresh_access_token(user_id) if not new_access_token: # 401 is more standard for auth failure than 404 return jsonify({"msg": "Session invalid or user not found"}), 401 return jsonify(access_token=new_access_token), 200 # --- Route Registration --- auth_bp.add_url_rule('/register', view_func=RegisterAPI.as_view('register_api')) auth_bp.add_url_rule('/login', view_func=LoginAPI.as_view('login_api')) auth_bp.add_url_rule('/refresh', view_func=RefreshAPI.as_view('refresh_api')) # Ensure this is added! routes/cart_routes.py: from flask import Blueprint, request, jsonify from flask.views import MethodView from flask_jwt_extended import jwt_required, get_jwt_identity from services import CartService from schemas import cart_items_schema from marshmallow import ValidationError cart_bp = Blueprint('cart', __name__) class CartAPI(MethodView): decorators = [jwt_required()] def get(self): user_id = get_jwt_identity() items, total = CartService.get_user_cart(user_id) return jsonify({ "items": cart_items_schema.dump(items), # Serialization "grand_total": total }), 200 def post(self): user_id = get_jwt_identity() try: data = request.get_json() CartService.add_to_cart(user_id, data) # Deserialization inside service return jsonify({"message": "Added to cart"}), 201 except ValidationError as err: return jsonify(err.messages), 400 except ValueError as e: return jsonify({"error": str(e)}), 400 class CheckoutAPI(MethodView): decorators = [jwt_required()] def post(self): user_id = get_jwt_identity() try: total = CartService.checkout(user_id) return jsonify({"message": "Checkout successful", "total_paid": total}), 200 except ValueError as e: return jsonify({"error": str(e)}), 400 cart_bp.add_url_rule('/cart', view_func=CartAPI.as_view('cart_api')) cart_bp.add_url_rule('/checkout', view_func=CheckoutAPI.as_view('checkout_api')) product_routes.py: from flask import Blueprint, request, jsonify from flask.views import MethodView from flask_jwt_extended import jwt_required from services import ProductService from services import OfferService from schemas import ( product_schema, products_schema, offer_schema, categories_schema ) prod_bp = Blueprint('products', __name__) class ProductAPI(MethodView): def get(self): prods = ProductService.get_all_products() return jsonify(products_schema.dump(prods)), 200 @jwt_required() # @admin_required() <-- Use this once you've set up the decorator def post(self): data = request.get_json() product = ProductService.create_product(data) return jsonify(product_schema.dump(product)), 201 class OfferAPI(MethodView): @jwt_required() def post(self): """Admin creates an offer""" data = request.get_json() offer = OfferService.create_offer(data) return jsonify(offer_schema.dump(offer)), 201 class ActiveOffersAPI(MethodView): def get(self): """Public: See all products currently on sale""" products = OfferService.get_active_offers_products() return jsonify(products_schema.dump(products)), 200 class CategoryListAPI(MethodView): def get(self): """Returns all available categories using the Service""" categories = ProductService.get_all_categories() return jsonify(categories_schema.dump(categories)), 200 class ProductCategoryAPI(MethodView): def get(self, category_id): """Returns products by category using the Service""" products = ProductService.get_products_by_category(category_id) return jsonify(products_schema.dump(products)), 200 class ApplyOfferAPI(MethodView): # @admin_required() @jwt_required() def post(self, offer_id, product_id): try: # Note: We use OfferService here because that's where you defined the logic OfferService.apply_offer_to_product(offer_id, product_id) return jsonify({"message": f"Offer {offer_id} applied to product {product_id}"}), 200 except Exception as e: return jsonify({"error": str(e)}), 404 # --- URL Rules (Registration) --- prod_bp.add_url_rule('/products', view_func=ProductAPI.as_view('product_api')) prod_bp.add_url_rule('/offers', view_func=OfferAPI.as_view('offer_admin_api')) prod_bp.add_url_rule('/offers/active', view_func=ActiveOffersAPI.as_view('offer_active_api')) # MISSING RULES ADDED BELOW: prod_bp.add_url_rule('/categories', view_func=CategoryListAPI.as_view('category_list_api')) prod_bp.add_url_rule('/categories//products', view_func=ProductCategoryAPI.as_view('prod_cat_api')) prod_bp.add_url_rule('/offers//apply/', view_func=ApplyOfferAPI.as_view('apply_offer_api')) services/init.py: # services/__init__.py from .auth_service import AuthService, bcrypt from .product_service import ProductService from .cart_service import CartService from .offer_service import OfferService # This allows you to do: # from services import ProductService, CartService # Instead of: # from services.product_service import ProductService services/auth_service.py: # services/auth_service.py from models import db, User from flask_bcrypt import Bcrypt from flask_jwt_extended import create_access_token, create_refresh_token bcrypt = Bcrypt() class AuthService: @staticmethod def register_user(data): from schemas import user_schema user = user_schema.load(data) if User.query.filter_by(username=user.username).first(): raise ValueError("Username already exists") user.password = bcrypt.generate_password_hash(user.password).decode('utf-8') db.session.add(user) db.session.commit() return user @staticmethod def login_user(data): """Initial login: returns both Access and Refresh tokens.""" username = data.get('username') password = data.get('password') user = User.query.filter_by(username=username).first() if user and bcrypt.check_password_hash(user.password, password): # Industry standard: Access tokens should carry permissions (claims) # even if you aren't using admin logic today, keep the structure ready. #creates claims = {"is_admin": user.is_admin} return { "access_token": create_access_token(identity=str(user.id), additional_claims=claims), "refresh_token": create_refresh_token(identity=str(user.id)) } return None @staticmethod def refresh_access_token(user_id): """ Generates a new access token. Professionally, we re-verify the user in the DB to check for account status changes (e.g. if they were deleted or promoted). """ user = User.query.get(user_id) if not user: return None # Re-fetch claims from DB so the new token is up-to-date claims = {"is_admin": user.is_admin} return create_access_token(identity=str(user.id), additional_claims=claims) services/cart_service.py: from models import db, CartItem, Product, Order, OrderItem from sqlalchemy.exc import SQLAlchemyError class CartService: @staticmethod def add_to_cart(user_id, data): from schemas import cart_item_schema # 1. Deserialization & Validation (Auto-checks quantity > 0) item_data = cart_item_schema.load(data) product = Product.query.get_or_404(item_data.product_id) if product.stock < item_data.quantity: raise ValueError(f"Only {product.stock} items available") existing_item = CartItem.query.filter_by(user_id=user_id, product_id=product.id).first() if existing_item: existing_item.quantity += item_data.quantity else: item_data.user_id = user_id db.session.add(item_data) db.session.commit() return True @staticmethod def get_user_cart(user_id): items = CartItem.query.filter_by(user_id=user_id).all() # Grand total logic (Business Logic) # Note: We use the product_schema's logic for the current_price (Offer-aware) from schemas import product_schema total = sum(product_schema.get_current_price(i.product) * i.quantity for i in items) return items, round(total, 2) @staticmethod def checkout(user_id): from schemas import product_schema # To get current offer-aware price cart_items, total = CartService.get_user_cart(user_id) if not cart_items: raise ValueError("Cart is empty") try: # 1. Create the Order Parent new_order = Order(user_id=user_id, total_price=total) db.session.add(new_order) db.session.flush() # This generates the Order ID without committing yet # 2. Loop through cart and create Snapshots for cart_item in cart_items: if cart_item.product.stock < cart_item.quantity: raise ValueError(f"Stock for {cart_item.product.name} ran out") # Calculate the price the user is paying RIGHT NOW final_price = product_schema.get_current_price(cart_item.product) # Create the permanent record order_item = OrderItem( order_id=new_order.id, product_id=cart_item.product_id, quantity=cart_item.quantity, price_at_purchase=final_price ) db.session.add(order_item) # Deduct stock cart_item.product.stock -= cart_item.quantity # 3. Clear the cart and commit CartItem.query.filter_by(user_id=user_id).delete() db.session.commit() return total except Exception as e: db.session.rollback() raise e services/offer_service.py: from models import db, Offer, Product from datetime import datetime, timezone from sqlalchemy.orm import joinedload class OfferService: @staticmethod def create_offer(data): from schemas import offer_schema offer = offer_schema.load(data) db.session.add(offer) db.session.commit() return offer @staticmethod def apply_offer_to_product(offer_id, product_id): product = Product.query.get_or_404(product_id) product.offer_id = offer_id db.session.commit() return product @staticmethod def get_active_offers_products(): now = datetime.now(timezone.utc) return Product.query.join(Offer).options( joinedload(Product.category), joinedload(Product.offer) ).filter( Offer.start_time <= now, Offer.end_time >= now ).all() services/product_service.py: from models import db, Product, Category class ProductService: @staticmethod def create_product(data): from schemas import product_schema # Deserialization + Auto Validation product = product_schema.load(data) db.session.add(product) db.session.commit() return product @staticmethod def get_all_products(): return Product.query.all() @staticmethod def get_all_categories(): return Category.query.all() @staticmethod def get_products_by_category(category_id): return Product.query.filter_by(category_id=category_id).all() give me code so that I can upload image file of user and product. there's no ui for frontend so we are using client software insomnia

Show more
Jan 3
I'll help you add image upload functionality for both users and products. Since you're using Insomnia, I'll set this up for multipart/form-data file uploads.

Updated models.py with Image Fields
Code 
Insomnia Testing Guide for Image Upload
Document 
Perfect! I've created a complete image upload system for your e-commerce API. Here's what I've added:

📦 What's Included:
Updated Models - Added profile_image to User and image to Product
FileService - Handles image upload, validation, deletion with security features
Updated Schemas - Added image_url and profile_image_url fields
Image Routes - New endpoints for uploading/deleting images
Updated app.py - Registered image routes and static file serving
Complete Testing Guide - Step-by-step Insomnia instructions
🚀 Key Features:
✅ Security: File type validation, size limits (5MB), UUID-based filenames
✅ Automatic cleanup: Old images deleted when uploading new ones
✅ RESTful: Separate endpoints for users and products
✅ JWT protected: Requires authentication
✅ Industry standard: Using Werkzeug's secure_filename

📍 New API Endpoints:
POST /api/user/profile-image - Upload user profile picture
DELETE /api/user/profile-image - Delete user profile picture
POST /api/products/{id}/image - Upload product image
DELETE /api/products/{id}/image - Delete product image
⚠️ Important Setup Steps:
Delete your old database (backup first!): rm instance/ecommerce.db
Create image folders: mkdir -p static/users static/products
Run the app: python app.py
The testing guide artifact shows you exactly how to configure Insomnia with multipart form data. The key is selecting Multipart Form as the body type and adding a File field named image.

Need any adjustments or have questions about testing it?

give me all the updated files so I can copy paste it

Jan 3
All Updated Files - Complete Code
Code 
Perfect! I've compiled all the updated files into one artifact for easy copy-pasting. Here's what you need to do:

🚀 Quick Setup Steps:
1. Backup your current database (if you have data you want to keep)
bash
cp instance/ecommerce.db instance/ecommerce_backup.db
2. Delete the old database (to apply new schema)
bash
rm instance/ecommerce.db
3. Create the image folders
bash
mkdir -p static/users static/products
4. Copy-paste the files from the artifact above
Each file is clearly labeled with # FILE: filename.py
Just copy each section into the corresponding file
5. Run the application
bash
python app.py
📋 Files Updated/Created:
Updated:

✅ app.py - Added image routes, static file serving, file size limits
✅ models.py - Added profile_image and image columns
✅ schemas.py - Added image_url and profile_image_url fields
✅ routes/__init__.py - Added image_bp import
✅ services/__init__.py - Added FileService import
New Files:

🆕 routes/image_routes.py - Image upload/delete endpoints
🆕 services/file_service.py - Image handling logic
Unchanged (no need to update):

routes/auth_routes.py
routes/product_routes.py
routes/cart_routes.py
services/auth_service.py
services/product_service.py
services/cart_service.py
services/offer_service.py
🎯 Test It:
Register/Login to get a token
Use Insomnia to upload images:
POST /api/user/profile-image with multipart form field image
POST /api/products/1/image with multipart form field image
Check the previous testing guide artifact for detailed Insomnia instructions!

POST /api/user/profile-image with multipart form field image
POST /api/products/1/image with multipart form field image should we add GET for these
Jan 3
Great question! Yes, you should add GET endpoints. Here are the updated routes with GET methods:

All Updated Files - Complete Code
Code ∙ Version 2 
Perfect! I've added GET methods to both endpoints. Here's what changed:

✅ New GET Endpoints:
1. Get User Profile (with image)
GET /api/user/profile-image
Authorization: Bearer {token}
Response:

json
{
  "id": 1,
  "username": "john_doe",
  "is_admin": false,
  "profile_image_url": "/static/users/abc123.jpg"
}
```

### **2. Get Product Details (with image)**
```
GET /api/products/1/image
Response:

json
{
  "id": 1,
  "name": "iPhone 15",
  "price": 999.99,
  "stock": 50,
  "category_id": 1,
  "image_url": "/static/products/xyz789.jpg",
  "category": {"name": "Electronics"},
  "current_price": 999.99,
  "is_on_offer": false
}
🔐 Access Control:
User Profile GET: Requires authentication (returns YOUR profile)
Product GET: Public (anyone can view product details)
All POST/DELETE: Require authentication
📝 Design Decision:
The product GET is public because in a real e-commerce site, anyone should be able to browse products and see their images without logging in. But you need to be logged in to upload/delete images.

This gives you a complete RESTful interface:

GET - Read
POST - Create/Update
DELETE - Remove
Want me to adjust the authentication requirements?

how do I login as an admin and the status says is_admin=true? what could be done

Jan 3
Great question! Currently, there's no way to register as an admin through the API. Let me give you several options:

Admin User Solutions - Multiple Approaches
Document 
Now let me give you the complete updated app.py with the admin seeding (easiest solution):

app.py - With Admin User Seeding
Code 
Perfect! I've given you multiple solutions. Here's my recommendation:

🎯 Easiest Solution (Use This):
Just update your app.py with the version I just created above. It will automatically create an admin user when you first run the app.

Steps:
Copy the new app.py (from the artifact above)
Delete your database: rm instance/ecommerce.db
Run the app: python app.py
You'll see: ✅ Admin user created - Username: 'admin', Password: 'admin123'
Login as Admin:
json
POST /api/login
{
  "username": "admin",
  "password": "admin123"
}
The response will include a JWT token with is_admin: true in the claims.

Alternative: Manual Database Update
If you already have users and don't want to recreate the database:

bash
python
python
from app import create_app
from models import db, User

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='your_username').first()
    user.is_admin = True
    db.session.commit()
    print(f"{user.username} is now admin!")
Want More Security?
Check the first artifact for solutions with secret keys and admin promotion endpoints. But for development/testing, the seeded admin user is perfect!

Which approach would you like to use?

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



(.venv) PS D:\flask-ecommerce> python app.py
Database seeded: 20 Categories created.
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.      
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 890-436-096

why is the admin not being created by seed_admin(), what may be the problem and what can be the soutin
Show more
Jan 3
I see the problem! You defined seed_admin() but never called it. Look at your create_app() function:

python
with app.app_context():
    db.create_all()
    seed_categories()
    # seed_admin() is missing here! ❌
🔧 Solution:
Add the call to seed_admin():

python
# --- Database Setup & Seeding ---
with app.app_context():
    db.create_all()
    seed_categories()
    seed_admin()  # ✅ ADD THIS LINE
Here's the corrected section:

Fixed app.py - Admin Seed Actually Called
Code 
🎯 What to do now:
Stop your Flask server (CTRL+C)
Update your app.py with the fixed version above
Restart the server: python app.py
You should now see:

✅ Database seeded: 20 Categories created.
✅ Admin user created - Username: 'admin', Password: 'admin123'
⚠️  IMPORTANT: Change this password in production!
Bonus Fix:
I also fixed a small bug in your seed_admin() where you defined admin_password from the environment variable but then hardcoded 'admin123'. Now it actually uses the environment variable if set:

python
admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
admin = User(
    username='admin',
    password=bcrypt.generate_password_hash(admin_password).decode('utf-8'),  # ✅ Uses the variable
    is_admin=True
)
Now you can login with:

json
POST /api/login
{
  "username": "admin",
  "password": "admin123"
}
Try it and let me know if you see the admin creation message! 🚀


from flask import Blueprint, request, jsonify from flask.views import MethodView from flask_jwt_extended import jwt_required, get_jwt_identity from services.file_service import FileService from models import db, User, Product from schemas import user_schema, product_schema image_bp = Bluepri

pasted

isn't logic being repeated for user-profile and product image for uploading and deleting

Jan 4
You're absolutely right! There's a lot of code duplication. Let me refactor this to follow the DRY (Don't Repeat Yourself) principle:

Refactored routes/image_routes.py - DRY Principle
Code 
Perfect! Now let me also create an even cleaner alternative using a service layer approach:

Alternative: Service Layer Approach (Most Professional)
Code 
Excellent observation! I've provided two refactored approaches:

📦 Approach 1: Mixin Pattern (First Artifact)
Uses a mixin class to share common upload/delete logic
Both view classes inherit from the mixin
Good for when logic is tightly coupled to views
Code reduced by ~40%
🏆 Approach 2: Service Layer (Second Artifact) ⭐ RECOMMENDED
Creates a new ImageService class
Completely separates business logic from routes
Routes become super thin and readable
Most professional and maintainable
Code reduced by ~50%
📊 Comparison:
Before (Your Original):
120+ lines with massive duplication
Upload logic repeated twice
Delete logic repeated twice
Hard to test and maintain
After (Service Layer):
~80 lines total (including new service file)
Single source of truth for upload/delete
Easy to test business logic separately
Easy to add new entities (e.g., Category images)
🎯 Which to Use?
Use Approach 2 (Service Layer) because:

✅ Follows your existing project pattern (AuthService, ProductService, etc.)
✅ Easier to unit test
✅ Can reuse ImageService for future features (e.g., multiple images per product)
✅ Business logic is centralized
📝 To Implement:
Create services/image_service.py (from second artifact)
Replace routes/image_routes.py (from second artifact)
Update services/__init__.py (from second artifact)
The routes are now so clean that each method is just:

Validate input
Call service
Return response
Perfect separation of concerns! 🎉

and what will be in file_service.py:

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
Show more
Jan 4
Your file_service.py looks great! It's already well-structured and handles low-level file operations perfectly. Here it is with some minor improvements and better documentation:

Enhanced services/file_service.py
Code 
Perfect! Your original file_service.py was already excellent. I made just a few small enhancements:

✅ What I Added:
Better documentation - Added detailed docstrings for each method
Return values - delete_image() now returns True/False to indicate success
Error handling - Added try-catch for OS errors during deletion
New helper method - file_exists() to check if a file exists (useful for debugging)
Validation improvement - save_image() now raises error if no file provided (instead of returning None)
📊 Your File Service Architecture:
FileService (Low-level)
    ↓
ImageService (Business logic)
    ↓
Routes (HTTP handling)
Separation of concerns:

FileService = Raw file I/O operations (save, delete, validate)
ImageService = Business logic (which entity, which folder, database updates)
Routes = HTTP request/response handling
🎯 Current State:
Your file_service.py is production-ready as-is! The enhancements I added are nice-to-haves but not essential. You can use either:

Your original version ✅ (already excellent)
Enhanced version ✅ (slightly more robust with better error handling)
Both work perfectly with the ImageService we created earlier. The key is that FileService focuses purely on file operations, while ImageService handles the business logic of connecting files to database entities.

Want to keep your original or use the enhanced version?

tell me the steps to create README for this project in the vs code and I have already pushed the project before in git and github, now pushing with the README

7:25 PM
Here's a complete guide to create and push a README for your Flask e-commerce project:

README Creation & Git Push Guide
Document 
Now let me also create a ready-to-use README template specifically for your project:

Ready-to-Use README.md Template
Document 
Perfect! Now here are the exact steps in VS Code terminal:

🎯 Quick Steps (Copy-Paste These):
bash
# Step 1: Create README.md file
touch README.md

# Step 2: Open README.md in VS Code
# (It should open automatically, or click on it in the file explorer)

# Step 3: Copy the "Ready-to-Use README.md Template" artifact above
#         and paste it into README.md

# Step 4: Generate requirements.txt (if you haven't already)
pip freeze > requirements.txt

# Step 5: Check what files have changed
git status

# Step 6: Add the new files
git add README.md requirements.txt

# Step 7: Commit with a descriptive message
git commit -m "docs: add comprehensive README and requirements.txt"

# Step 8: Push to GitHub (replace 'main' with 'master' if needed)
git push origin main

# Step 9: Visit your GitHub repository in browser to see the README!
📝 Customize the README:
Before pushing, replace these placeholders in the README:

Repository URL: Line 37 - Change yourusername to your GitHub username
Author Section: Near the bottom - Add your name and links
Badges: Optional - Keep or remove based on preference
✅ Verify Success:
After pushing, your GitHub repository homepage will automatically display the README with:

Formatted markdown
Code blocks with syntax highlighting
Tables and badges
Emoji support
That's it! Your project now has professional documentation! 🎉



Want to be notified when Claude responds?



Claude is AI and can make mistakes. Please double-check responses.
📝 Creating and Pushing README to GitHub
Step 1: Create README.md in VS Code
Option A: Using VS Code UI
In VS Code, click on your project folder in the Explorer
Click the "New File" icon (or right-click → New File)
Name it: README.md
The file will open automatically
Option B: Using Terminal in VS Code
bash
# Open terminal in VS Code (Ctrl + ` or View → Terminal)
touch README.md
# or
echo "# Flask E-Commerce API" > README.md
Step 2: Write Your README
Copy this template and customize it:

markdown
# 🛒 Flask E-Commerce API

A full-featured RESTful API for an e-commerce platform built with Flask, featuring user authentication, product management, shopping cart, offers, and image uploads.

## 🚀 Features

- **User Authentication**: JWT-based auth with access and refresh tokens
- **Product Management**: CRUD operations with category filtering
- **Shopping Cart**: Add, update, and checkout items
- **Offers & Discounts**: Time-based discount system (up to 20%)
- **Image Uploads**: Profile pictures and product images
- **Admin Panel**: Admin-only endpoints for managing products and offers

## 🛠️ Tech Stack

- **Framework**: Flask 3.x
- **Database**: SQLAlchemy (SQLite for dev, PostgreSQL-ready)
- **Authentication**: Flask-JWT-Extended
- **Validation**: Marshmallow
- **Password Hashing**: Flask-Bcrypt
- **File Handling**: Werkzeug

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip
- virtualenv (recommended)

### Setup

1. **Clone the repository**
```bash
   git clone https://github.com/yourusername/flask-ecommerce.git
   cd flask-ecommerce
```

2. **Create virtual environment**
```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
   # Create .env file
   touch .env
```
   
   Add to `.env`:
DATABASE_URL=sqlite:///ecommerce.db
JWT_SECRET_KEY=your-secret-key-here
ADMIN_PASSWORD=admin123


5. **Create required folders**
```bash
   mkdir -p static/users static/products
```

6. **Run the application**
```bash
   python app.py
```
# For any new interns, the following are the steps how approached to make this project

## Topics covered in Week 1:
- working with lower framework first like Flask
- learning why django chose MVT approach and what DRF solved in Django?
- learning different types of APIS
- What not to push in git

## Topics covered in Week 2:
- JSON format: 
- JWT authentication token
- Session based authentication
- Web services
- REST 
- RPC
- ODoo
- Task to build this api using Flask using jwt(token-based) authentication, using Insomnia as api client, build- CRUD (e-commerce service: product, order, cart, etc..)
- Following DRY and SOLID principles

## Topics covered in Week 3:
- use python error handling (try, except)
- use serializer (Marshmallow)
- research on date-time, timezone, timedelta, dst, utc, timezones
- adding featuring in this api: "Offer" service where comparing date-time between client and server (how to handle date-time between them)
- simply saying "a client choosing a product with an offer valid from a certain time range"
- using class-based views (MethodView)  
- Also adding "Categories" service 

## Topics covered in Week 4:
- Uploading image files in this api, (see the documentation of flask for uploading files)




