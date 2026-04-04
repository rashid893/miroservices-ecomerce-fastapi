# 🚀 Kubernetes Production Manifests
## ecommerce-microservices (FastAPI)

Generated from your actual project structure. All env vars, ports, image
commands, and service names match the codebase exactly.

---

## 📁 Directory Structure

```
k8s-ecommerce/
├── 00-namespace/         Namespace: ecommerce
├── 01-secrets/           Secrets (DB URLs, JWT keys, passwords)
├── 02-configmaps/        Non-sensitive env vars per service
├── 03-databases/         PostgreSQL StatefulSets (auth-db, product-db, order-db)
├── 04-redis/             Redis StatefulSet (caching)
├── 05-rabbitmq/          RabbitMQ StatefulSet (messaging)
├── 06-services/          ClusterIP Services for all microservices
├── 07-deployments/       Deployments: auth, product, order, gateway
├── 08-hpa/               HorizontalPodAutoscalers (CPU/Memory based)
├── 09-ingress/           Nginx Ingress + TLS (cert-manager)
├── 10-jobs/              Alembic migration Jobs
├── deploy.sh             One-shot deployment script
└── README.md             This file
```

---

## 🔧 Before You Deploy

### 1. Build & Push Docker Images

```bash
# Replace `your-registry` with your actual Docker Hub / GCR / ECR path
REGISTRY=your-registry

docker build -t $REGISTRY/auth-service:latest    ./auth-service
docker build -t $REGISTRY/product-service:latest ./product-service
docker build -t $REGISTRY/order-service:latest   ./order-service
docker build -t $REGISTRY/gateway-service:latest ./gateway-service

docker push $REGISTRY/auth-service:latest
docker push $REGISTRY/product-service:latest
docker push $REGISTRY/order-service:latest
docker push $REGISTRY/gateway-service:latest
```

Then update the `image:` field in each `07-deployments/*.yaml` file.

### 2. Update Secrets

All secrets in `01-secrets/secrets.yaml` use base64-encoded placeholder values.
**Replace them before deploying to production.**

```bash
# Generate a secure JWT secret key
openssl rand -hex 32

# Encode a value for the secret YAML
echo -n "your-new-value" | base64
```

Critical secrets to change:
- `JWT_SECRET_KEY` in `auth-service-secret`, `product-service-secret`, `order-service-secret`
- All `POSTGRES_PASSWORD` values
- `DATABASE_URL` values (must match the passwords above)

### 3. Update Domain Names

In `09-ingress/ingress.yaml`, replace:
- `api.yourdomain.com` → your actual API domain
- `your-email@yourdomain.com` → your Let's Encrypt email

In `02-configmaps/configmaps.yaml`, replace:
- `ALLOWED_ORIGINS` with your frontend domain

### 4. Choose Storage Class

In `03-databases/postgres.yaml`, `04-redis/redis.yaml`, `05-rabbitmq/rabbitmq.yaml`:

| Cloud Provider | storageClassName |
|---|---|
| AWS EKS | `gp2` or `gp3` |
| GKE | `standard-rwo` or `premium-rwo` |
| Azure AKS | `managed-premium` |
| Local/minikube | `standard` (default) |

---

## 🚀 Deployment

### Prerequisites

```bash
# 1. metrics-server (for HPA)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# 2. nginx ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.1/deploy/static/provider/cloud/deploy.yaml

# 3. cert-manager (for TLS)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.4/cert-manager.yaml
```

### Deploy Everything

```bash
chmod +x deploy.sh
./deploy.sh

# Dry-run first (recommended)
./deploy.sh --dry-run
```

### Or deploy step by step

```bash
kubectl apply -f 00-namespace/
kubectl apply -f 01-secrets/
kubectl apply -f 02-configmaps/
kubectl apply -f 03-databases/
kubectl apply -f 04-redis/
kubectl apply -f 05-rabbitmq/

# Wait for DBs to be ready, then run migrations
kubectl apply -f 10-jobs/migration-jobs.yaml
kubectl wait --for=condition=complete job/auth-migrate    -n ecommerce --timeout=180s
kubectl wait --for=condition=complete job/product-migrate -n ecommerce --timeout=180s
kubectl wait --for=condition=complete job/order-migrate   -n ecommerce --timeout=180s

kubectl apply -f 06-services/
kubectl apply -f 07-deployments/
kubectl apply -f 08-hpa/
kubectl apply -f 09-ingress/
```

---

## 📡 Service Architecture

```
Internet
   │
   ▼
[Ingress: api.yourdomain.com]
   │
   ▼
[gateway-service :8000]  ──── proxies to ────►  [auth-service :8000]   ── auth-db (postgres)
                                            ──►  [product-service :8000] ── product-db (postgres)
                                            ──►  [order-service :8000]   ── order-db (postgres)
                                                          │
                                                    [redis :6379]
                                                    [rabbitmq :5672]
```

## 🔍 Verify Deployment

```bash
# Check all resources
kubectl get all -n ecommerce

# Check pod logs
kubectl logs -f deploy/auth-service    -n ecommerce
kubectl logs -f deploy/product-service -n ecommerce
kubectl logs -f deploy/order-service   -n ecommerce
kubectl logs -f deploy/gateway-service -n ecommerce

# Check HPA status
kubectl get hpa -n ecommerce

# Check ingress
kubectl get ingress -n ecommerce
kubectl describe ingress ecommerce-ingress -n ecommerce

# Port-forward gateway locally for testing
kubectl port-forward svc/gateway-service 8000:8000 -n ecommerce
# Then visit: http://localhost:8000/docs
```

## 🔄 Rolling Updates

```bash
# Update a service image
kubectl set image deployment/auth-service auth-service=your-registry/auth-service:v2 -n ecommerce
kubectl rollout status deployment/auth-service -n ecommerce

# Rollback if needed
kubectl rollout undo deployment/auth-service -n ecommerce
```

## 🧹 Teardown

```bash
# Delete all resources in namespace
kubectl delete namespace ecommerce

# Or selectively
kubectl delete -f 07-deployments/ -n ecommerce
```

---

## ⚠️ Production Checklist

- [ ] All secrets replaced with real values
- [ ] Images pushed to a private registry
- [ ] `imagePullSecrets` added to Deployments if using private registry
- [ ] Storage class updated for your cloud provider
- [ ] Domain names updated in Ingress and ConfigMaps
- [ ] cert-manager ClusterIssuer email updated
- [ ] `ALLOWED_ORIGINS` set to your real frontend domain
- [ ] Resource limits tuned for your actual workload
- [ ] Backups configured for PostgreSQL PersistentVolumes
- [ ] Network policies added (optional, for extra security)
- [ ] Monitoring set up (Prometheus + Grafana recommended)
