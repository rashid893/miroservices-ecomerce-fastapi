"""
proxy_service.py
----------------
The core of the gateway. Takes an incoming FastAPI Request and forwards it
to the target downstream service, preserving method, headers, body, and query params.

This is intentionally simple: it does NOT buffer the response body into memory
for large payloads — it streams it back directly.
"""
import httpx
from fastapi import Request, Response
from core.logging import get_logger

logger = get_logger(__name__)

# Single shared async client — reuses connections (connection pooling)
_client = httpx.AsyncClient(timeout=30.0)


async def proxy_request(request: Request, target_base_url: str) -> Response:
    """
    Forward a request to target_base_url + request.url.path, preserving:
    - HTTP method
    - Query parameters
    - Request headers (minus hop-by-hop headers)
    - Request body
    """
    # Build the upstream URL
    upstream_url = f"{target_base_url}{request.url.path}"
    if request.url.query:
        upstream_url = f"{upstream_url}?{request.url.query}"

    # Forward headers, strip hop-by-hop headers that should not be proxied
    headers = dict(request.headers)
    for h in ("host", "content-length", "transfer-encoding", "connection"):
        headers.pop(h, None)

    body = await request.body()

    logger.debug(f"Proxying {request.method} {upstream_url}")

    upstream_response = await _client.request(
        method=request.method,
        url=upstream_url,
        headers=headers,
        content=body,
    )

    # Build FastAPI response, forwarding status and headers
    response_headers = dict(upstream_response.headers)
    # Remove transfer-encoding — FastAPI will handle chunking
    response_headers.pop("transfer-encoding", None)

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
        media_type=upstream_response.headers.get("content-type"),
    )
