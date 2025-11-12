# Client Examples

> **Ready-to-use client implementations for Template Service**

## Available Examples

### Python Client
- **File**: [python_client.py](./python_client.py)
- **Framework**: requests
- **Use Case**: Python/FastAPI services

```bash
pip install requests
python docs/examples/python_client.py
```

### Node.js Client
- **File**: [nodejs_client.js](./nodejs_client.js)
- **Framework**: axios
- **Use Case**: Node.js/Express/NestJS services

```bash
npm install axios
node docs/examples/nodejs_client.js
```

### C# Client
- **File**: [csharp_client.cs](./csharp_client.cs)
- **Framework**: HttpClient
- **Use Case**: .NET/ASP.NET Core services

```bash
dotnet run
```

## Quick Start

All examples demonstrate:
- Health check
- Template rendering
- Multi-language support
- Error handling

### Basic Usage Pattern

```python
# 1. Initialize client
client = TemplateServiceClient("http://localhost:3004")

# 2. Check health
if not client.health_check():
    raise Exception("Service unavailable")

# 3. Render template
rendered = client.render_template(
    "welcome_email",
    {"name": "John", "company_name": "Acme"}
)

# 4. Use rendered content
send_email(
    subject=rendered["subject"],
    body=rendered["body"]
)
```

## Integration Patterns

### Email Service Integration

```python
class EmailService:
    def __init__(self):
        self.template_client = TemplateServiceClient()
    
    async def send_welcome_email(self, user):
        rendered = self.template_client.render_template(
            "welcome_email",
            {"name": user.name, "company_name": "Acme"}
        )
        await self.send_email(user.email, rendered)
```

### Notification Service Integration

```javascript
class NotificationService {
  async sendNotification(userId, templateId, data) {
    const rendered = await this.templateClient.renderTemplate(
      templateId,
      data
    );
    await this.pushProvider.send(userId, rendered);
  }
}
```

## Error Handling

All clients implement proper error handling:

```python
try:
    rendered = client.render_template(template_id, data)
except requests.HTTPError as e:
    # Network/HTTP error
    logger.error(f"Template service error: {e}")
    use_fallback_template()
except ValueError as e:
    # Template render error (missing variables, etc.)
    logger.error(f"Render error: {e}")
    skip_notification()
```

## Testing

Each example can be run standalone for testing:

```bash
# Python
python docs/examples/python_client.py

# Node.js
node docs/examples/nodejs_client.js

# C#
dotnet run --project docs/examples/
```

## Production Considerations

1. **Connection Pooling**: Reuse HTTP clients
2. **Timeouts**: Set appropriate request timeouts
3. **Retries**: Implement exponential backoff
4. **Caching**: Cache rendered templates when possible
5. **Circuit Breaker**: Prevent cascade failures
6. **Monitoring**: Track render times and errors

## See Also

- [Integration Guide](../integration/README.md)
- [API Reference](../api-reference.md)
- [Deployment Guide](../deployment.md)
