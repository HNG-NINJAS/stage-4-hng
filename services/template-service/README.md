# Template Service

Microservice for managing notification templates with multi-language support, version control, template rendering, and event-driven architecture.

## 🚀 Features

- ✅ **Template CRUD** - Create, read, update, delete templates
- ✅ **Variable Substitution** - Jinja2 rendering (e.g., `{{name}}` → `John`)
- ✅ **Multi-Language Support** - i18n with translations
- ✅ **Version History** - Automatic version tracking
- ✅ **Event Publishing** - RabbitMQ integration for async communication
- ✅ **Caching** - Redis caching for performance
- ✅ **Circuit Breaker** - Fault tolerance with pybreaker
- ✅ **Retry Logic** - Exponential backoff with tenacity
- ✅ **Health Checks** - Kubernetes-ready probes
- ✅ **Observability** - Prometheus metrics, structured logging
- ✅ **Snake Case API** - All endpoints follow snake_case convention
- ✅ **OpenAPI Docs** - Auto-generated Swagger documentation

## 📋 Requirements

- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (optional, for caching)
- RabbitMQ 3.12+ (optional, for events)

## 🏃 Quick Start

### Local Development
```bash
# Clone repository
cd services/template-service

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Start infrastructure (from repo root)
cd ../..
docker-compose up -d postgres_template redis rabbitmq

# Back to service directory
cd services/template-service

# Run database migrations
alembic upgrade head

# Seed sample templates
python scripts/seed_templates.py

# Start service
uvicorn app.main:app --reload --port 3004
```

### With Docker Compose (Recommended)
```bash
# From repo root
docker-compose up -d template-service

# Check logs
docker-compose logs -f template-service

# Stop
docker-compose stop template-service
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:3004/docs
- **ReDoc**: http://localhost:3004/redoc
- **Health Check**: http://localhost:3004/health
- **Metrics**: http://localhost:3004/metrics

## 🔌 API Endpoints

### Templates

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/templates` | Create template |
| GET | `/api/v1/templates` | List templates (paginated, filterable) |
| GET | `/api/v1/templates/{id}` | Get template by ID |
| PUT | `/api/v1/templates/{id}` | Update template (creates new version) |
| DELETE | `/api/v1/templates/{id}` | Soft delete template |
| POST | `/api/v1/templates/{id}/render` | Render template with data |
| POST | `/api/v1/templates/{id}/translations` | Add/update translation |
| GET | `/api/v1/templates/{id}/versions` | Get version history |
| GET | `/api/v1/templates/stats/summary` | Get statistics |

### Health & Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check (for load balancers) |
| GET | `/ready` | Readiness probe (Kubernetes) |
| GET | `/live` | Liveness probe (Kubernetes) |
| GET | `/metrics` | Prometheus metrics |

## 🎯 Example Usage

### Create Template
```bash
curl -X POST http://localhost:3004/api/v1/templates \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "welcome_email",
    "name": "Welcome Email",
    "type": "email",
    "subject": "Welcome {{name}} to {{company_name}}!",
    "body": "Hi {{name}},\n\nWelcome to {{company_name}}!",
    "language_code": "en"
  }'
```

### Render Template
```bash
curl -X POST http://localhost:3004/api/v1/templates/welcome_email/render \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "name": "John Doe",
      "company_name": "Acme Corp"
    },
    "language_code": "en"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "subject": "Welcome John Doe to Acme Corp!",
    "body": "Hi John Doe,\n\nWelcome to Acme Corp!",
    "variables_used": ["name", "company_name"]
  },
  "message": "Template rendered successfully",
  "meta": {...}
}
```

## 🌍 Multi-Language Support
```bash
# Add Spanish translation
curl -X POST http://localhost:3004/api/v1/templates/welcome_email/translations \
  -H "Content-Type: application/json" \
  -d '{
    "language_code": "es",
    "subject": "¡Bienvenido {{name}} a {{company_name}}!",
    "body": "Hola {{name}},\n\n¡Bienvenido a {{company_name}}!"
  }'

# Render in Spanish
curl -X POST http://localhost:3004/api/v1/templates/welcome_email/render \
  -H "Content-Type: application/json" \
  -d '{
    "data": {"name": "Juan", "company_name": "Acme Corp"},
    "language_code": "es"
  }'
```

## 📤 Event Publishing

Template Service publishes events to RabbitMQ for other services to consume:

### Published Events

| Event | Routing Key | Payload |
|-------|-------------|---------|
| Template Created | `template.created` | `{template_id, name, type, created_at}` |
| Template Updated | `template.updated` | `{template_id, name, updated_at}` |
| Template Deleted | `template.deleted` | `{template_id, deleted_at}` |

**Exchange**: `template.events` (topic)

### Example: Listening to Events (Other Services)
```python
import pika
import json

connection = pika.BlockingConnection(
    pika.URLParameters('amqp://admin:admin123@localhost:5672/')
)
channel = connection.channel()

# Bind to template events
channel.queue_declare(queue='my_service_queue', durable=True)
channel.queue_bind(
    queue='my_service_queue',
    exchange='template.events',
    routing_key='template.*'
)

def callback(ch, method, properties, body):
    event = json.loads(body)
    print(f"Received event: {method.routing_key}")
    print(f"Data: {event}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='my_service_queue', on_message_callback=callback)
channel.start_consuming()
```

## 🔧 Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | ✅ Yes |
| `REDIS_URL` | Redis connection string | - | ⚠️ Optional |
| `RABBITMQ_URL` | RabbitMQ connection string | - | ⚠️ Optional |
| `SERVICE_NAME` | Service name | `template-service` | No |
| `SERVICE_VERSION` | Service version | `1.0.0` | No |
| `PORT` | HTTP port | `3004` | No |
| `ENVIRONMENT` | Environment (dev/prod) | `development` | No |
| `DEBUG` | Debug mode | `True` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `CACHE_TTL` | Cache TTL in seconds | `300` | No |

## 📈 Monitoring & Observability

### Prometheus Metrics

Available at `/metrics`:

- `template_http_requests_total` - Total HTTP requests
- `template_http_request_duration_seconds` - Request duration
- `template_operations_total` - Template operations (create, update, delete, render)
- `template_render_duration_seconds` - Render duration by template_id
- `template_active_templates_total` - Current active templates count

### Structured Logging

JSON logs with correlation IDs for distributed tracing:
```json
{
  "timestamp": "2025-11-10T10:30:00Z",
  "level": "INFO",
  "service": "template-service",
  "message": "Template rendered successfully",
  "correlation_id": "abc-123",
  "template_id": "welcome_email",
  "duration_ms": 45.2
}
```

### Health Checks
```bash
# Health check (includes dependency status)
curl http://localhost:3004/health

# Readiness (for Kubernetes)
curl http://localhost:3004/ready

# Liveness (for Kubernetes)
curl http://localhost:3004/live
```

## 🗄️ Database

### Schema

- **templates** - Main template records
- **template_versions** - Version history (automatic)
- **template_translations** - Multi-language support

### Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View history
alembic history
```

## 🧪 Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_template_service.py -v

# Run only unit tests
pytest -m unit

# Run API integration tests
pytest tests/test_api.py -v

# View coverage report
open htmlcov/index.html
```

### Manual API Testing
```bash
# Seed sample templates
python scripts/seed_templates.py

# Test all endpoints
./scripts/test_api.sh
```

## 🐳 Docker

### Build Image
```bash
docker build -t template-service:1.0.0 .
```

### Run Container
```bash
docker run -d \
  --name template-service \
  -p 3004:3004 \
  -e DATABASE_URL=postgresql://admin:admin123@host.docker.internal:5432/template_service \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  -e RABBITMQ_URL=amqp://admin:admin123@host.docker.internal:5672/ \
  template-service:1.0.0
```

### Docker Compose (Production)
```bash
# Start all services
docker-compose up -d

# Scale template service
docker-compose up -d --scale template-service=3

# View logs
docker-compose logs -f template-service

# Stop services
docker-compose down
```

[Intergration guid →](./INTEGRATION.md)