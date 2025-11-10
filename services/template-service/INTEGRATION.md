# Template Service - Integration Guide

## For Other Services

### Base URL
- **Development**: `http://localhost:3004`
- **Docker**: `http://template-service:3004`

### Authentication
Currently no authentication required (add if needed).

## API Usage

### 1. Get Template
```bash
GET /api/v1/templates/{template_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "template_id": "welcome_email",
    "name": "Welcome Email",
    "type": "email",
    "current_version": {
      "subject": "Welcome {{name}}!",
      "body": "...",
      "variables": ["name", "email"]
    }
  }
}
```

### 2. Render Template
```bash
POST /api/v1/templates/{template_id}/render
Content-Type: application/json

{
  "data": {
    "name": "John Doe",
    "email": "john@example.com"
  },
  "language_code": "en"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "subject": "Welcome John Doe!",
    "body": "...",
    "variables_used": ["name", "email"]
  }
}
```

### 3. Error Handling

All errors follow this format:
```json
{
  "success": false,
  "error": "TEMPLATE_NOT_FOUND",
  "message": "Template with id 'xyz' not found"
}
```

## Available Templates

| Template ID | Type | Description | Variables |
|------------|------|-------------|-----------|
| `welcome_email` | email | Welcome new users | name, company_name, verification_link |
| `password_reset` | email | Password reset | name, reset_link, expiry_hours |
| `order_shipped` | push | Order shipped notification | name, order_id, tracking_url |

## Health Check
```bash
GET /health
```

Returns service status and dependencies health.

## Integration Examples

### Python (for Email/Push Services)
```python
import httpx

async def render_template(template_id: str, data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://template-service:3004/api/v1/templates/{template_id}/render",
            json={"data": data, "language_code": "en"}
        )
        result = response.json()
        if result["success"]:
            return result["data"]
        raise Exception(result["error"])
```

### Node.js (for API Gateway)
```javascript
const axios = require('axios');

async function renderTemplate(templateId, data) {
  const response = await axios.post(
    `http://template-service:3004/api/v1/templates/${templateId}/render`,
    { data, language_code: 'en' }
  );
  
  if (response.data.success) {
    return response.data.data;
  }
  throw new Error(response.data.error);
}
```

### C# (for .NET Services)
```csharp
using System.Net.Http;
using System.Text.Json;

public async Task<TemplateRenderResult> RenderTemplateAsync(string templateId, Dictionary<string, string> data)
{
    var client = new HttpClient();
    var payload = new { data, language_code = "en" };
    
    var response = await client.PostAsync(
        $"http://template-service:3004/api/v1/templates/{templateId}/render",
        new StringContent(JsonSerializer.Serialize(payload))
    );
    
    var result = await response.Content.ReadAsStringAsync();
    var parsed = JsonSerializer.Deserialize<ApiResponse>(result);
    
    if (parsed.Success)
        return parsed.Data;
    
    throw new Exception(parsed.Error);
}
```

## Need Help?

Contact: [iMuaz/G12]