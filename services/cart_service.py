from models import db, CartItem, Product, Order, OrderItem

class CartService:
    @staticmethod
    def add_to_cart(user_id, data):
        from schemas import cart_item_schema
        item_data = cart_item_schema.load(data)
        product = Product.query.get_or_404(item_data.product_id)
        if product.stock < item_data.quantity:
            raise ValueError(f"Only {product.stock} items available")
        existing_item = CartItem.query.filter_by(user_id=user_id, product_id=product.id).first()
        if existing_item:
            existing_item.quantity += item_data.quantity
        else:
            item_data.user_id = user_id
            db.session.add(item_data)
        db.session.commit()
        return True
    
    @staticmethod
    def get_user_cart(user_id):
        items = CartItem.query.filter_by(user_id=user_id).all()
        from schemas import product_schema
        total = sum(product_schema.get_current_price(i.product) * i.quantity for i in items)
        return items, round(total, 2)
    
    @staticmethod
    def checkout(user_id):
        from schemas import product_schema
        cart_items, total = CartService.get_user_cart(user_id)
        if not cart_items:
            raise ValueError("Cart is empty")
        try:
            new_order = Order(user_id=user_id, total_price=total)
            db.session.add(new_order)
            db.session.flush()
            for cart_item in cart_items:
                if cart_item.product.stock < cart_item.quantity:
                    raise ValueError(f"Stock for {cart_item.product.name} ran out")
                final_price = product_schema.get_current_price(cart_item.product)
                order_item = OrderItem(
                    order_id=new_order.id,
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    price_at_purchase=final_price
                )
                db.session.add(order_item)
                cart_item.product.stock -= cart_item.quantity
            CartItem.query.filter_by(user_id=user_id).delete()
            db.session.commit()
            return total
        except Exception as e:
            db.session.rollback()
            raise e
