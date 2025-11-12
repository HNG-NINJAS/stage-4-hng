# Deployment Guide

Guide for deploying Template Service to production.

## Docker Deployment

### Build Image

```bash
docker build -t template-service:1.0.0 .
```

### Run Container

```bash
docker run -d \
  --name template-service \
  -p 3004:3004 \
  -e DATABASE_URL=postgresql://admin:admin123@postgres:5432/template_service \
  -e REDIS_URL=redis://redis:6379/0 \
  -e RABBITMQ_URL=amqp://admin:admin123@rabbitmq:5672/ \
  -e ENVIRONMENT=production \
  -e DEBUG=False \
  -e LOG_LEVEL=INFO \
  template-service:1.0.0
```

### Docker Compose

```yaml
version: '3.8'

services:
  template-service:
    image: template-service:1.0.0
    ports:
      - "3004:3004"
    environment:
      DATABASE_URL: postgresql://admin:admin123@postgres:5432/template_service
      REDIS_URL: redis://redis:6379/0
      RABBITMQ_URL: amqp://admin:admin123@rabbitmq:5672/
      ENVIRONMENT: production
      DEBUG: "False"
      LOG_LEVEL: INFO
    depends_on:
      - postgres
      - redis
      - rabbitmq
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3004/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: template_service
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin123
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  rabbitmq:
    image: rabbitmq:3.12-management-alpine
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: admin123
    ports:
      - "15672:15672"
    restart: unless-stopped

volumes:
  postgres_data:
```

## Kubernetes Deployment

### Namespace

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: template-service
```

### ConfigMap

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: template-service-config
  namespace: template-service
data:
  SERVICE_NAME: "template-service"
  SERVICE_VERSION: "1.0.0"
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  PORT: "3004"
```

### Secret

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: template-service-secret
  namespace: template-service
type: Opaque
stringData:
  DATABASE_URL: "postgresql://admin:admin123@postgres:5432/template_service"
  REDIS_URL: "redis://redis:6379/0"
  RABBITMQ_URL: "amqp://admin:admin123@rabbitmq:5672/"
```

### Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: template-service
  namespace: template-service
  labels:
    app: template-service
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
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: template-service-secret
              key: DATABASE_URL
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: template-service-secret
              key: REDIS_URL
        - name: RABBITMQ_URL
          valueFrom:
            secretKeyRef:
              name: template-service-secret
              key: RABBITMQ_URL
        envFrom:
        - configMapRef:
            name: template-service-config
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
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 3004
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
```

### Service

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: template-service
  namespace: template-service
  labels:
    app: template-service
spec:
  type: ClusterIP
  ports:
  - port: 3004
    targetPort: 3004
    protocol: TCP
    name: http
  selector:
    app: template-service
```

### Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: template-service
  namespace: template-service
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - template-service.yourdomain.com
    secretName: template-service-tls
  rules:
  - host: template-service.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: template-service
            port:
              number: 3004
```

### HorizontalPodAutoscaler

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: template-service
  namespace: template-service
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: template-service
  minReplicas: 3
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
# Create namespace
kubectl apply -f namespace.yaml

# Create config and secrets
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml

# Deploy application
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml
kubectl apply -f hpa.yaml

# Check status
kubectl get pods -n template-service
kubectl get svc -n template-service
kubectl logs -f deployment/template-service -n template-service
```

## Database Migrations

### Run Migrations

```bash
# In production, run migrations before deploying new version
kubectl exec -it deployment/template-service -n template-service -- \
  alembic upgrade head
```

### Migration Job

```yaml
# migration-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: template-service-migration
  namespace: template-service
spec:
  template:
    spec:
      containers:
      - name: migration
        image: template-service:1.0.0
        command: ["alembic", "upgrade", "head"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: template-service-secret
              key: DATABASE_URL
      restartPolicy: OnFailure
  backoffLimit: 3
```

## Environment Variables

### Production Configuration

```env
# Service
SERVICE_NAME=template-service
SERVICE_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
PORT=3004

# Database
DATABASE_URL=postgresql://user:pass@postgres:5432/template_service

# Redis (optional)
REDIS_URL=redis://redis:6379/0
CACHE_TTL=300

# RabbitMQ (optional)
RABBITMQ_URL=amqp://user:pass@rabbitmq:5672/

# Security
ALLOWED_HOSTS=template-service.yourdomain.com
CORS_ORIGINS=https://yourdomain.com
```

## Scaling Considerations

### Horizontal Scaling

Template Service is stateless and can be scaled horizontally:

```bash
# Scale to 5 replicas
kubectl scale deployment template-service --replicas=5 -n template-service

# Or use HPA for auto-scaling
kubectl autoscale deployment template-service \
  --min=3 --max=10 --cpu-percent=70 \
  -n template-service
```

### Vertical Scaling

Adjust resource limits based on load:

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

## Load Balancing

### Nginx Configuration

```nginx
upstream template_service {
    least_conn;
    server template-service-1:3004;
    server template-service-2:3004;
    server template-service-3:3004;
}

server {
    listen 80;
    server_name template-service.yourdomain.com;

    location / {
        proxy_pass http://template_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Correlation-ID $request_id;
        
        # Timeouts
        proxy_connect_timeout 10s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    location /health {
        proxy_pass http://template_service/health;
        access_log off;
    }
}
```

## Backup & Recovery

### Database Backup

```bash
# Backup
kubectl exec -it postgres-0 -n template-service -- \
  pg_dump -U admin template_service > backup.sql

# Restore
kubectl exec -i postgres-0 -n template-service -- \
  psql -U admin template_service < backup.sql
```

### Automated Backups

```yaml
# backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: template-service-backup
  namespace: template-service
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15-alpine
            command:
            - /bin/sh
            - -c
            - |
              pg_dump -h postgres -U admin template_service | \
              gzip > /backup/template_service_$(date +%Y%m%d).sql.gz
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: template-service-secret
                  key: POSTGRES_PASSWORD
            volumeMounts:
            - name: backup
              mountPath: /backup
          volumes:
          - name: backup
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

## Rollback Strategy

### Kubernetes Rollback

```bash
# Check rollout history
kubectl rollout history deployment/template-service -n template-service

# Rollback to previous version
kubectl rollout undo deployment/template-service -n template-service

# Rollback to specific revision
kubectl rollout undo deployment/template-service --to-revision=2 -n template-service
```

### Blue-Green Deployment

```yaml
# Deploy new version (green)
kubectl apply -f deployment-green.yaml

# Test green deployment
kubectl port-forward deployment/template-service-green 3004:3004

# Switch traffic to green
kubectl patch service template-service -p '{"spec":{"selector":{"version":"green"}}}'

# Remove blue deployment
kubectl delete deployment template-service-blue
```

## Security

### Network Policies

```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: template-service
  namespace: template-service
spec:
  podSelector:
    matchLabels:
      app: template-service
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 3004
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 5432  # PostgreSQL
    - protocol: TCP
      port: 6379  # Redis
    - protocol: TCP
      port: 5672  # RabbitMQ
```

### Pod Security Policy

```yaml
# psp.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: template-service
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Secrets created securely
- [ ] Database migrations run
- [ ] Health checks configured
- [ ] Resource limits set
- [ ] HPA configured
- [ ] Monitoring enabled
- [ ] Logging configured
- [ ] Backup strategy in place
- [ ] Rollback plan documented
- [ ] Security policies applied
- [ ] Load testing completed
- [ ] Documentation updated

## Next Steps

- Configure [Monitoring](./monitoring.md)
- Review [Database Operations](./database.md)
- Set up [Integration](../integration/overview.md)
