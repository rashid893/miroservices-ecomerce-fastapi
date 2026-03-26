import uuid
from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from dependencies.auth import get_current_user_id, get_current_user_payload
from schemas.order import CreateOrderRequest, OrderResponse, UpdateOrderStatusRequest
from services.order_service import OrderService

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])
bearer_scheme = HTTPBearer()


def get_order_service(session: AsyncSession = Depends(get_db)) -> OrderService:
    return OrderService(session)


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(
    payload: CreateOrderRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_id: uuid.UUID = Depends(get_current_user_id),
    svc: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """Create a new order. Validates products with product-service."""
    authorization = f"Bearer {credentials.credentials}"
    return await svc.create_order(user_id=user_id, payload=payload, authorization=authorization)


@router.get("", response_model=list[OrderResponse])
async def list_orders(
    user_id: uuid.UUID = Depends(get_current_user_id),
    svc: OrderService = Depends(get_order_service),
) -> list[OrderResponse]:
    return await svc.list_orders(user_id)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    svc: OrderService = Depends(get_order_service),
) -> OrderResponse:
    return await svc.get_order(order_id, user_id)


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: uuid.UUID,
    payload: UpdateOrderStatusRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    svc: OrderService = Depends(get_order_service),
) -> OrderResponse:
    return await svc.update_status(order_id, payload, user_id)
