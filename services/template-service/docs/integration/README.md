# Integration Guide

> **How to integrate Template Service with other microservices**

## Overview

Template Service provides two integration patterns:

1. **Synchronous** - REST API calls for immediate template rendering
2. **Asynchronous** - RabbitMQ events for template lifecycle notifications

## Quick Integration

### 1. REST API Integration

The most common integration is calling the render endpoint:

```bash
POST /api/v1/templates/{template_id}/render
```

**Use cases:**
- Email Service rendering email templates
- Notification Service rendering push notifications
- SMS Service rendering SMS messages

### 2. Event-Driven Integration

Subscribe to template lifecycle events:

**Exchange**: `template.events` (topic)

**Events:**
- `template.created` - New template created
- `template.updated` - Template content/metadata updated
- `template.deleted` - Template soft deleted

---

## REST API Integration Examples

### Python (requests)

```python
import requests

class TemplateServiceClient:
    def __init__(self, base_url="http://template-service:3004"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
    
    def render_template(self, template_id: str, data: dict, language_code: str = "en"):
        """Render a template with provided data"""
        response = requests.post(
            f"{self.api_url}/templates/{template_id}/render",
            json={"data": data, "language_code": language_code},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        result = response.json()
        
        if not result["success"]:
            raise Exception(f"Template render failed: {result.get('error')}")
        
        return result["data"]

# Usage
client = TemplateServiceClient()
rendered = client.render_template(
    "welcome_email",
    {"name": "John", "company_name": "Acme"}
)
print(rendered["subject"])  # "Welcome John to Acme!"
print(rendered["body"])
```

### Node.js (axios)

```javascript
const axios = require('axios');

class TemplateServiceClient {
  constructor(baseUrl = 'http://template-service:3004') {
    this.apiUrl = `${baseUrl}/api/v1`;
  }

  async renderTemplate(templateId, data, languageCode = 'en') {
    try {
      const response = await axios.post(
        `${this.apiUrl}/templates/${templateId}/render`,
        { data, language_code: languageCode }
      );

      if (!response.data.success) {
        throw new Error(`Template render failed: ${response.data.error}`);
      }

      return response.data.data;
    } catch (error) {
      console.error('Template render error:', error.message);
      throw error;
    }
  }
}

// Usage
const client = new TemplateServiceClient();
const rendered = await client.renderTemplate('welcome_email', {
  name: 'John',
  company_name: 'Acme'
});
console.log(rendered.subject);
console.log(rendered.body);
```

### C# (.NET)

```csharp
using System.Net.Http;
using System.Text.Json;

public class TemplateServiceClient
{
    private readonly HttpClient _httpClient;
    private readonly string _apiUrl;

    public TemplateServiceClient(string baseUrl = "http://template-service:3004")
    {
        _httpClient = new HttpClient();
        _apiUrl = $"{baseUrl}/api/v1";
    }

    public async Task<RenderedTemplate> RenderTemplateAsync(
        string templateId, 
        Dictionary<string, object> data, 
        string languageCode = "en")
    {
        var payload = new
        {
            data = data,
            language_code = languageCode
        };

        var response = await _httpClient.PostAsJsonAsync(
            $"{_apiUrl}/templates/{templateId}/render",
            payload
        );

        response.EnsureSuccessStatusCode();
        var result = await response.Content.ReadFromJsonAsync<ApiResponse>();

        if (!result.Success)
        {
            throw new Exception($"Template render failed: {result.Error}");
        }

        return result.Data;
    }
}

// Usage
var client = new TemplateServiceClient();
var rendered = await client.RenderTemplateAsync("welcome_email", new Dictionary<string, object>
{
    ["name"] = "John",
    ["company_name"] = "Acme"
});
Console.WriteLine(rendered.Subject);
Console.WriteLine(rendered.Body);
```

---

## Event-Driven Integration

### Consuming Template Events

#### Python (pika)

```python
import pika
import json

def on_template_event(ch, method, properties, body):
    """Handle template lifecycle events"""
    event = json.loads(body)
    routing_key = method.routing_key
    
    if routing_key == "template.created":
        print(f"New template created: {event['template_id']}")
        # Invalidate cache, update local registry, etc.
    
    elif routing_key == "template.updated":
        print(f"Template updated: {event['template_id']}")
        # Clear cached rendered templates
    
    elif routing_key == "template.deleted":
        print(f"Template deleted: {event['template_id']}")
        # Remove from local cache

# Connect to RabbitMQ
connection = pika.BlockingConnection(
    pika.URLParameters('amqp://guest:guest@rabbitmq:5672/')
)
channel = connection.channel()

# Declare exchange
channel.exchange_declare(
    exchange='template.events',
    exchange_type='topic',
    durable=True
)

# Create queue
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# Bind to all template events
channel.queue_bind(
    exchange='template.events',
    queue=queue_name,
    routing_key='template.*'
)

# Start consuming
channel.basic_consume(
    queue=queue_name,
    on_message_callback=on_template_event,
    auto_ack=True
)

print('Waiting for template events...')
channel.start_consuming()
```

#### Node.js (amqplib)

```javascript
const amqp = require('amqplib');

async function consumeTemplateEvents() {
  const connection = await amqp.connect('amqp://guest:guest@rabbitmq:5672/');
  const channel = await connection.createChannel();

  const exchange = 'template.events';
  await channel.assertExchange(exchange, 'topic', { durable: true });

  const q = await channel.assertQueue('', { exclusive: true });
  
  // Subscribe to all template events
  await channel.bindQueue(q.queue, exchange, 'template.*');

  console.log('Waiting for template events...');

  channel.consume(q.queue, (msg) => {
    const event = JSON.parse(msg.content.toString());
    const routingKey = msg.fields.routingKey;

    switch (routingKey) {
      case 'template.created':
        console.log(`New template: ${event.template_id}`);
        break;
      case 'template.updated':
        console.log(`Updated template: ${event.template_id}`);
        break;
      case 'template.deleted':
        console.log(`Deleted template: ${event.template_id}`);
        break;
    }
  }, { noAck: true });
}

consumeTemplateEvents().catch(console.error);
```

---

## Service-Specific Integration

### Email Service Integration

```python
# email_service/template_client.py
from template_service_client import TemplateServiceClient

class EmailService:
    def __init__(self):
        self.template_client = TemplateServiceClient()
    
    async def send_welcome_email(self, user_email: str, user_name: str):
        # Render template
        rendered = self.template_client.render_template(
            "welcome_email",
            {
                "name": user_name,
                "company_name": "Acme Corp",
                "verification_link": f"https://app.acme.com/verify/{user_email}"
            }
        )
        
        # Send email using your email provider
        await self.send_email(
            to=user_email,
            subject=rendered["subject"],
            body=rendered["body"]
        )
```

### Notification Service Integration

```javascript
// notification_service/template_client.js
const TemplateServiceClient = require('./template_service_client');

class NotificationService {
  constructor() {
    this.templateClient = new TemplateServiceClient();
  }

  async sendPushNotification(userId, templateId, data) {
    // Render template
    const rendered = await this.templateClient.renderTemplate(
      templateId,
      data
    );

    // Send push notification
    await this.pushProvider.send({
      userId: userId,
      title: rendered.subject,
      body: rendered.body
    });
  }
}
```

---

## Error Handling

### Handling Template Errors

```python
from requests.exceptions import RequestException

try:
    rendered = client.render_template("welcome_email", data)
except RequestException as e:
    # Network error - retry with exponential backoff
    logger.error(f"Template service unreachable: {e}")
    # Fallback to default template or queue for retry
except Exception as e:
    # Template error (missing variables, etc.)
    logger.error(f"Template render failed: {e}")
    # Use fallback template or skip notification
```

### Circuit Breaker Pattern

```python
from pybreaker import CircuitBreaker

template_breaker = CircuitBreaker(
    fail_max=5,
    timeout_duration=60
)

@template_breaker
def render_with_circuit_breaker(template_id, data):
    return client.render_template(template_id, data)

try:
    rendered = render_with_circuit_breaker("welcome_email", data)
except CircuitBreakerError:
    # Service is down, use fallback
    rendered = get_fallback_template()
```

---

## Caching Strategy

### Client-Side Caching

```python
import redis
import json

class CachedTemplateClient:
    def __init__(self):
        self.client = TemplateServiceClient()
        self.redis = redis.Redis(host='redis', port=6379)
        self.cache_ttl = 300  # 5 minutes
    
    def render_template(self, template_id: str, data: dict):
        # Create cache key from template_id and data
        cache_key = f"template:{template_id}:{hash(json.dumps(data, sort_keys=True))}"
        
        # Check cache
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Render and cache
        rendered = self.client.render_template(template_id, data)
        self.redis.setex(cache_key, self.cache_ttl, json.dumps(rendered))
        
        return rendered
```

---

## Health Checks

### Monitoring Template Service

```python
def check_template_service_health():
    """Check if template service is healthy"""
    try:
        response = requests.get(
            "http://template-service:3004/health",
            timeout=5
        )
        health = response.json()
        return health["data"]["status"] == "healthy"
    except:
        return False
```

---

## Best Practices

1. **Use correlation IDs** for request tracing
2. **Implement retries** with exponential backoff
3. **Cache rendered templates** when data doesn't change frequently
4. **Subscribe to events** to invalidate caches
5. **Use circuit breakers** to prevent cascade failures
6. **Have fallback templates** for critical notifications
7. **Monitor render times** and set appropriate timeouts
8. **Validate data** before sending to template service

---

## Environment Configuration

### Docker Compose

```yaml
services:
  email-service:
    environment:
      - TEMPLATE_SERVICE_URL=http://template-service:3004
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
    depends_on:
      - template-service
      - rabbitmq
```

### Kubernetes

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: email-service-config
data:
  TEMPLATE_SERVICE_URL: "http://template-service.default.svc.cluster.local:3004"
  RABBITMQ_URL: "amqp://guest:guest@rabbitmq.default.svc.cluster.local:5672/"
```

---

See [Examples](../examples/) for complete working implementations.
