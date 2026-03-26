# E-Commerce Microservices Backend

Production-style FastAPI + PostgreSQL microservices project.

## Architecture

```
Client → gateway-service (8000)
              ├── /api/v1/auth/*      → auth-service (8001)
              ├── /api/v1/products/*  → product-service (8002)
              ├── /api/v1/categories/* → product-service (8002)
              └── /api/v1/orders/*   → order-service (8003)
```

## Quick Start

### 1. Prerequisites
- Docker Desktop installed and running
- Docker Compose v2+

### 2. Clone and configure
```bash
git clone <your-repo>
cd ecommerce-microservices
# .env files are pre-filled for local dev — change secrets for production!
```

### 3. Start all services
```bash
docker compose up --build
```

### 4. Verify health
```bash
curl http://localhost:8000/api/v1/health   # gateway
curl http://localhost:8001/api/v1/health   # auth
curl http://localhost:8002/api/v1/health   # product
curl http://localhost:8003/api/v1/health   # order
```

---

## Running Migrations Manually

Migrations run automatically on container startup. To run manually:

```bash
docker compose exec auth-service alembic upgrade head
docker compose exec product-service alembic upgrade head
docker compose exec order-service alembic upgrade head
```

---

## Service URLs

| Service | Local URL | Swagger Docs |
|---------|-----------|--------------|
| Gateway | http://localhost:8000 | http://localhost:8000/docs |
| Auth | http://localhost:8001 | http://localhost:8001/docs |
| Product | http://localhost:8002 | http://localhost:8002/docs |
| Order | http://localhost:8003 | http://localhost:8003/docs |
| RabbitMQ UI | http://localhost:15672 | guest/guest |

---

## API Endpoints

### Auth Service
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/v1/auth/register | ❌ | Register new user |
| POST | /api/v1/auth/login | ❌ | Login, get tokens |
| POST | /api/v1/auth/refresh | ❌ | Refresh access token |
| GET | /api/v1/auth/me | ✅ | Get current user |

### Product Service
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/v1/categories | ✅ Admin | Create category |
| GET | /api/v1/categories | ❌ | List categories |
| POST | /api/v1/products | ✅ Admin | Create product |
| GET | /api/v1/products | ❌ | List products (paginated) |
| GET | /api/v1/products/{id} | ❌ | Get product detail |
| PUT | /api/v1/products/{id} | ✅ Admin | Update product |
| DELETE | /api/v1/products/{id} | ✅ Admin | Delete product |

### Order Service
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/v1/orders | ✅ | Create order |
| GET | /api/v1/orders | ✅ | List my orders |
| GET | /api/v1/orders/{id} | ✅ | Get order detail |
| PATCH | /api/v1/orders/{id}/status | ✅ | Update order status |

---

## Example cURL Commands

> All examples go through the **gateway on port 8000**.

### Register
```bash
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Password123","full_name":"Jane Doe"}' \
  | python3 -m json.tool
```

### Login
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Password123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo $TOKEN
```

### Get current user
```bash
curl -s http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Create admin user (promote in DB after register)
```bash
# Register first, then:
docker compose exec auth-db psql -U auth_user -d auth_db \
  -c "UPDATE users SET role='admin' WHERE email='admin@example.com';"
```

### Create a category (admin only)
```bash
curl -s -X POST http://localhost:8000/api/v1/categories \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Electronics","description":"Electronic gadgets"}' \
  | python3 -m json.tool
```

### Create a product (admin only)
```bash
curl -s -X POST http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Wireless Headphones",
    "description": "Noise cancelling over-ear headphones",
    "price": "79.99",
    "stock": 100,
    "is_active": true
  }' | python3 -m json.tool
```

### List products
```bash
curl -s "http://localhost:8000/api/v1/products?page=1&page_size=10" | python3 -m json.tool
```

### Create an order
```bash
curl -s -X POST http://localhost:8000/api/v1/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"product_id": "<product-uuid>", "quantity": 2}
    ]
  }' | python3 -m json.tool
```

### Update order status
```bash
curl -s -X PATCH http://localhost:8000/api/v1/orders/<order-uuid>/status \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "paid"}' | python3 -m json.tool
```

---

## Project Structure

```
ecommerce-microservices/
├── gateway-service/          # API gateway (proxies all requests)
├── auth-service/             # Auth: register, login, JWT
├── product-service/          # Products and categories CRUD
├── order-service/            # Orders (calls product-service)
├── shared/                   # Reference schemas, event definitions
│   ├── schemas/
│   ├── events/
│   ├── security/
│   └── utils/
├── infrastructure/
│   ├── nginx/                # Optional nginx config
│   ├── scripts/              # Helper shell scripts
│   └── docs/                 # Architecture docs
├── docker-compose.yml
├── .env
└── README.md
```

## Each service follows clean architecture:
```
<service>/
├── api/v1/           # FastAPI route handlers
├── core/             # config, logging, exceptions
├── db/               # SQLAlchemy models, session, base
├── schemas/          # Pydantic request/response models
├── repositories/     # Database query layer
├── services/         # Business logic layer
├── dependencies/     # FastAPI dependency injection
├── utils/            # Helpers (security, http client)
├── alembic/          # Database migrations
├── main.py           # FastAPI app entrypoint
├── Dockerfile
├── requirements.txt
└── .env
```

---

## Stopping and Cleaning Up

```bash
# Stop all containers
docker compose down

# Stop and remove volumes (wipes all databases)
docker compose down -v
```
