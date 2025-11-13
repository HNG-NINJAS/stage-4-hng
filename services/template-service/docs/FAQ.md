# Frequently Asked Questions (FAQ)

> **Common questions about Template Service**

## General Questions

### What is Template Service?

Template Service is a microservice for managing notification templates with multi-language support, version control, and event-driven architecture. It handles template rendering for emails, push notifications, and SMS messages.

### What are the main features?

- ✅ Template CRUD operations
- ✅ Jinja2 variable substitution
- ✅ Multi-language support (i18n)
- ✅ Automatic version control
- ✅ RabbitMQ event publishing
- ✅ Redis caching
- ✅ Circuit breaker & retry logic
- ✅ Prometheus metrics
- ✅ OpenAPI documentation

### What technologies does it use?

- **Backend**: Python 3.11+, FastAPI
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+ (optional)
- **Message Queue**: RabbitMQ 3.12+ (optional)
- **Template Engine**: Jinja2

## Getting Started

### How do I run it locally?

```bash
# Quick start with Docker Compose
docker-compose up -d template-service

# Or manually
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload --port 3004
```

See [Getting Started Guide](./getting-started.md) for details.

### Do I need Redis and RabbitMQ?

**No, they're optional:**
- **Redis**: Improves performance through caching, but service works without it
- **RabbitMQ**: Enables event publishing, but not required for basic template rendering

The service will work with just PostgreSQL.

### How do I check if it's running?

```bash
curl http://localhost:3004/health
```

Should return:
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

## API Usage

### How do I render a template?

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

See [API Reference](./api-reference.md#render-template) for details.

### What template variables can I use?

Any variables you define in your template. Use Jinja2 syntax:
- `{{variable_name}}` - Simple substitution
- `{{user.name}}` - Nested objects
- `{% if condition %}...{% endif %}` - Conditionals
- `{% for item in items %}...{% endfor %}` - Loops

Example:
```
Subject: Welcome {{name}}!
Body: Hi {{name}}, welcome to {{company_name}}!
```

### How do I handle missing variables?

The API will return an error if required variables are missing:

```json
{
  "success": false,
  "error": "MISSING_VARIABLES",
  "message": "Missing required variables: verification_link"
}
```

**Best practice**: Always provide all variables or use default values in templates:
```
{{variable_name|default('default value')}}
```

### Can I use HTML in templates?

**Yes!** Templates support HTML for email bodies:

```html
<h1>Welcome {{name}}!</h1>
<p>Click <a href="{{verification_link}}">here</a> to verify.</p>
```

Jinja2 auto-escapes variables to prevent XSS attacks.

## Multi-Language Support

### How do I add translations?

```bash
curl -X POST http://localhost:3004/api/v1/templates/welcome_email/translations \
  -H "Content-Type: application/json" \
  -d '{
    "language_code": "es",
    "subject": "¡Bienvenido {{name}}!",
    "body": "Hola {{name}}, ¡bienvenido a {{company_name}}!"
  }'
```

### How do I render in a specific language?

```bash
curl -X POST http://localhost:3004/api/v1/templates/welcome_email/render \
  -H "Content-Type: application/json" \
  -d '{
    "data": {"name": "Juan"},
    "language_code": "es"
  }'
```

### What happens if a translation doesn't exist?

The service falls back to the default language (English).

## Integration

### How do I integrate with my service?

Three main approaches:

1. **REST API** (synchronous) - For immediate template rendering
2. **RabbitMQ Events** (asynchronous) - For cache invalidation and notifications
3. **Client Libraries** - Use our pre-built clients

See [Integration Guide](./integration/overview.md) for details.

### Which client library should I use?

Depends on your language:
- **Python/FastAPI** → [Python Client](./integration/python-client.md)
- **TypeScript/NestJS** → [TypeScript Client](./integration/typescript-client.md)
- **C#/.NET** → [C# Client](./integration/csharp-client.md)

### Should I cache rendered templates?

**Yes, if:**
- Same template rendered frequently with same data
- Template content doesn't change often
- Performance is critical

**No, if:**
- Data changes frequently
- Templates are personalized per user
- Memory is constrained

The service has built-in Redis caching (5-minute TTL).

### How do I handle service downtime?

**Best practices:**
1. Implement retry logic with exponential backoff
2. Use circuit breaker pattern
3. Have fallback templates
4. Queue requests for later retry

Example:
```python
try:
    rendered = client.render_template(template_id, data)
except ServiceUnavailable:
    # Use fallback template
    rendered = get_fallback_template()
```

## Performance

### How fast is template rendering?

**Typical latency (p95):**
- Cached: <5ms
- Uncached: <50ms
- With database query: <100ms

**Throughput:**
- ~1000 req/sec (cached)
- ~100 req/sec (uncached)

### How can I improve performance?

1. **Enable Redis caching** - Dramatically improves response times
2. **Cache on client side** - For frequently used templates
3. **Use connection pooling** - Reuse HTTP connections
4. **Batch operations** - Render multiple templates in parallel
5. **Scale horizontally** - Add more service instances

### What are the resource requirements?

**Minimum:**
- Memory: 256MB
- CPU: 0.5 cores
- Database connections: 10

**Recommended (production):**
- Memory: 512MB
- CPU: 1-2 cores
- Database connections: 20
- Replicas: 3+

## Deployment

### How do I deploy to production?

**Docker:**
```bash
docker build -t template-service:1.0.0 .
docker run -d -p 3004:3004 template-service:1.0.0
```

**Kubernetes:**
```bash
kubectl apply -f k8s/
```

See [Deployment Guide](./operations/deployment.md) for details.

### How do I run database migrations?

```bash
# Development
alembic upgrade head

# Production (Kubernetes)
kubectl exec -it deployment/template-service -- alembic upgrade head
```

### How do I scale the service?

**Horizontal scaling** (recommended):
```bash
# Kubernetes
kubectl scale deployment template-service --replicas=5

# Or use HPA for auto-scaling
kubectl autoscale deployment template-service --min=3 --max=10 --cpu-percent=70
```

**Vertical scaling**:
```yaml
resources:
  limits:
    memory: "1Gi"
    cpu: "2000m"
```

### How do I monitor the service?

1. **Health checks**: `GET /health`
2. **Prometheus metrics**: `GET /metrics`
3. **Logs**: Structured JSON logs
4. **Distributed tracing**: Use correlation IDs

See [Monitoring Guide](./operations/monitoring.md) for details.

## Troubleshooting

### Service won't start

**Check:**
1. Database connection: `psql $DATABASE_URL`
2. Environment variables: `env | grep DATABASE_URL`
3. Logs: `docker-compose logs template-service`
4. Port availability: `lsof -i :3004`

### Database connection error

```bash
# Test connection
psql postgresql://user:pass@host:5432/db

# Check if PostgreSQL is running
docker-compose ps postgres_template

# Restart PostgreSQL
docker-compose restart postgres_template
```

### Template not found

**Possible causes:**
1. Template doesn't exist - check with `GET /api/v1/templates`
2. Template is inactive - check `is_active` field
3. Wrong template_id - verify spelling

### Render fails with missing variables

**Solution**: Provide all required variables or use defaults:
```
{{variable_name|default('default value')}}
```

### High memory usage

**Solutions:**
1. Reduce cache TTL
2. Limit database connection pool
3. Increase memory limits
4. Scale horizontally instead

### Slow response times

**Check:**
1. Database query performance
2. Cache hit rate
3. Network latency
4. Resource utilization

**Solutions:**
1. Enable Redis caching
2. Add database indexes
3. Scale horizontally
4. Optimize templates

## Security

### Is the service secure?

**Built-in security:**
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ XSS prevention (Jinja2 auto-escaping)
- ✅ Input validation (Pydantic)
- ✅ Sandboxed template rendering

**You should add:**
- Authentication/authorization
- Rate limiting
- Network policies
- TLS/SSL

### Can templates execute code?

**No.** Templates run in a sandboxed Jinja2 environment with no code execution capabilities. Only variable substitution and basic logic (if/for) are allowed.

### How do I secure the API?

**Recommendations:**
1. Add authentication (JWT, API keys)
2. Implement rate limiting
3. Use network policies (Kubernetes)
4. Enable TLS/SSL
5. Restrict access to internal network

## Development

### How do I contribute?

1. Fork the repository
2. Create a feature branch
3. Make changes following coding standards
4. Write tests
5. Submit pull request

See [Development Guide](./development.md) for details.

### How do I run tests?

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test
pytest tests/test_api.py::test_create_template -v
```

### How do I create a migration?

```bash
# Auto-generate
alembic revision --autogenerate -m "Add new column"

# Review generated file in alembic/versions/

# Apply migration
alembic upgrade head
```

## Events

### What events does the service publish?

| Event | Routing Key | When |
|-------|-------------|------|
| Template Created | `template.created` | New template created |
| Template Updated | `template.updated` | Template modified |
| Template Deleted | `template.deleted` | Template deleted |

### How do I subscribe to events?

See [Event Integration Guide](./integration/events.md) for examples in Python, TypeScript, and C#.

### Why use events?

**Use cases:**
- Cache invalidation across services
- Audit logging
- Analytics and monitoring
- Workflow triggers
- Eventual consistency

## Best Practices

### Template Design

1. **Keep templates simple** - Complex logic belongs in code
2. **Use meaningful variable names** - `user_name` not `un`
3. **Provide default values** - `{{name|default('User')}}`
4. **Test with real data** - Verify rendering before deploying
5. **Version templates** - Service handles this automatically

### Integration

1. **Use correlation IDs** - For distributed tracing
2. **Implement retries** - With exponential backoff
3. **Use circuit breakers** - Prevent cascade failures
4. **Cache when possible** - Reduce API calls
5. **Have fallbacks** - For critical notifications

### Operations

1. **Monitor health checks** - Set up alerts
2. **Track metrics** - Request rate, errors, latency
3. **Backup database** - Regular automated backups
4. **Scale horizontally** - Add replicas, not resources
5. **Use staging environment** - Test before production

## Still Have Questions?

1. **Check documentation**: [Complete Index](./INDEX.md)
2. **Review examples**: [Code Examples](./examples/README.md)
3. **Search issues**: Look for similar problems
4. **Ask the team**: Reach out in your team chat

---

**Can't find your question?** Please submit a pull request to add it to this FAQ!
