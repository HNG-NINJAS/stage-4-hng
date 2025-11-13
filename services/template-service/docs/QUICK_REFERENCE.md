# Quick Reference Guide

> **Fast lookup for common Template Service operations**

## 🚀 Quick Start

```bash
# Start service locally
docker-compose up -d template-service

# Check health
curl http://localhost:3004/health

# View API docs
open http://localhost:3004/docs
```

## 📡 API Endpoints

### Base URL
```
Local:      http://localhost:3004
Docker:     http://template-service:3004
Production: https://your-domain.com
```

### Core Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/v1/templates` | Create template |
| `GET` | `/api/v1/templates/{id}` | Get template |
| `GET` | `/api/v1/templates` | List templates |
| `PUT` | `/api/v1/templates/{id}` | Update template |
| `DELETE` | `/api/v1/templates/{id}` | Delete template |
| `POST` | `/api/v1/templates/{id}/render` | Render template |
| `POST` | `/api/v1/templates/{id}/translations` | Add translation |
| `GET` | `/health` | Health check |
| `GET` | `/metrics` | Prometheus metrics |

## 💻 Code Snippets

### Python

```python
import requests

# Render template
response = requests.post(
    "http://template-service:3004/api/v1/templates/welcome_email/render",
    json={"data": {"name": "John", "company_name": "Acme"}}
)
rendered = response.json()["data"]
print(rendered["subject"])  # "Welcome John to Acme!"
```

### TypeScript/Node.js

```typescript
import axios from 'axios';

// Render template
const response = await axios.post(
  'http://template-service:3004/api/v1/templates/welcome_email/render',
  { data: { name: 'John', company_name: 'Acme' } }
);
const rendered = response.data.data;
console.log(rendered.subject);  // "Welcome John to Acme!"
```

### C#

```csharp
using System.Net.Http;

// Render template
var client = new HttpClient();
var response = await client.PostAsJsonAsync(
    "http://template-service:3004/api/v1/templates/welcome_email/render",
    new { data = new { name = "John", company_name = "Acme" } }
);
var rendered = await response.Content.ReadFromJsonAsync<ApiResponse>();
Console.WriteLine(rendered.Data.Subject);  // "Welcome John to Acme!"
```

### cURL

```bash
# Render template
curl -X POST http://localhost:3004/api/v1/templates/welcome_email/render \
  -H "Content-Type: application/json" \
  -d '{"data": {"name": "John", "company_name": "Acme"}}'

# Create template
curl -X POST http://localhost:3004/api/v1/templates \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "welcome_email",
    "name": "Welcome Email",
    "type": "email",
    "subject": "Welcome {{name}}!",
    "body": "Hi {{name}}, welcome to {{company_name}}!"
  }'

# Get template
curl http://localhost:3004/api/v1/templates/welcome_email

# List templates
curl "http://localhost:3004/api/v1/templates?type=email&limit=10"

# Health check
curl http://localhost:3004/health
```

## 🐳 Docker Commands

```bash
# Build image
docker build -t template-service:1.0.0 .

# Run container
docker run -d -p 3004:3004 \
  -e DATABASE_URL=postgresql://user:pass@postgres:5432/template_db \
  template-service:1.0.0

# Docker Compose
docker-compose up -d template-service
docker-compose logs -f template-service
docker-compose stop template-service
docker-compose down
```

## ☸️ Kubernetes Commands

```bash
# Deploy
kubectl apply -f k8s/

# Check status
kubectl get pods -l app=template-service
kubectl get svc template-service
kubectl describe deployment template-service

# View logs
kubectl logs -f deployment/template-service
kubectl logs -f deployment/template-service --tail=100

# Scale
kubectl scale deployment template-service --replicas=5

# Rollback
kubectl rollout undo deployment/template-service

# Port forward (for testing)
kubectl port-forward svc/template-service 3004:3004
```

## 🗄️ Database Commands

```bash
# Run migrations
alembic upgrade head

# Create migration
alembic revision --autogenerate -m "Add new column"

# Rollback migration
alembic downgrade -1

# View migration history
alembic history

# Backup database
pg_dump -h localhost -U admin template_service > backup.sql

# Restore database
psql -h localhost -U admin template_service < backup.sql
```

## 🧪 Testing Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::test_create_template -v

# Run integration tests only
pytest -m integration
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:3004/health | jq
```

### Metrics
```bash
curl http://localhost:3004/metrics
```

### Prometheus Queries
```promql
# Request rate
rate(template_http_requests_total[5m])

# Error rate
rate(template_http_requests_total{status=~"5.."}[5m])

# P95 latency
histogram_quantile(0.95, rate(template_http_request_duration_seconds_bucket[5m]))

# Cache hit rate
rate(template_cache_hits_total[5m]) / 
(rate(template_cache_hits_total[5m]) + rate(template_cache_misses_total[5m]))
```

## 🔧 Troubleshooting

### Service won't start
```bash
# Check logs
docker-compose logs template-service

# Check database connection
docker-compose exec template-service python -c "from app.database import engine; engine.connect()"

# Check environment variables
docker-compose exec template-service env | grep DATABASE_URL
```

### Database connection error
```bash
# Test PostgreSQL connection
psql $DATABASE_URL

# Check if PostgreSQL is running
docker-compose ps postgres_template

# Restart PostgreSQL
docker-compose restart postgres_template
```

### Migration issues
```bash
# Check current version
alembic current

# Show migration history
alembic history

# Downgrade to specific version
alembic downgrade <revision>

# Force upgrade
alembic upgrade head
```

### High memory usage
```bash
# Check container stats
docker stats template-service

# Check Kubernetes pod resources
kubectl top pod -l app=template-service

# Increase memory limit
kubectl set resources deployment template-service --limits=memory=1Gi
```

## 🔐 Environment Variables

### Required
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
```

### Optional
```bash
REDIS_URL=redis://redis:6379/0
RABBITMQ_URL=amqp://user:pass@rabbitmq:5672/
LOG_LEVEL=INFO
PORT=3004
CACHE_TTL=300
```

## 📝 Response Format

All API responses follow this structure:

```json
{
  "success": true,
  "data": { /* response data */ },
  "error": null,
  "message": "Operation successful",
  "meta": {
    "total": 100,
    "limit": 10,
    "page": 1,
    "total_pages": 10,
    "has_next": true,
    "has_previous": false
  }
}
```

## 🎯 Common Use Cases

### Send Welcome Email
```python
# 1. Render template
rendered = client.render_template(
    "welcome_email",
    {"name": "John", "company_name": "Acme", "verification_link": "https://..."}
)

# 2. Send email
send_email(
    to="john@example.com",
    subject=rendered["subject"],
    body=rendered["body"]
)
```

### Multi-language Support
```python
# Render in Spanish
rendered = client.render_template(
    "welcome_email",
    {"name": "Juan", "company_name": "Acme"},
    language_code="es"
)
```

### Cache Invalidation (via Events)
```python
# Subscribe to template.updated events
def on_template_updated(event):
    template_id = event["template_id"]
    cache.delete(f"template:{template_id}:*")
```

## 📚 More Information

- **Complete API Reference**: [api-reference.md](./api-reference.md)
- **Integration Guides**: [integration/overview.md](./integration/overview.md)
- **Deployment Guide**: [operations/deployment.md](./operations/deployment.md)
- **Full Documentation**: [INDEX.md](./INDEX.md)

---

**Pro Tip**: Bookmark this page for quick access to common commands and snippets!
