from fastapi import APIRouter, Request, Response
from core.config import settings
from services.proxy_service import proxy_request

router = APIRouter()

@router.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def auth_proxy(path: str, request: Request) -> Response:
    """Proxy all /api/v1/auth/* requests to auth-service."""
    return await proxy_request(request, settings.AUTH_SERVICE_URL)
