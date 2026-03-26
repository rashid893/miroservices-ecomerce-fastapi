import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from dependencies.auth import get_current_user_payload, require_admin
from schemas.product import (
    CategoryCreate, CategoryResponse,
    PaginatedProductResponse, ProductCreate, ProductResponse, ProductUpdate,
)
from services.product_service import CategoryService, ProductService

router = APIRouter(prefix="/api/v1", tags=["Products"])


def get_product_service(session: AsyncSession = Depends(get_db)) -> ProductService:
    return ProductService(session)

def get_category_service(session: AsyncSession = Depends(get_db)) -> CategoryService:
    return CategoryService(session)


@router.post("/categories", response_model=CategoryResponse, status_code=201)
async def create_category(
    payload: CategoryCreate,
    svc: CategoryService = Depends(get_category_service),
    _=Depends(require_admin),
) -> CategoryResponse:
    return await svc.create(payload)


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(svc: CategoryService = Depends(get_category_service)) -> list[CategoryResponse]:
    return await svc.list_all()


@router.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(
    payload: ProductCreate,
    svc: ProductService = Depends(get_product_service),
    _=Depends(require_admin),
) -> ProductResponse:
    return await svc.create(payload)


@router.get("/products", response_model=PaginatedProductResponse)
async def list_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    svc: ProductService = Depends(get_product_service),
) -> PaginatedProductResponse:
    return await svc.list_paginated(page=page, page_size=page_size)


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: uuid.UUID, svc: ProductService = Depends(get_product_service)) -> ProductResponse:
    return await svc.get_by_id(product_id)


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: uuid.UUID,
    payload: ProductUpdate,
    svc: ProductService = Depends(get_product_service),
    _=Depends(require_admin),
) -> ProductResponse:
    return await svc.update(product_id, payload)


@router.delete("/products/{product_id}", status_code=204)
async def delete_product(
    product_id: uuid.UUID,
    svc: ProductService = Depends(get_product_service),
    _=Depends(require_admin),
) -> None:
    await svc.delete(product_id)
