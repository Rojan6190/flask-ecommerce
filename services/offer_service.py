from models import db, Offer, Product
from datetime import datetime, timezone
from sqlalchemy.orm import joinedload
from exceptions import ProductNotFoundException, OfferNotFoundException
class OfferService:
    @staticmethod
    def create_offer(data):
        from schemas import offer_schema
        offer = offer_schema.load(data)
        db.session.add(offer)
        db.session.commit()
        return offer
    
    @staticmethod
    def apply_offer_to_product(offer_id, product_id):
        # Check if product exists
        product = Product.query.get(product_id)
        if not product:
            raise ProductNotFoundException(product_id)
        
        # Check if offer exists
        offer = Offer.query.get(offer_id)
        if not offer:
            raise OfferNotFoundException(offer_id)
        
        # Apply offer
        product.offer_id = offer_id
        db.session.commit()
        return product
    
    
    @staticmethod
    def get_active_offers_products():
        now = datetime.now(timezone.utc)
        return Product.query.join(Offer).options(
            joinedload(Product.category),
            joinedload(Product.offer)
        ).filter(
            Offer.start_time <= now,
            Offer.end_time >= now
        ).all()
