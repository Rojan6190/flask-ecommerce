from flask import Blueprint, request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from services import CartService
from schemas import cart_items_schema
from marshmallow import ValidationError

cart_bp = Blueprint('cart', __name__)

class CartAPI(MethodView):
    decorators = [jwt_required()]
    
    def get(self):
        user_id = get_jwt_identity()
        items, total = CartService.get_user_cart(user_id)
        return jsonify({
            "items": cart_items_schema.dump(items),
            "grand_total": total
        }), 200
    
    def post(self):
        user_id = get_jwt_identity()
        try:
            data = request.get_json()
            CartService.add_to_cart(user_id, data)
            return jsonify({"message": "Added to cart"}), 201
        except ValidationError as err:
            return jsonify(err.messages), 400
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

class CheckoutAPI(MethodView):
    decorators = [jwt_required()]
    
    def post(self):
        user_id = get_jwt_identity()
        try:
            total = CartService.checkout(user_id)
            return jsonify({"message": "Checkout successful", "total_paid": total}), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

cart_bp.add_url_rule('/cart', view_func=CartAPI.as_view('cart_api'))
cart_bp.add_url_rule('/checkout', view_func=CheckoutAPI.as_view('checkout_api'))

