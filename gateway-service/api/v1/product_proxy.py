from fastapi import APIRouter, Request, Response
from core.config import settings
from services.proxy_service import proxy_request

router = APIRouter()

@router.api_route("/api/v1/products/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def product_proxy(path: str, request: Request) -> Response:
    return await proxy_request(request, settings.PRODUCT_SERVICE_URL)

@router.api_route("/api/v1/products", methods=["GET", "POST"])
async def product_proxy_root(request: Request) -> Response:
    return await proxy_request(request, settings.PRODUCT_SERVICE_URL)

@router.api_route("/api/v1/categories/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def category_proxy(path: str, request: Request) -> Response:
    return await proxy_request(request, settings.PRODUCT_SERVICE_URL)

@router.api_route("/api/v1/categories", methods=["GET", "POST"])
async def category_proxy_root(request: Request) -> Response:
    return await proxy_request(request, settings.PRODUCT_SERVICE_URL)
