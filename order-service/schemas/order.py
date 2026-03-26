import uuid
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class OrderItemRequest(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(ge=1)

class CreateOrderRequest(BaseModel):
    items: list[OrderItemRequest] = Field(min_length=1)
    notes: str | None = None

class UpdateOrderStatusRequest(BaseModel):
    status: str = Field(pattern="^(pending|paid|cancelled|shipped)$")

class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    product_id: uuid.UUID
    product_name: str
    unit_price: Decimal
    quantity: int
    subtotal: Decimal

class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    total: Decimal
    notes: str | None
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime
