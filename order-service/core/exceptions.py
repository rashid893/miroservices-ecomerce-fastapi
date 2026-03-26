from fastapi import HTTPException, status

class OrderNotFoundException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

class ProductServiceError(HTTPException):
    def __init__(self, detail: str = "Failed to communicate with product service.") -> None:
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)

class InsufficientStockError(HTTPException):
    def __init__(self, product_name: str) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Insufficient stock for product: {product_name}")

class ProductNotFoundError(HTTPException):
    def __init__(self, product_id: str) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product not found: {product_id}")
