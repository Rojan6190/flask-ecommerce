from flask_marshmallow import Marshmallow
from marshmallow import fields, validate, post_dump, validates_schema, ValidationError
from models import User, Product, Category, CartItem, Offer, db
from datetime import datetime, timezone

ma = Marshmallow()

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        sqla_session = db.session
        load_only = ["password"]
    
    username = fields.String(required=True, validate=validate.Length(min=3))
    password = fields.String(required=True, validate=validate.Length(min=6))
    profile_image_url = fields.Method("get_profile_image_url", dump_only=True)
    
    def get_profile_image_url(self, obj):
        if obj.profile_image:
            return f"/static/users/{obj.profile_image}"
        return None

class CategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        load_instance = True
        sqla_session = db.session
    
    product_count = fields.Method("get_product_count", dump_only=True)
    
    def get_product_count(self, obj):
        return len(obj.products)

class OfferSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Offer
        load_instance = True
        sqla_session = db.session
    
    discount_percent = fields.Float(required=True, validate=validate.Range(min=0, max=50))
    start_time = fields.DateTime(format='iso')
    end_time = fields.DateTime(format='iso')
   
    @validates_schema
    def validate_dates(self, data, **kwargs):
        """
        Ensure start_time < end_time
        """
        start = data.get("start_time")
        end = data.get("end_time")
        
        if start and end and start >= end:
            raise ValidationError("end_time must be after start_time")
        
class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
        include_fk = True
        sqla_session = db.session
    
    price = fields.Float(validate=validate.Range(min=0.01))
    
    #dump only->serialization (output)
    category = ma.Nested(CategorySchema, only=("name",), dump_only=True)
    offer = ma.Nested(OfferSchema, only=("name", "discount_percent"), dump_only=True)
    
    # NEW: Image URL field
    image_url = fields.Method("get_image_url", dump_only=True)
    
    # Calculated fields
    current_price = fields.Method("get_current_price", dump_only=True)
    is_on_offer = fields.Method("check_offer_active", dump_only=True)
    discount_amount = fields.Method("get_discount_amount", dump_only=True)
    
    def get_image_url(self, obj):
        if obj.image:
            return f"/static/products/{obj.image}"
        return None
    
    def check_offer_active(self, obj):
        if obj.offer:
            now = datetime.now(timezone.utc)
            start = obj.offer.start_time.replace(tzinfo=timezone.utc)
            end = obj.offer.end_time.replace(tzinfo=timezone.utc)
            return start <= now <= end
        return False
    
    def get_current_price(self, obj):
        if self.check_offer_active(obj):
            discount = obj.offer.discount_percent / 100
            return round(obj.price * (1 - discount), 2)
        return obj.price
    
    def get_discount_amount(self, obj):
        if self.check_offer_active(obj):
            return round(obj.price - self.get_current_price(obj), 2)
        return 0.0
    
    @post_dump
    def remove_expired_offer(self, data, many, **kwargs):
        if not data.get('is_on_offer'):
            data['offer'] = None
        return data

class CartItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CartItem
        load_instance = True
        include_fk = True
        sqla_session = db.session
    
    quantity = fields.Int(validate=validate.Range(min=1))
    product = ma.Nested(ProductSchema, dump_only=True)
    line_total = fields.Method("get_line_total", dump_only=True)
    
    def get_line_total(self, obj):
        unit_price = ProductSchema().get_current_price(obj.product)
        return round(unit_price * obj.quantity, 2)

# Schema instances
user_schema = UserSchema()
users_schema = UserSchema(many=True)
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)
offer_schema = OfferSchema()
offers_schema = OfferSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
cart_item_schema = CartItemSchema()
cart_items_schema = CartItemSchema(many=True)