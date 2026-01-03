# routes/__init__.py

from .auth_routes import auth_bp
from .product_routes import prod_bp
from .cart_routes import cart_bp

# This allows your app.py to do:
# from routes import auth_bp, prod_bp, cart_bp