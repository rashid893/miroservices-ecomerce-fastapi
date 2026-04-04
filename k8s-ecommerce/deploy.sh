#!/usr/bin/env bash
# ==============================================================
# deploy.sh — Full production deployment script
# Usage: ./deploy.sh [--dry-run]
#
# Prerequisites:
#   - kubectl configured and pointing at your cluster
#   - Images built and pushed to your-registry
#   - Replace REGISTRY below with your Docker registry
# ==============================================================

set -euo pipefail

NAMESPACE="ecommerce"
DRY_RUN=${1:-""}
KUBECTL="kubectl"
[[ "$DRY_RUN" == "--dry-run" ]] && KUBECTL="kubectl --dry-run=client"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " 🚀 Deploying ecommerce microservices to K8s"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── Step 1: Namespace ────────────────────────────────────────
echo "▶ [1/9] Creating namespace..."
$KUBECTL apply -f 00-namespace/namespace.yaml

# ── Step 2: Secrets ──────────────────────────────────────────
echo "▶ [2/9] Applying secrets..."
$KUBECTL apply -f 01-secrets/secrets.yaml

# ── Step 3: ConfigMaps ───────────────────────────────────────
echo "▶ [3/9] Applying configmaps..."
$KUBECTL apply -f 02-configmaps/configmaps.yaml

# ── Step 4: Databases ────────────────────────────────────────
echo "▶ [4/9] Deploying PostgreSQL databases..."
$KUBECTL apply -f 03-databases/postgres.yaml

echo "   Waiting for databases to be ready..."
[[ "$DRY_RUN" == "" ]] && kubectl rollout status statefulset/auth-db -n $NAMESPACE --timeout=120s
[[ "$DRY_RUN" == "" ]] && kubectl rollout status statefulset/product-db -n $NAMESPACE --timeout=120s
[[ "$DRY_RUN" == "" ]] && kubectl rollout status statefulset/order-db -n $NAMESPACE --timeout=120s

# ── Step 5: Redis & RabbitMQ ─────────────────────────────────
echo "▶ [5/9] Deploying Redis..."
$KUBECTL apply -f 04-redis/redis.yaml

echo "▶ [5/9] Deploying RabbitMQ..."
$KUBECTL apply -f 05-rabbitmq/rabbitmq.yaml

# ── Step 6: Run DB Migrations ────────────────────────────────
echo "▶ [6/9] Running database migrations..."
$KUBECTL apply -f 10-jobs/migration-jobs.yaml

if [[ "$DRY_RUN" == "" ]]; then
  echo "   Waiting for migrations to complete..."
  kubectl wait --for=condition=complete job/auth-migrate    -n $NAMESPACE --timeout=180s
  kubectl wait --for=condition=complete job/product-migrate -n $NAMESPACE --timeout=180s
  kubectl wait --for=condition=complete job/order-migrate   -n $NAMESPACE --timeout=180s
  echo "   ✅ All migrations completed"
fi

# ── Step 7: Services ─────────────────────────────────────────
echo "▶ [7/9] Applying K8s Services..."
$KUBECTL apply -f 06-services/services.yaml

# ── Step 8: Deployments ──────────────────────────────────────
echo "▶ [8/9] Deploying microservices..."
$KUBECTL apply -f 07-deployments/auth-service.yaml
$KUBECTL apply -f 07-deployments/product-service.yaml
$KUBECTL apply -f 07-deployments/order-service.yaml
$KUBECTL apply -f 07-deployments/gateway-service.yaml

if [[ "$DRY_RUN" == "" ]]; then
  echo "   Waiting for rollouts..."
  kubectl rollout status deployment/auth-service    -n $NAMESPACE --timeout=180s
  kubectl rollout status deployment/product-service -n $NAMESPACE --timeout=180s
  kubectl rollout status deployment/order-service   -n $NAMESPACE --timeout=180s
  kubectl rollout status deployment/gateway-service -n $NAMESPACE --timeout=180s
fi

# ── Step 9: HPA & Ingress ────────────────────────────────────
echo "▶ [9/9] Applying HPA and Ingress..."
$KUBECTL apply -f 08-hpa/hpa.yaml
$KUBECTL apply -f 09-ingress/ingress.yaml

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " ✅ Deployment complete!"
echo ""
echo " Useful commands:"
echo "   kubectl get all -n $NAMESPACE"
echo "   kubectl get ingress -n $NAMESPACE"
echo "   kubectl logs -f deploy/gateway-service -n $NAMESPACE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
