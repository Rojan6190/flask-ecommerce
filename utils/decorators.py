# utils/decorators.py
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt
from flask import jsonify

def admin_required(fn):
    """Decorator to require admin privileges"""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):  
        claims = get_jwt()
        if not claims.get('is_admin'):
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs) 
    return wrapper