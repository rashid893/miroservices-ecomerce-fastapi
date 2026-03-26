import math
import uuid
from decimal import Decimal
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import CategoryNotFoundException, ProductNotFoundException, SlugAlreadyExistsError
from repositories.product_repository import CategoryRepository, ProductRepository
from schemas.product import (
    CategoryCreate, CategoryResponse,
    PaginatedProductResponse, ProductCreate, ProductResponse, ProductUpdate,
)


class CategoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = CategoryRepository(session)

    async def create(self, payload: CategoryCreate) -> CategoryResponse:
        category = await self.repo.create(name=payload.name, description=payload.description)
        return CategoryResponse.model_validate(category)

    async def list_all(self) -> list[CategoryResponse]:
        categories = await self.repo.get_all()
        return [CategoryResponse.model_validate(c) for c in categories]


class ProductService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = ProductRepository(session)
        self.cat_repo = CategoryRepository(session)

    async def create(self, payload: ProductCreate) -> ProductResponse:
        if payload.category_id:
            cat = await self.cat_repo.get_by_id(payload.category_id)
            if not cat:
                raise CategoryNotFoundException()
        slug = slugify(payload.name)
        existing = await self.repo.get_by_slug(slug)
        if existing:
            raise SlugAlreadyExistsError()
        product = await self.repo.create(
            name=payload.name, slug=slug, description=payload.description,
            price=payload.price, stock=payload.stock,
            category_id=payload.category_id, is_active=payload.is_active,
        )
        return ProductResponse.model_validate(product)

    async def list_paginated(self, page: int, page_size: int) -> PaginatedProductResponse:
        items, total = await self.repo.list_paginated(page=page, page_size=page_size)
        return PaginatedProductResponse(
            items=[ProductResponse.model_validate(p) for p in items],
            total=total, page=page, page_size=page_size,
            pages=math.ceil(total / page_size) if total else 0,
        )

    async def get_by_id(self, product_id: uuid.UUID) -> ProductResponse:
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException()
        return ProductResponse.model_validate(product)

    async def update(self, product_id: uuid.UUID, payload: ProductUpdate) -> ProductResponse:
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException()
        update_data = payload.model_dump(exclude_unset=True)
        product = await self.repo.update(product, **update_data)
        return ProductResponse.model_validate(product)

    async def delete(self, product_id: uuid.UUID) -> None:
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException()
        await self.repo.delete(product)
