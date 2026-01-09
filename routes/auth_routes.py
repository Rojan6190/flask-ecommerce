from flask import Blueprint, request, jsonify
from flask.views import MethodView
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
from services import AuthService
from schemas import user_schema

auth_bp = Blueprint('auth', __name__)

class RegisterAPI(MethodView):
    def post(self):
        try:
            data = request.get_json()
            user = AuthService.register_user(data)
            return jsonify({
                "message": "User created",
                "user": user_schema.dump(user)     #serializes
            }), 201
        except ValidationError as err:
            return jsonify(err.messages), 400
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

class LoginAPI(MethodView):
    def post(self):
        data = request.get_json()
        tokens = AuthService.login_user(data)
        if tokens:
            return jsonify(tokens), 200
        return jsonify({"message": "Invalid credentials"}), 401

class RefreshAPI(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        user_id = get_jwt_identity()
        new_access_token = AuthService.refresh_access_token(user_id)
        if not new_access_token:
            return jsonify({"msg": "Session invalid or user not found"}), 401
        return jsonify(access_token=new_access_token), 200

auth_bp.add_url_rule('/register', view_func=RegisterAPI.as_view('register_api'))
auth_bp.add_url_rule('/login', view_func=LoginAPI.as_view('login_api'))
auth_bp.add_url_rule('/refresh', view_func=RefreshAPI.as_view('refresh_api'))

