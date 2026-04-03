import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None

class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    # ADDED max_digits here as well to match ProductUpdate
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(ge=0)
    category_id: uuid.UUID | None = None
    is_active: bool = True

class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    # This looks good, keeping it as is
    price: float = Field(gt=0)
    #price: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    stock: int | None = Field(default=None, ge=0)
    category_id: uuid.UUID | None = None
    is_active: bool | None = None

class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    price: Decimal
    stock: int
    category_id: uuid.UUID | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

class PaginatedProductResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
    pages: int