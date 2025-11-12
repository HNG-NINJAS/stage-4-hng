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

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Set up environment
cp .env.example .env

# Run database migrations
alembic upgrade head

# Seed sample templates
python scripts/seed_templates.py

# Start service
uvicorn app.main:app --reload --port 3004
```

**With Docker Compose:**
```bash
docker-compose up -d template-service
```

## 📚 Documentation

Complete documentation is available in the `docs/` directory:

### Getting Started
- [Quick Start Guide](./docs/getting-started.md) - Setup and run the service
- [API Reference](./docs/api-reference.md) - Complete API documentation

### Integration Guides
- [Integration Overview](./docs/integration/overview.md) - Integration patterns and best practices
- [Python Client](./docs/integration/python-client.md) - Python/FastAPI integration
- [TypeScript/NestJS Client](./docs/integration/typescript-client.md) - Node.js/NestJS integration
- [C# Client](./docs/integration/csharp-client.md) - .NET integration
- [Event Streaming](./docs/integration/events.md) - RabbitMQ event integration

### Operations
- [Deployment](./docs/operations/deployment.md) - Docker and Kubernetes deployment
- [Monitoring](./docs/operations/monitoring.md) - Health checks, metrics, and logging
- [Database](./docs/operations/database.md) - Schema and migrations

## 🔌 Quick API Examples

### Render Template
```bash
curl -X POST http://localhost:3004/api/v1/templates/welcome_email/render \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "name": "John Doe",
      "company_name": "Acme Corp"
    }
  }'
```

### Create Template
```bash
curl -X POST http://localhost:3004/api/v1/templates \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "welcome_email",
    "name": "Welcome Email",
    "type": "email",
    "subject": "Welcome {{name}}!",
    "body": "Hi {{name}}, welcome to {{company_name}}!"
  }'
```

## 🌍 Multi-Language Support

```bash
# Add translation
curl -X POST http://localhost:3004/api/v1/templates/welcome_email/translations \
  -H "Content-Type: application/json" \
  -d '{
    "language_code": "es",
    "subject": "¡Bienvenido {{name}}!",
    "body": "Hola {{name}}, ¡bienvenido a {{company_name}}!"
  }'
```

## 📤 Event Publishing

Template Service publishes events to RabbitMQ:

| Event | Routing Key | When |
|-------|-------------|------|
| Template Created | `template.created` | New template created |
| Template Updated | `template.updated` | Template modified |
| Template Deleted | `template.deleted` | Template deleted |

See [Event Integration Guide](./docs/integration/events.md) for details.

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific tests
pytest tests/test_api.py -v
```

## 📊 Monitoring

- **Swagger UI**: http://localhost:3004/docs
- **Health Check**: http://localhost:3004/health
- **Metrics**: http://localhost:3004/metrics

## 🐳 Docker

```bash
# Build image
docker build -t template-service:1.0.0 .

# Run container
docker run -d -p 3004:3004 \
  -e DATABASE_URL=postgresql://admin:admin123@postgres:5432/template_service \
  template-service:1.0.0
```

## 📖 Additional Resources

- [Complete Documentation](./docs/README.md)
- [API Reference](./docs/api-reference.md)
- [Integration Examples](./docs/integration/overview.md)
- [Deployment Guide](./docs/operations/deployment.md)