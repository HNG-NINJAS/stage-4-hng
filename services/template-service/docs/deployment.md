# Deployment Guide

> **Production deployment guide for Template Service**

## Prerequisites

- Docker 20.10+
- Kubernetes 1.24+ (for K8s deployment)
- PostgreSQL 15+
- Redis 7+ (optional)
- RabbitMQ 3.12+ (optional)

## Environment Variables

### Required

```bash
DATABASE_URL=postgresql://user:password@postgres:5432/template_db
PORT=3004
```

### Optional

```bash
# Redis (caching)
REDIS_URL=redis://redis:6379/0

# RabbitMQ (events)
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# Logging
LOG_LEVEL=INFO

# Performance
WORKERS=4
```

## Docker Deployment

### 1. Build Image

```bash
docker build -t template-service:1.0.0 .
```

### 2. Run with Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  template-service:
    image: template-service:1.0.0
    ports:
      - "3004:3004"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/template_db
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
    depends_on:
      - postgres
      - redis
      - rabbitmq
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3004/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=template_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  rabbitmq:
    image: rabbitmq:3.12-management-alpine
    ports:
      - "15672:15672"
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq

volumes:
  postgres_data:
  redis_data:
  rabbitmq_data:
```

```bash
docker-compose up -d
```

## Kubernetes Deployment

### 1. ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: template-service-config
  namespace: default
data:
  PORT: "3004"
  LOG_LEVEL: "INFO"
  WORKERS: "4"
```

### 2. Secret

```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: template-service-secret
  namespace: default
type: Opaque
stringData:
  DATABASE_URL: postgresql://user:password@postgres.default.svc.cluster.local:5432/template_db
  REDIS_URL: redis://redis.default.svc.cluster.local:6379/0
  RABBITMQ_URL: amqp://guest:guest@rabbitmq.default.svc.cluster.local:5672/
```

### 3. Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: template-service
  namespace: default
spec:
  replicas: 3
  selector:
    matchLabels:
      app: template-service
  template:
    metadata:
      labels:
        app: template-service
    spec:
      containers:
      - name: template-service
        image: template-service:1.0.0
        ports:
        - containerPort: 3004
        envFrom:
        - configMapRef:
            name: template-service-config
        - secretRef:
            name: template-service-secret
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /live
            port: 3004
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3004
          initialDelaySeconds: 10
          periodSeconds: 5
```

### 4. Service

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: template-service
  namespace: default
spec:
  selector:
    app: template-service
  ports:
  - protocol: TCP
    port: 3004
    targetPort: 3004
  type: ClusterIP
```

### 5. HorizontalPodAutoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: template-service-hpa
  namespace: default
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: template-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Deploy to Kubernetes

```bash
kubectl apply -f k8s/
```

## Database Migrations

### Initial Setup

```bash
# Run migrations
alembic upgrade head

# Seed templates (optional)
python scripts/seed_templates.py
```

### In Production

```bash
# Create migration job
kubectl create job --from=cronjob/db-migrate db-migrate-$(date +%s)
```

Or use init container:

```yaml
initContainers:
- name: db-migrate
  image: template-service:1.0.0
  command: ["alembic", "upgrade", "head"]
  envFrom:
  - secretRef:
      name: template-service-secret
```

## Monitoring

### Prometheus

```yaml
# prometheus-config.yaml
scrape_configs:
  - job_name: 'template-service'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: template-service
      - source_labels: [__meta_kubernetes_pod_ip]
        action: replace
        target_label: __address__
        replacement: $1:3004
```

### Grafana Dashboard

Import dashboard from `monitoring/grafana-dashboard.json`

Key metrics:
- Request rate
- Error rate
- Response time (p50, p95, p99)
- Template render time
- Cache hit rate
- Database connection pool

## Logging

### Structured Logging

Logs are JSON formatted for easy parsing:

```json
{
  "timestamp": "2025-11-10T10:30:00Z",
  "level": "INFO",
  "service": "template-service",
  "correlation_id": "abc-123",
  "message": "Template rendered",
  "template_id": "welcome_email",
  "duration_ms": 23.5
}
```

### Log Aggregation

**ELK Stack:**
```yaml
# filebeat.yaml
filebeat.inputs:
- type: container
  paths:
    - '/var/log/containers/*template-service*.log'
  json.keys_under_root: true
  json.add_error_key: true
```

**Loki:**
```yaml
# promtail-config.yaml
scrape_configs:
- job_name: kubernetes-pods
  kubernetes_sd_configs:
  - role: pod
  relabel_configs:
  - source_labels: [__meta_kubernetes_pod_label_app]
    action: keep
    regex: template-service
```

## Backup & Recovery

### Database Backup

```bash
# Automated backup
kubectl create cronjob db-backup \
  --image=postgres:15-alpine \
  --schedule="0 2 * * *" \
  -- pg_dump $DATABASE_URL > /backup/template_db_$(date +%Y%m%d).sql
```

### Disaster Recovery

1. Restore database from backup
2. Run migrations: `alembic upgrade head`
3. Verify health: `curl http://service/health`
4. Reseed if needed: `python scripts/seed_templates.py`

## Security

### Network Policies

```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: template-service-policy
spec:
  podSelector:
    matchLabels:
      app: template-service
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: email-service
    - podSelector:
        matchLabels:
          app: notification-service
    ports:
    - protocol: TCP
      port: 3004
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

### Secrets Management

Use external secret managers:

```yaml
# Using External Secrets Operator
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: template-service-secret
spec:
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: template-service-secret
  data:
  - secretKey: DATABASE_URL
    remoteRef:
      key: prod/template-service/database-url
```

## Performance Tuning

### Database Connection Pool

```python
# app/config.py
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 10
SQLALCHEMY_POOL_TIMEOUT = 30
SQLALCHEMY_POOL_RECYCLE = 3600
```

### Redis Caching

```python
# Cache rendered templates for 5 minutes
CACHE_TTL = 300
```

### Gunicorn Workers

```bash
# Calculate workers: (2 x CPU cores) + 1
gunicorn app.main:app \
  --workers 9 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:3004
```

## Troubleshooting

### Check Logs

```bash
# Kubernetes
kubectl logs -f deployment/template-service

# Docker
docker-compose logs -f template-service
```

### Database Connection Issues

```bash
# Test connection
kubectl exec -it deployment/template-service -- \
  python -c "from app.database import engine; engine.connect()"
```

### Health Check Failing

```bash
# Check dependencies
curl http://localhost:3004/health | jq '.data.dependencies'
```

### High Memory Usage

```bash
# Check metrics
kubectl top pod -l app=template-service

# Adjust resources in deployment
kubectl set resources deployment template-service \
  --limits=memory=1Gi \
  --requests=memory=512Mi
```

## Rollback

```bash
# Kubernetes
kubectl rollout undo deployment/template-service

# Docker Compose
docker-compose down
docker-compose up -d --force-recreate
```

## Production Checklist

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Logging aggregation setup
- [ ] Backup strategy in place
- [ ] Security policies applied
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Runbook created
