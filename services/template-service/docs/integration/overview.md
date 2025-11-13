# Integration Overview

This guide provides an overview of integrating with the Template Service.

## Integration Methods

Template Service offers two integration patterns:

### 1. REST API (Synchronous)

**Use for:**
- Immediate template rendering (Email/Push services)
- Fetching template details (API Gateway)
- Template management (Admin interfaces)

**Example:**
```bash
POST /api/v1/templates/welcome_email/render
```

**Best for:** Real-time operations requiring immediate response

---

### 2. RabbitMQ Events (Asynchronous)

**Use for:**
- Cache invalidation when templates change
- Audit logging
- Analytics and monitoring
- Workflow triggers

**Example:**
```python
# Listen to template.created, template.updated, template.deleted
```

**Best for:** Event-driven architectures and eventual consistency

---

## Service Information

### Endpoints

| Environment | URL |
|------------|-----|
| Local Development | `http://localhost:3004` |
| Docker Network | `http://template-service:3004` |
| Production | Configure as needed |

### Health Checks

```bash
# Health check (includes dependencies)
GET /health

# Kubernetes readiness probe
GET /ready

# Kubernetes liveness probe
GET /live

# Prometheus metrics
GET /metrics
```

---

## Client Libraries

We provide client implementations for:

- [Python/FastAPI](./python-client.md) - For Email/Push services
- [TypeScript/NestJS](./typescript-client.md) - For API Gateway
- [C#/.NET](./csharp-client.md) - For User Service
- [RabbitMQ Events](./events.md) - For event-driven integration

---

## Quick Start Examples

### Python
```python
from template_client import TemplateClient

client = TemplateClient(base_url="http://template-service:3004")

rendered = await client.render_template(
    template_id="welcome_email",
    data={"name": "John", "company_name": "Acme Corp"}
)

print(rendered["subject"])  # "Welcome John to Acme Corp!"
```

### TypeScript/NestJS
```typescript
import { TemplateServiceClient } from './templateClient';

const client = new TemplateServiceClient('http://template-service:3004');

const rendered = await client.renderTemplate('welcome_email', {
  name: 'John',
  company_name: 'Acme Corp'
});

console.log(rendered.subject);  // "Welcome John to Acme Corp!"
```

### C#/.NET
```csharp
var client = new TemplateServiceClient(httpClient, logger);

var rendered = await client.RenderTemplateAsync(
    "welcome_email",
    new Dictionary<string, object> {
        { "name", "John" },
        { "company_name", "Acme Corp" }
    }
);

Console.WriteLine(rendered.Subject);  // "Welcome John to Acme Corp!"
```

---

## Best Practices

### 1. Use Correlation IDs
Always include correlation IDs for distributed tracing:

```python
rendered = await client.render_template(
    template_id="welcome_email",
    data=data,
    correlation_id=f"user-signup-{user_id}"
)
```

### 2. Implement Fallback Strategy
```python
async def send_email_safe(template_id: str, data: dict):
    # Try primary template
    rendered = await client.render_template(template_id, data)
    
    if not rendered:
        # Fallback to generic template
        rendered = await client.render_template("generic_notification", data)
    
    if not rendered:
        # Last resort: hardcoded message
        rendered = {"subject": "Notification", "body": f"Hello {data['name']}"}
    
    await send_email(rendered)
```

### 3. Cache Template Metadata
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_template(template_id: str):
    return client.get_template(template_id)
```

### 4. Implement Circuit Breaker
```python
from pybreaker import CircuitBreaker

breaker = CircuitBreaker(fail_max=5, timeout_duration=60)

@breaker
async def render_template_protected(template_id: str, data: dict):
    return await client.render_template(template_id, data)
```

### 5. Handle Errors Gracefully
```python
try:
    rendered = await client.render_template(template_id, data)
except TimeoutError:
    logger.error("Template service timeout")
    # Use fallback
except Exception as e:
    logger.error(f"Template render failed: {e}")
    # Use fallback
```

---

## Error Handling

### Common Errors

#### TEMPLATE_NOT_FOUND
```json
{
  "success": false,
  "error": "TEMPLATE_NOT_FOUND",
  "message": "Template with id 'invalid_template' not found"
}
```

**Solution:** Verify template_id and check if template is active

#### MISSING_VARIABLES
```json
{
  "success": false,
  "error": "MISSING_VARIABLES",
  "message": "Missing required variables: verification_link"
}
```

**Solution:** Check template's variables list and provide all required data

#### Service Unavailable
**Solution:** Implement retry logic with exponential backoff

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def render_with_retry(template_id: str, data: dict):
    return await client.render_template(template_id, data)
```

---

## Testing Your Integration

### Unit Testing
```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_render_template_success():
    mock_response = {
        "success": True,
        "data": {
            "subject": "Welcome John!",
            "body": "Hi John!",
            "variables_used": ["name"]
        }
    }
    
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response
        
        client = TemplateClient()
        result = await client.render_template("welcome_email", {"name": "John"})
        
        assert result["subject"] == "Welcome John!"
```

### Integration Testing
```bash
# Start Template Service
docker-compose up -d template-service

# Run integration tests
pytest tests/integration/test_template_integration.py
```

---

## Monitoring

### Health Check Integration
```python
async def check_dependencies():
    template_healthy = await template_client.health_check()
    
    return {
        "template_service": "up" if template_healthy else "down"
    }
```

### Metrics Collection
```python
from prometheus_client import Counter, Histogram

template_render_counter = Counter(
    'template_renders_total',
    'Total template renders',
    ['template_id', 'status']
)

template_render_duration = Histogram(
    'template_render_duration_seconds',
    'Template render duration',
    ['template_id']
)
```

---

## Integration Checklist

Before deploying:

- [ ] Template Service health check passes
- [ ] Test template rendering with sample data
- [ ] Error handling implemented
- [ ] Retry logic configured
- [ ] Circuit breaker applied
- [ ] Logging includes correlation IDs
- [ ] Metrics being collected
- [ ] Fallback templates configured
- [ ] Load testing completed
- [ ] Monitoring dashboards setup

---

## Next Steps

- Review language-specific client guides:
  - [Python Client](./python-client.md)
  - [TypeScript/NestJS Client](./typescript-client.md)
  - [C# Client](./csharp-client.md)
- Set up [Event Streaming](./events.md)
- Configure [Monitoring](../operations/monitoring.md)
