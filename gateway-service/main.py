from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.auth_proxy import router as auth_router
from api.v1.product_proxy import router as product_router
from api.v1.order_proxy import router as order_router
from core.config import settings
from core.logging import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info(f"Starting {settings.SERVICE_NAME}")
    yield
    logger.info(f"Shutting down {settings.SERVICE_NAME}")

app = FastAPI(
    title="API Gateway",
    description="Single entry point — proxies to auth, product, and order services.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(product_router)
app.include_router(order_router)

@app.get("/api/v1/health", tags=["Health"])
async def health() -> dict:
    return {"status": "healthy", "service": settings.SERVICE_NAME}

@app.get("/", tags=["Root"])
async def root() -> dict:
    return {
        "service": "API Gateway",
        "routes": ["/api/v1/auth/*", "/api/v1/products/*", "/api/v1/categories/*", "/api/v1/orders/*"],
    }
