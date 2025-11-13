# Getting Started

This guide will help you set up and run the Template Service locally.

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (optional, for caching)
- RabbitMQ 3.12+ (optional, for events)

## Local Development Setup

### 1. Clone and Navigate
```bash
cd services/template-service
```

### 2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements-dev.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

**Required environment variables:**
```env
DATABASE_URL=postgresql://admin:admin123@localhost:5432/template_service
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://admin:admin123@localhost:5672/
```

### 5. Start Infrastructure
```bash
# From repo root
cd ../..
docker-compose up -d postgres_template redis rabbitmq

# Back to service directory
cd services/template-service
```

### 6. Run Database Migrations
```bash
alembic upgrade head
```

### 7. Seed Sample Templates
```bash
python scripts/seed_templates.py
```

### 8. Start Service
```bash
uvicorn app.main:app --reload --port 3004
```

The service will be available at http://localhost:3004

## Docker Setup (Recommended)

### Using Docker Compose
```bash
# From repo root
docker-compose up -d template-service

# Check logs
docker-compose logs -f template-service

# Stop
docker-compose stop template-service
```

### Build Docker Image
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

## Verify Installation

### Check Health
```bash
curl http://localhost:3004/health
```

**Expected response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "template-service",
    "version": "1.0.0"
  }
}
```

### View API Documentation
Open http://localhost:3004/docs in your browser

### Test Template Rendering
```bash
curl -X POST http://localhost:3004/api/v1/templates/welcome_email/render \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "name": "John Doe",
      "company_name": "Acme Corp",
      "verification_link": "https://example.com/verify/123"
    }
  }'
```

## Available Templates

After seeding, these templates are available:

| Template ID | Type | Description |
|------------|------|-------------|
| `welcome_email` | email | Welcome new users |
| `password_reset` | email | Password reset |
| `order_confirmation` | email | Order confirmation |
| `order_shipped` | push | Order shipped notification |
| `promotional_offer` | email | Marketing promotion |
| `account_alert` | push | Security alert |
| `payment_received` | email | Payment confirmation |
| `subscription_reminder` | email | Subscription renewal |
| `new_message` | push | New message notification |
| `account_verification` | email | Email verification |

## Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Run Specific Tests
```bash
pytest tests/test_api.py -v
```

### Manual API Testing
```bash
./scripts/test_api.sh
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `REDIS_URL` | Redis connection string | - | Optional |
| `RABBITMQ_URL` | RabbitMQ connection string | - | Optional |
| `SERVICE_NAME` | Service name | `template-service` | No |
| `SERVICE_VERSION` | Service version | `1.0.0` | No |
| `PORT` | HTTP port | `3004` | No |
| `ENVIRONMENT` | Environment (dev/prod) | `development` | No |
| `DEBUG` | Debug mode | `True` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `CACHE_TTL` | Cache TTL in seconds | `300` | No |

## Next Steps

- Review the [API Reference](./api-reference.md) for complete endpoint documentation
- Explore [Integration Guides](./integration/overview.md) to integrate with your services
- Check [Code Examples](./examples/README.md) for ready-to-use client implementations
- Read [Development Guide](./development.md) if you plan to contribute
- Set up [Monitoring](./operations/monitoring.md) for production deployments
