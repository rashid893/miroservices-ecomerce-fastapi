# Architecture Overview

## Services

| Service | Port | Responsibility |
|---------|------|----------------|
| gateway-service | 8000 | API gateway, request routing |
| auth-service | 8001 | Registration, login, JWT |
| product-service | 8002 | Product & category CRUD |
| order-service | 8003 | Order creation and management |

## Databases

Each service has its own isolated PostgreSQL database.
There are NO cross-service foreign keys or shared tables.

| DB | Port | Owner |
|----|------|-------|
| auth_db | 5433 | auth-service |
| product_db | 5434 | product-service |
| order_db | 5435 | order-service |

## Service Communication

- All client requests enter via **gateway-service** (port 8000)
- Gateway proxies to the correct downstream service via internal Docker network
- **order-service** calls **product-service** via HTTP to validate products
- JWT is validated independently by each service (shared secret)

## Token Flow

1. Client calls `POST /api/v1/auth/login`
2. Gets `access_token` + `refresh_token`
3. Sends `Authorization: Bearer <access_token>` on all protected endpoints
4. Each service validates the JWT locally (no round-trip to auth-service)
5. When access token expires, call `POST /api/v1/auth/refresh`

## Future Improvements

- Add RabbitMQ event publishing (e.g., `order.created` → decrement stock)
- Add Redis caching for product reads
- Add rate limiting in gateway
- Add distributed tracing (OpenTelemetry)
