import uuid
import math
from decimal import Decimal
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Category, Product


class CategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self) -> list[Category]:
        result = await self.session.execute(select(Category).order_by(Category.name))
        return list(result.scalars().all())

    async def get_by_id(self, category_id: uuid.UUID) -> Category | None:
        result = await self.session.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    async def create(self, name: str, description: str | None) -> Category:
        category = Category(name=name, description=description)
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, product_id: uuid.UUID) -> Product | None:
        result = await self.session.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Product | None:
        result = await self.session.execute(select(Product).where(Product.slug == slug))
        return result.scalar_one_or_none()

    async def list_paginated(self, page: int, page_size: int, active_only: bool = True):
        query = select(Product)
        count_query = select(func.count()).select_from(Product)
        if active_only:
            query = query.where(Product.is_active == True)
            count_query = count_query.where(Product.is_active == True)
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()
        query = query.offset((page - 1) * page_size).limit(page_size).order_by(Product.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def create(self, name: str, slug: str, description: str | None, price: Decimal,
                     stock: int, category_id: uuid.UUID | None, is_active: bool) -> Product:
        product = Product(name=name, slug=slug, description=description, price=price,
                          stock=stock, category_id=category_id, is_active=is_active)
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def update(self, product: Product, **kwargs) -> Product:
        for key, value in kwargs.items():
            if value is not None:
                setattr(product, key, value)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def delete(self, product: Product) -> None:
        await self.session.delete(product)
        await self.session.commit()
