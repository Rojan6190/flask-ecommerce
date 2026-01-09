from flask import Blueprint, request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from services import ProductService, OfferService
from schemas import product_schema, products_schema, offer_schema, categories_schema
from utils.decorators import admin_required  # Import decorator

prod_bp = Blueprint('products', __name__)

class ProductAPI(MethodView):
    def get(self):
        prods = ProductService.get_all_products()
        return jsonify(products_schema.dump(prods)), 200
    
    @admin_required
    def post(self):
        data = request.get_json()
        product = ProductService.create_product(data)
        return jsonify(product_schema.dump(product)), 201

class OfferAPI(MethodView):
    @admin_required 
    def post(self):
        data = request.get_json()
        offer = OfferService.create_offer(data)
        return jsonify(offer_schema.dump(offer)), 201

class ActiveOffersAPI(MethodView):
    def get(self):
        products = OfferService.get_active_offers_products()
        return jsonify(products_schema.dump(products)), 200

class CategoryListAPI(MethodView):
    def get(self):
        categories = ProductService.get_all_categories()
        return jsonify(categories_schema.dump(categories)), 200

class ProductCategoryAPI(MethodView):
    def get(self, category_id):
        products = ProductService.get_products_by_category(category_id)
        return jsonify(products_schema.dump(products)), 200

class ApplyOfferAPI(MethodView):
    @admin_required
    def post(self, offer_id, product_id):
        try:
            OfferService.apply_offer_to_product(offer_id, product_id)
            return jsonify({"message": f"Offer {offer_id} applied to product {product_id}"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 404

prod_bp.add_url_rule('/products', view_func=ProductAPI.as_view('product_api'))
prod_bp.add_url_rule('/offers', view_func=OfferAPI.as_view('offer_admin_api'))
prod_bp.add_url_rule('/offers/active', view_func=ActiveOffersAPI.as_view('offer_active_api'))
prod_bp.add_url_rule('/categories', view_func=CategoryListAPI.as_view('category_list_api'))
prod_bp.add_url_rule('/categories/<int:category_id>/products', view_func=ProductCategoryAPI.as_view('prod_cat_api'))
prod_bp.add_url_rule('/offers/<int:offer_id>/apply/<int:product_id>', view_func=ApplyOfferAPI.as_view('apply_offer_api'))
