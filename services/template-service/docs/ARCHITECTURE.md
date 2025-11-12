# Template Service Architecture

> **System architecture and design overview**

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Services                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Email Service│  │Notification  │  │  SMS Service │          │
│  │              │  │   Service    │  │              │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                  │                   │
│         └─────────────────┼──────────────────┘                   │
│                           │ HTTP/REST                            │
└───────────────────────────┼──────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Template Service (FastAPI)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                     API Layer                             │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │  │
│  │  │ Templates  │  │   Health   │  │  Metrics   │         │  │
│  │  │  Endpoints │  │   Checks   │  │            │         │  │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘         │  │
│  └────────┼───────────────┼───────────────┼────────────────┘  │
│           │               │               │                    │
│  ┌────────▼───────────────▼───────────────▼────────────────┐  │
│  │                  Service Layer                           │  │
│  │  ┌──────────────────────────────────────────────────┐   │  │
│  │  │         TemplateService (Business Logic)         │   │  │
│  │  │  • CRUD Operations                               │   │  │
│  │  │  • Version Management                            │   │  │
│  │  │  • Translation Handling                          │   │  │
│  │  │  • Event Publishing                              │   │  │
│  │  └──────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│           │               │               │                    │
│  ┌────────▼───────┐  ┌───▼────────┐  ┌──▼─────────┐          │
│  │   Renderer     │  │   Cache    │  │  RabbitMQ  │          │
│  │   (Jinja2)     │  │  (Redis)   │  │  Publisher │          │
│  └────────────────┘  └────────────┘  └────────────┘          │
│           │                                                     │
│  ┌────────▼─────────────────────────────────────────────────┐ │
│  │              Database Layer (SQLAlchemy)                  │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │ │
│  │  │Templates │  │ Versions │  │Translation│               │ │
│  │  │  Model   │  │  Model   │  │   Model   │               │ │
│  │  └──────────┘  └──────────┘  └──────────┘               │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │    Redis     │    │  RabbitMQ    │
│   Database   │    │    Cache     │    │   Events     │
└──────────────┘    └──────────────┘    └──────────────┘
```

## Component Details

### API Layer
- **FastAPI Framework**: High-performance async API
- **OpenAPI/Swagger**: Auto-generated documentation
- **Pydantic**: Request/response validation
- **CORS**: Cross-origin support

### Service Layer
- **TemplateService**: Core business logic
- **Version Control**: Automatic versioning on changes
- **Event Publishing**: RabbitMQ integration
- **Caching**: Redis for performance

### Data Layer
- **SQLAlchemy ORM**: Database abstraction
- **Alembic**: Database migrations
- **PostgreSQL**: Primary data store
- **Redis**: Caching layer

### Utilities
- **Jinja2 Renderer**: Template variable substitution
- **Circuit Breaker**: Fault tolerance (pybreaker)
- **Metrics**: Prometheus-compatible metrics
- **Logging**: Structured JSON logging

## Data Flow

### Template Rendering Flow

```
1. Client Request
   │
   ├─→ POST /api/v1/templates/{template_id}/render
   │   Body: {"data": {"name": "John"}, "language_code": "en"}
   │
2. API Layer (templates.py)
   │
   ├─→ Validate request (Pydantic schema)
   │
3. Service Layer (template_service.py)
   │
   ├─→ Check Redis cache
   │   ├─ Cache hit → Return cached result
   │   └─ Cache miss → Continue
   │
   ├─→ Query database for template
   │   └─ Get template + current version + translation
   │
4. Renderer (renderer.py)
   │
   ├─→ Render with Jinja2
   │   ├─ Subject: "Welcome {{name}}" → "Welcome John"
   │   └─ Body: "Hi {{name}}!" → "Hi John!"
   │
5. Cache & Return
   │
   ├─→ Store in Redis (TTL: 5 min)
   └─→ Return to client
```

### Template Creation Flow

```
1. Client Request
   │
   ├─→ POST /api/v1/templates
   │   Body: {template_id, name, type, subject, body, ...}
   │
2. API Layer
   │
   ├─→ Validate request
   │
3. Service Layer
   │
   ├─→ Check if template_id exists
   │   └─ If exists → Return error
   │
   ├─→ Create template record
   │
   ├─→ Create initial version (1.0.0)
   │
   ├─→ Publish event to RabbitMQ
   │   └─ Exchange: template.events
   │       Routing Key: template.created
   │       Payload: {template_id, name, type, created_at}
   │
4. Database
   │
   ├─→ Insert into templates table
   ├─→ Insert into template_versions table
   └─→ Commit transaction
   │
5. Return Response
   └─→ Return created template with version
```

## Database Schema

```sql
-- Templates table
CREATE TABLE templates (
    id UUID PRIMARY KEY,
    template_id VARCHAR(255) UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Template versions table
CREATE TABLE template_versions (
    id UUID PRIMARY KEY,
    template_id UUID REFERENCES templates(id),
    version VARCHAR(20) NOT NULL,
    subject TEXT,
    body TEXT NOT NULL,
    language_code VARCHAR(10) DEFAULT 'en',
    variables JSONB,
    template_metadata JSONB,
    is_current BOOLEAN DEFAULT false,
    created_at TIMESTAMP,
    UNIQUE(template_id, version, language_code)
);

-- Translations table
CREATE TABLE template_translations (
    id UUID PRIMARY KEY,
    template_id UUID REFERENCES templates(id),
    language_code VARCHAR(10) NOT NULL,
    subject TEXT,
    body TEXT NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(template_id, language_code)
);

-- Indexes
CREATE INDEX idx_templates_type ON templates(type);
CREATE INDEX idx_templates_category ON templates(category);
CREATE INDEX idx_templates_active ON templates(is_active);
CREATE INDEX idx_versions_template ON template_versions(template_id);
CREATE INDEX idx_versions_current ON template_versions(is_current);
CREATE INDEX idx_translations_template ON template_translations(template_id);
```

## Event Architecture

### RabbitMQ Setup

```
Exchange: template.events (topic)
│
├─→ Routing Key: template.created
│   └─ Consumers: Analytics, Audit Log, Cache Invalidator
│
├─→ Routing Key: template.updated
│   └─ Consumers: Cache Invalidator, Notification Service
│
└─→ Routing Key: template.deleted
    └─ Consumers: Cache Invalidator, Cleanup Service
```

### Event Payload Structure

```json
{
  "event_type": "template.created",
  "timestamp": "2025-11-12T10:00:00Z",
  "correlation_id": "abc-123",
  "data": {
    "template_id": "welcome_email",
    "name": "Welcome Email",
    "type": "email",
    "created_at": "2025-11-12T10:00:00Z"
  }
}
```

## Caching Strategy

### Cache Keys
```
template:{template_id}:version:{version}:lang:{lang}
template:{template_id}:rendered:{hash(data)}
```

### Cache TTL
- Template metadata: 10 minutes
- Rendered templates: 5 minutes
- Translation data: 10 minutes

### Cache Invalidation
- On template update → Invalidate all related keys
- On template delete → Invalidate all related keys
- On RabbitMQ event → Invalidate across services

## Security Considerations

### Input Validation
- Pydantic schemas validate all inputs
- SQL injection prevention via SQLAlchemy ORM
- XSS prevention in Jinja2 (auto-escaping enabled)

### Template Rendering
- Sandboxed Jinja2 environment
- No code execution in templates
- Variable whitelist validation

### Network Security
- Internal service (no public exposure)
- Network policies in Kubernetes
- TLS for database connections

## Performance Characteristics

### Throughput
- **Template Rendering**: ~1000 req/sec (cached)
- **Template Creation**: ~100 req/sec
- **Database Queries**: <10ms (indexed)

### Latency (p95)
- **Render (cached)**: <5ms
- **Render (uncached)**: <50ms
- **Create Template**: <100ms
- **List Templates**: <30ms

### Resource Usage
- **Memory**: ~256MB base, ~512MB under load
- **CPU**: ~0.5 cores idle, ~2 cores under load
- **Database Connections**: Pool of 20

## Scalability

### Horizontal Scaling
- Stateless service (scales horizontally)
- Load balancer distributes requests
- Shared cache (Redis) and database

### Vertical Scaling
- Increase worker processes (Gunicorn)
- Increase database connection pool
- Increase Redis memory

### Bottlenecks
1. **Database**: Most queries are indexed
2. **Redis**: In-memory, very fast
3. **Jinja2 Rendering**: CPU-bound, but cached

## Monitoring & Observability

### Metrics (Prometheus)
- Request rate, error rate, duration
- Template render time
- Cache hit/miss ratio
- Database connection pool usage

### Logging
- Structured JSON logs
- Correlation IDs for tracing
- Log levels: DEBUG, INFO, WARNING, ERROR

### Health Checks
- `/health` - Full health with dependencies
- `/ready` - Kubernetes readiness probe
- `/live` - Kubernetes liveness probe

## Deployment Architecture

### Docker Compose (Development)
```yaml
services:
  - template-service
  - postgres
  - redis
  - rabbitmq
```

### Kubernetes (Production)
```yaml
Deployment: template-service (3 replicas)
Service: ClusterIP
HPA: 2-10 replicas (CPU 70%)
ConfigMap: Environment variables
Secret: Database credentials
```

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Runtime | Python | 3.11+ |
| Framework | FastAPI | 0.104+ |
| ORM | SQLAlchemy | 2.0+ |
| Validation | Pydantic | 2.0+ |
| Database | PostgreSQL | 15+ |
| Cache | Redis | 7+ |
| Message Queue | RabbitMQ | 3.12+ |
| Template Engine | Jinja2 | 3.1+ |
| Migrations | Alembic | 1.12+ |
| Testing | Pytest | 7.4+ |
| Server | Uvicorn | 0.24+ |

## Design Patterns

### Repository Pattern
- Service layer abstracts database operations
- Easy to test and mock

### Circuit Breaker
- Prevents cascade failures
- Graceful degradation

### Event-Driven
- Loose coupling between services
- Async communication via RabbitMQ

### Caching
- Read-through cache pattern
- Cache-aside for rendered templates

## Future Enhancements

- [ ] Template preview API
- [ ] A/B testing support
- [ ] Template analytics
- [ ] Scheduled template updates
- [ ] Template inheritance
- [ ] Rich text editor integration
- [ ] Template marketplace
- [ ] Multi-tenant support

## References

- [API Reference](./api-reference.md)
- [Integration Guide](./integration/README.md)
- [Deployment Guide](./deployment.md)
- [Development Guide](./development.md)
