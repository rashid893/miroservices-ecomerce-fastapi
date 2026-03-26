import uuid
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from db.models import Order, OrderItem


class OrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, order_id: uuid.UUID) -> Order | None:
        result = await self.session.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items))
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: uuid.UUID) -> list[Order]:
        result = await self.session.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(
        self,
        user_id: uuid.UUID,
        total: Decimal,
        notes: str | None,
        items: list[dict],
    ) -> Order:
        order = Order(user_id=user_id, total=total, notes=notes, status="pending")
        self.session.add(order)
        # flush to get the order.id before creating items
        await self.session.flush()

        for item_data in items:
            item = OrderItem(
                order_id=order.id,
                product_id=item_data["product_id"],
                product_name=item_data["product_name"],
                unit_price=item_data["unit_price"],
                quantity=item_data["quantity"],
                subtotal=item_data["subtotal"],
            )
            self.session.add(item)

        await self.session.commit()
        await self.session.refresh(order)
        # Re-fetch with items loaded
        return await self.get_by_id(order.id)

    async def update_status(self, order: Order, status: str) -> Order:
        order.status = status
        await self.session.commit()
        await self.session.refresh(order)
        return order
