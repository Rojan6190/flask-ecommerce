from models import db, Product, Category

class ProductService:
    @staticmethod
    def create_product(data):
        from schemas import product_schema
        product = product_schema.load(data)
        db.session.add(product)
        db.session.commit()
        return product
    
    @staticmethod
    def get_all_products():
        return Product.query.all()
    
    @staticmethod
    def get_all_categories():
        return Category.query.all()
    
    @staticmethod
    def get_products_by_category(category_id):
        return Product.query.filter_by(category_id=category_id).all()
