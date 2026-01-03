from models import db, User
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token

bcrypt = Bcrypt()

class AuthService:
    @staticmethod
    def register_user(data):
        from schemas import user_schema
        user = user_schema.load(data)
        if User.query.filter_by(username=user.username).first():
            raise ValueError("Username already exists")
        user.password = bcrypt.generate_password_hash(user.password).decode('utf-8')
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def login_user(data):
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            claims = {"is_admin": user.is_admin}
            return {
                "access_token": create_access_token(identity=str(user.id), additional_claims=claims),
                "refresh_token": create_refresh_token(identity=str(user.id)),
                "user":{
                    "id": user.id,
                    "is_admin":user.is_admin
                }
            }
        
        return None
    
    @staticmethod
    def refresh_access_token(user_id):
        user = User.query.get(user_id)
        if not user:
            return None
        claims = {"is_admin": user.is_admin}
        return create_access_token(identity=str(user.id), additional_claims=claims)
