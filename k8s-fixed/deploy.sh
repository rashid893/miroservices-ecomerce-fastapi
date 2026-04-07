#!/usr/bin/env bash
# ==============================================================
# deploy.sh — FIXED for docker-desktop / local K8s
# Usage: ./deploy.sh
# ==============================================================
set -euo pipefail

NS="ecommerce"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Deploying ecommerce microservices"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "[1/8] Namespace..."
kubectl apply -f 00-namespace/namespace.yaml

echo "[2/8] Secrets..."
kubectl apply -f 01-secrets/secrets.yaml

echo "[3/8] ConfigMaps..."
kubectl apply -f 02-configmaps/configmaps.yaml

echo "[4/8] Databases..."
kubectl apply -f 03-databases/postgres.yaml
echo "  Waiting for databases..."
kubectl rollout status deployment/auth-db    -n $NS --timeout=120s
kubectl rollout status deployment/product-db -n $NS --timeout=120s
kubectl rollout status deployment/order-db   -n $NS --timeout=120s

echo "[5/8] Redis & RabbitMQ..."
kubectl apply -f 04-redis/redis.yaml
kubectl apply -f 05-rabbitmq/rabbitmq.yaml

echo "[6/8] Running Alembic migrations..."
# Delete old completed/failed jobs first
kubectl delete jobs auth-migrate product-migrate order-migrate -n $NS --ignore-not-found
kubectl apply -f 10-jobs/migration-jobs.yaml

echo "  Waiting for migrations (up to 3 min)..."
kubectl wait --for=condition=complete job/auth-migrate    -n $NS --timeout=180s
kubectl wait --for=condition=complete job/product-migrate -n $NS --timeout=180s
kubectl wait --for=condition=complete job/order-migrate   -n $NS --timeout=180s
echo "  All migrations done!"

echo "[7/8] Services..."
kubectl apply -f 06-services/services.yaml

echo "[8/8] Deployments..."
kubectl apply -f 07-deployments/auth-service.yaml
kubectl apply -f 07-deployments/product-service.yaml
kubectl apply -f 07-deployments/order-service.yaml
kubectl apply -f 07-deployments/gateway-service.yaml

echo "  Waiting for rollouts..."
kubectl rollout status deployment/auth-service    -n $NS --timeout=180s
kubectl rollout status deployment/product-service -n $NS --timeout=180s
kubectl rollout status deployment/order-service   -n $NS --timeout=180s
kubectl rollout status deployment/gateway-service -n $NS --timeout=180s

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Done! Gateway available at: http://localhost:30000"
echo " Swagger docs:               http://localhost:30000/docs"
echo ""
echo " kubectl get all -n $NS"
echo " kubectl logs -f deploy/auth-service -n $NS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
