# exceptions.py
class BaseAppException(Exception):
    """Base exception for the application"""
    pass

class NotFoundException(BaseAppException):
    """Resource not found"""
    def __init__(self, resource_type, resource_id):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"{resource_type} with ID {resource_id} not found")

class ProductNotFoundException(NotFoundException):
    """Product not found"""
    def __init__(self, product_id):
        super().__init__("Product", product_id)

class OfferNotFoundException(NotFoundException):
    """Offer not found"""
    def __init__(self, offer_id):
        super().__init__("Offer", offer_id)

class ValidationException(BaseAppException):
    """Validation error"""
    pass