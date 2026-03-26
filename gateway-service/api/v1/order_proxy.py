from fastapi import APIRouter, Request, Response
from core.config import settings
from services.proxy_service import proxy_request

router = APIRouter()

@router.api_route("/api/v1/orders/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def order_proxy(path: str, request: Request) -> Response:
    return await proxy_request(request, settings.ORDER_SERVICE_URL)

@router.api_route("/api/v1/orders", methods=["GET", "POST"])
async def order_proxy_root(request: Request) -> Response:
    return await proxy_request(request, settings.ORDER_SERVICE_URL)
