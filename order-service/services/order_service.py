import uuid
from decimal import Decimal

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import (
    InsufficientStockError,
    OrderNotFoundException,
    ProductNotFoundError,
    ProductServiceError,
)
from repositories.order_repository import OrderRepository
from schemas.order import CreateOrderRequest, OrderResponse, UpdateOrderStatusRequest
from utils.http_client import get_product


class OrderService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = OrderRepository(session)

    async def create_order(
        self, user_id: uuid.UUID, payload: CreateOrderRequest, authorization: str | None = None
    ) -> OrderResponse:
        """
        1. Fetch each product from product-service
        2. Validate stock > 0
        3. Build item snapshots
        4. Persist order + items in a single transaction
        """
        order_items = []
        total = Decimal("0.00")

        for item_req in payload.items:
            try:
                product = await get_product(str(item_req.product_id), authorization)
            except httpx.RequestError:
                raise ProductServiceError()

            if product is None:
                raise ProductNotFoundError(str(item_req.product_id))

            if product.get("stock", 0) < item_req.quantity:
                raise InsufficientStockError(product.get("name", str(item_req.product_id)))

            unit_price = Decimal(str(product["price"]))
            subtotal = unit_price * item_req.quantity
            total += subtotal

            order_items.append({
                "product_id": item_req.product_id,
                "product_name": product["name"],
                "unit_price": unit_price,
                "quantity": item_req.quantity,
                "subtotal": subtotal,
            })

        order = await self.repo.create(
            user_id=user_id,
            total=total,
            notes=payload.notes,
            items=order_items,
        )
        return OrderResponse.model_validate(order)

    async def list_orders(self, user_id: uuid.UUID) -> list[OrderResponse]:
        orders = await self.repo.list_by_user(user_id)
        return [OrderResponse.model_validate(o) for o in orders]

    async def get_order(self, order_id: uuid.UUID, user_id: uuid.UUID) -> OrderResponse:
        order = await self.repo.get_by_id(order_id)
        if not order or order.user_id != user_id:
            raise OrderNotFoundException()
        return OrderResponse.model_validate(order)

    async def update_status(
        self, order_id: uuid.UUID, payload: UpdateOrderStatusRequest, user_id: uuid.UUID
    ) -> OrderResponse:
        order = await self.repo.get_by_id(order_id)
        if not order or order.user_id != user_id:
            raise OrderNotFoundException()
        order = await self.repo.update_status(order, payload.status)
        return OrderResponse.model_validate(order)
