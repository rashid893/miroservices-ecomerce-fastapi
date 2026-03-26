import httpx
from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)

async def get_product(product_id: str, authorization: str | None = None) -> dict | None:
    """
    Call the product-service to fetch a single product by ID.
    Returns the product dict or None if not found.
    Raises httpx.HTTPError on network failures.
    """
    headers = {}
    if authorization:
        headers["Authorization"] = authorization

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{settings.PRODUCT_SERVICE_URL}/api/v1/products/{product_id}",
                headers=headers,
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            logger.error(f"Network error calling product-service: {exc}")
            raise
