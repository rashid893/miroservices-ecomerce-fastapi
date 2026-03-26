#!/bin/bash
# Run Alembic migrations for all services
# Usage: ./infrastructure/scripts/migrate_all.sh

set -e

echo "==> Migrating auth-service..."
docker compose exec auth-service alembic upgrade head

echo "==> Migrating product-service..."
docker compose exec product-service alembic upgrade head

echo "==> Migrating order-service..."
docker compose exec order-service alembic upgrade head

echo "All migrations complete!"
