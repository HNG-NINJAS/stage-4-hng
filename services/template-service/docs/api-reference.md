# API Reference

Complete reference for Template Service REST API.

## Base URL

- **Local**: `http://localhost:3004`
- **Docker**: `http://template-service:3004`

## Response Format

All endpoints return this structure:

```json
{
  "success": boolean,
  "data": object | null,
  "error": string | null,
  "message": string,
  "meta": {
    "total": number,
    "limit": number,
    "page": number,
    "total_pages": number,
    "has_next": boolean,
    "has_previous": boolean
  }
}
```

## Common Headers

**Request:**
```http
Content-Type: application/json
X-Correlation-ID: your-trace-id (optional)
```

**Response:**
```http
Content-Type: application/json
X-Correlation-ID: echoed-trace-id
X-Response-Time: 0.045
X-Service-Version: 1.0.0
```

## Endpoints

### Templates

#### Create Template
```http
POST /api/v1/templates
```

**Request Body:**
```json
{
  "template_id": "welcome_email",
  "name": "Welcome Email",
  "type": "email",
  "subject": "Welcome {{name}}!",
  "body": "Hi {{name}}, welcome to {{company_name}}!",
  "language_code": "en",
  "description": "Welcome email for new users",
  "category": "onboarding"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "template_id": "welcome_email",
    "name": "Welcome Email",
    "type": "email",
    "is_active": true,
    "created_at": "2025-11-12T10:00:00Z"
  },
  "message": "Template created successfully"
}
```

---

#### Get Template
```http
GET /api/v1/templates/{template_id}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "template_id": "welcome_email",
    "name": "Welcome Email",
    "type": "email",
    "description": "Welcome email for new users",
    "category": "onboarding",
    "is_active": true,
    "created_at": "2025-11-12T10:00:00Z",
    "updated_at": "2025-11-12T10:00:00Z",
    "current_version": {
      "version": "1.0.0",
      "subject": "Welcome {{name}}!",
      "body": "Hi {{name}}, welcome!",
      "variables": ["name", "company_name"]
    }
  }
}
```

---

#### List Templates
```http
GET /api/v1/templates?page=1&limit=10&type=email&search=welcome
```

**Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `page` | integer | Page number (default: 1) | `page=2` |
| `limit` | integer | Items per page (default: 10, max: 100) | `limit=20` |
| `type` | string | Filter by type (email, push, sms) | `type=email` |
| `category` | string | Filter by category | `category=onboarding` |
| `search` | string | Search in name/description | `search=welcome` |

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "template_id": "welcome_email",
      "name": "Welcome Email",
      "type": "email",
      "is_active": true
    }
  ],
  "meta": {
    "total": 15,
    "limit": 10,
    "page": 1,
    "total_pages": 2,
    "has_next": true,
    "has_previous": false
  }
}
```

---

#### Update Template
```http
PUT /api/v1/templates/{template_id}
```

**Request Body:**
```json
{
  "name": "Welcome Email - Updated",
  "subject": "Welcome {{name}} to {{company_name}}!",
  "body": "Hi {{name}}, welcome!"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "template_id": "welcome_email",
    "updated_at": "2025-11-12T11:00:00Z"
  },
  "message": "Template updated successfully"
}
```

---

#### Delete Template
```http
DELETE /api/v1/templates/{template_id}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Template deleted successfully"
}
```

---

#### Render Template
```http
POST /api/v1/templates/{template_id}/render
```

**Request Body:**
```json
{
  "data": {
    "name": "John Doe",
    "company_name": "Acme Corp",
    "verification_link": "https://example.com/verify/123"
  },
  "language_code": "en"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "subject": "Welcome John Doe to Acme Corp!",
    "body": "Hi John Doe, welcome to Acme Corp!",
    "variables_used": ["name", "company_name", "verification_link"]
  },
  "message": "Template rendered successfully"
}
```

---

#### Add Translation
```http
POST /api/v1/templates/{template_id}/translations
```

**Request Body:**
```json
{
  "language_code": "es",
  "subject": "¡Bienvenido {{name}}!",
  "body": "Hola {{name}}, ¡bienvenido a {{company_name}}!"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "template_id": "welcome_email",
    "language_code": "es"
  },
  "message": "Translation added successfully"
}
```

---

#### Get Version History
```http
GET /api/v1/templates/{template_id}/versions
```

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "version": "1.0.1",
      "subject": "Welcome {{name}}!",
      "body": "Hi {{name}}!",
      "variables": ["name"],
      "is_current": true,
      "created_at": "2025-11-12T12:00:00Z"
    }
  ]
}
```

---

#### Get Statistics
```http
GET /api/v1/templates/stats/summary
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "total_templates": 10,
    "active_templates": 8,
    "templates_by_type": {
      "email": 6,
      "push": 2,
      "sms": 2
    }
  }
}
```

---

### Health & Monitoring

#### Health Check
```http
GET /health
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "template-service",
    "version": "1.0.0",
    "dependencies": {
      "database": "up",
      "redis": "up",
      "rabbitmq": "up"
    }
  }
}
```

---

#### Readiness Probe
```http
GET /ready
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "ready": true
  }
}
```

---

#### Liveness Probe
```http
GET /live
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "alive": true
  }
}
```

---

#### Prometheus Metrics
```http
GET /metrics
```

**Response (200):**
```
# HELP template_http_requests_total Total HTTP requests
# TYPE template_http_requests_total counter
template_http_requests_total{method="POST",endpoint="/api/v1/templates/render"} 1234

# HELP template_render_duration_seconds Template render duration
# TYPE template_render_duration_seconds histogram
template_render_duration_seconds_bucket{template_id="welcome_email",le="0.1"} 950
```

---

## Error Responses

### Template Not Found (404)
```json
{
  "success": false,
  "error": "TEMPLATE_NOT_FOUND",
  "message": "Template with id 'invalid_template' not found"
}
```

### Missing Variables (400)
```json
{
  "success": false,
  "error": "MISSING_VARIABLES",
  "message": "Missing required variables: verification_link, company_name"
}
```

### Validation Error (422)
```json
{
  "success": false,
  "error": "VALIDATION_ERROR",
  "message": "Invalid request body",
  "details": [
    {
      "field": "template_id",
      "message": "Field required"
    }
  ]
}
```

### Internal Server Error (500)
```json
{
  "success": false,
  "error": "INTERNAL_ERROR",
  "message": "An unexpected error occurred"
}
```

---

## Rate Limiting

Currently no rate limiting is enforced. Consider implementing rate limiting in production.

## Authentication

Currently no authentication is required. Implement authentication/authorization as needed for your environment.

## OpenAPI Specification

Interactive API documentation available at:
- **Swagger UI**: http://localhost:3004/docs
- **ReDoc**: http://localhost:3004/redoc
- **OpenAPI JSON**: http://localhost:3004/openapi.json
