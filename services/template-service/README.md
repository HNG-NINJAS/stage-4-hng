# Template Service

Microservice for managing notification templates with multi-language support and version control.

## Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements-dev.txt

# Set up environment
cp .env.example .env

# Run migrations
alembic upgrade head

# Start service
uvicorn app.main:app --reload --port 3004
```

### With Docker
```bash
# Build image
docker build -t template-service .

# Run container
docker run -p 3004:3004 --env-file .env template-service
```

## API Endpoints

- `POST /api/v1/templates` - Create template
- `GET /api/v1/templates` - List templates
- `GET /api/v1/templates/{template_id}` - Get template
- `PUT /api/v1/templates/{template_id}` - Update template
- `POST /api/v1/templates/{template_id}/render` - Render template
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

## Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_template_service.py -v
```

## Environment Variables

See `.env.example` for required configuration.

## Documentation

- API Docs: http://localhost:3004/docs
- Integration Guide: See `INTEGRATION.md`