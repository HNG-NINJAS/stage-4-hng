# Template Service - Integration Guide

**Version**: 1.0.0  
**Last Updated**: November 10, 2025  
**Service Owner**: Template Service Team

This guide provides everything you need to integrate with the Template Service in our distributed notification system.

---

## Table of Contents

1. [Overview](#overview)
2. [Service Information](#service-information)
3. [Integration Methods](#integration-methods)
4. [REST API Integration](#rest-api-integration)
5. [RabbitMQ Events Integration](#rabbitmq-events-integration)
6. [Language-Specific Examples](#language-specific-examples)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Testing](#testing)
10. [Support](#support)

---

## Overview

Template Service manages notification templates with:
- ✅ Template CRUD operations
- ✅ Variable substitution (Jinja2)
- ✅ Multi-language support (i18n)
- ✅ Version history tracking
- ✅ Event publishing via RabbitMQ
- ✅ Redis caching for performance

### Key Capabilities

| Feature | Description |
|---------|-------------|
| **Template Rendering** | Convert `{{variable}}` to actual values |
| **Multi-language** | Same template in multiple languages |
| **Version Control** | Automatic version tracking on changes |
| **Event Publishing** | Notifies other services of changes |
| **Caching** | Fast template retrieval with Redis |

---

## Service Information

### Endpoints

| Environment | URL | Notes |
|------------|-----|-------|
| **Local Development** | `http://localhost:3004` | Run locally |
| **Docker Network** | `http://template-service:3004` | Within docker-compose |
| **Production** | `https://template-service.yourdomain.com` | To be configured |

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

### API Documentation

- **Swagger UI**: `http://localhost:3004/docs`
- **ReDoc**: `http://localhost:3004/redoc`
- **OpenAPI JSON**: `http://localhost:3004/openapi.json`

---

## Integration Methods

Template Service offers **two integration methods**:

### 1. REST API (Synchronous) ⚡

**Use for:**
- Immediate template rendering (Email/Push services)
- Fetching template details (API Gateway)
- Template management (Admin interfaces)

**Example:**
```bash
POST /api/v1/templates/welcome_email/render
```

### 2. RabbitMQ Events (Asynchronous) 📡

**Use for:**
- Cache invalidation when templates change
- Audit logging
- Analytics and monitoring
- Workflow triggers

**Example:**
```python
# Listen to template.created, template.updated, template.deleted
```

---

## REST API Integration

### Base Response Format

**All endpoints return this structure:**
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

### Common Headers

**Request Headers:**
```http
Content-Type: application/json
X-Correlation-ID: your-trace-id (optional but recommended)
```

**Response Headers:**
```http
Content-Type: application/json
X-Correlation-ID: echoed-trace-id
X-Response-Time: 0.045
X-Service-Version: 1.0.0
```

---

### API Endpoints Reference

#### 1. Get Template Details
```http
GET /api/v1/templates/{template_id}
```

**Purpose**: Retrieve template metadata, current version, and variables.

**Example Request:**
```bash
curl -X GET "http://template-service:3004/api/v1/templates/welcome_email" \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: user-123-signup"
```

**Success Response (200):**
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
    "created_at": "2025-11-10T10:00:00Z",
    "updated_at": "2025-11-10T10:00:00Z",
    "current_version": {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "version": "1.0.0",
      "subject": "Welcome {{name}} to {{company_name}}!",
      "body": "Hi {{name}},\n\nWelcome to {{company_name}}!",
      "variables": ["name", "company_name", "verification_link"],
      "is_current": true,
      "created_at": "2025-11-10T10:00:00Z"
    }
  },
  "message": "Template retrieved successfully",
  "meta": {
    "total": 1,
    "limit": 10,
    "page": 1,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  }
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "TEMPLATE_NOT_FOUND",
  "message": "Template with id 'invalid_template' not found",
  "meta": {
    "total": 0,
    "limit": 10,
    "page": 1,
    "total_pages": 0,
    "has_next": false,
    "has_previous": false
  }
}
```

---

#### 2. Render Template
```http
POST /api/v1/templates/{template_id}/render
```

**Purpose**: Render template with provided data (most commonly used endpoint).

**Request Body:**
```json
{
  "data": {
    "name": "John Doe",
    "company_name": "Acme Corp",
    "verification_link": "https://example.com/verify/abc123"
  },
  "language_code": "en"
}
```

**Example Request:**
```bash
curl -X POST "http://template-service:3004/api/v1/templates/welcome_email/render" \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: email-send-456" \
  -d '{
    "data": {
      "name": "John Doe",
      "company_name": "Acme Corp",
      "verification_link": "https://example.com/verify/abc123"
    },
    "language_code": "en"
  }'
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "subject": "Welcome John Doe to Acme Corp!",
    "body": "Hi John Doe,\n\nWelcome to Acme Corp!\n\nPlease verify your email: https://example.com/verify/abc123",
    "variables_used": ["name", "company_name", "verification_link"]
  },
  "message": "Template rendered successfully",
  "meta": {
    "total": 1,
    "limit": 10,
    "page": 1,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  }
}
```

**Error Response - Missing Variables (200 with success: false):**
```json
{
  "success": false,
  "error": "MISSING_VARIABLES",
  "message": "Missing required variables: verification_link",
  "meta": {
    "total": 0,
    "limit": 10,
    "page": 1,
    "total_pages": 0,
    "has_next": false,
    "has_previous": false
  }
}
```

---

#### 3. List Templates
```http
GET /api/v1/templates?page=1&limit=10&type=email&search=welcome
```

**Purpose**: Get paginated list of templates with filters.

**Query Parameters:**

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `page` | integer | No | Page number (default: 1) | `page=2` |
| `limit` | integer | No | Items per page (default: 10, max: 100) | `limit=20` |
| `type` | string | No | Filter by type (email, push, sms) | `type=email` |
| `category` | string | No | Filter by category | `category=onboarding` |
| `search` | string | No | Search in name/description | `search=welcome` |

**Example Request:**
```bash
curl -X GET "http://template-service:3004/api/v1/templates?page=1&limit=10&type=email" \
  -H "Content-Type: application/json"
```

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "template_id": "welcome_email",
      "name": "Welcome Email",
      "type": "email",
      "category": "onboarding",
      "is_active": true,
      "current_version": {
        "version": "1.0.0",
        "subject": "Welcome {{name}}!",
        "variables": ["name", "company_name"]
      }
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "template_id": "password_reset",
      "name": "Password Reset",
      "type": "email",
      "category": "security",
      "is_active": true,
      "current_version": {
        "version": "1.0.0",
        "subject": "Reset Your Password",
        "variables": ["name", "reset_link"]
      }
    }
  ],
  "message": "Templates retrieved successfully",
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

#### 4. Add Translation
```http
POST /api/v1/templates/{template_id}/translations
```

**Purpose**: Add or update translation for a template.

**Request Body:**
```json
{
  "language_code": "es",
  "subject": "¡Bienvenido {{name}} a {{company_name}}!",
  "body": "Hola {{name}},\n\n¡Bienvenido a {{company_name}}!"
}
```

**Example Request:**
```bash
curl -X POST "http://template-service:3004/api/v1/templates/welcome_email/translations" \
  -H "Content-Type: application/json" \
  -d '{
    "language_code": "es",
    "subject": "¡Bienvenido {{name}} a {{company_name}}!",
    "body": "Hola {{name}},\n\n¡Bienvenido a {{company_name}}!"
  }'
```

**Success Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "template_id": "welcome_email",
    "language_code": "es",
    "created_at": "2025-11-10T11:00:00Z"
  },
  "message": "Translation added successfully",
  "meta": {
    "total": 1,
    "limit": 10,
    "page": 1,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  }
}
```

---

#### 5. Get Version History
```http
GET /api/v1/templates/{template_id}/versions
```

**Purpose**: Get all versions of a template.

**Example Request:**
```bash
curl -X GET "http://template-service:3004/api/v1/templates/welcome_email/versions" \
  -H "Content-Type: application/json"
```

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "version": "1.0.1",
      "subject": "Welcome {{name}}! Updated",
      "body": "Hi {{name}}, welcome!",
      "variables": ["name"],
      "is_current": true,
      "created_at": "2025-11-10T12:00:00Z",
      "metadata": {"updated_from": "1.0.0"}
    },
    {
      "id": "990e8400-e29b-41d4-a716-446655440004",
      "version": "1.0.0",
      "subject": "Welcome {{name}}!",
      "body": "Hi {{name}}!",
      "variables": ["name"],
      "is_current": false,
      "created_at": "2025-11-10T10:00:00Z",
      "metadata": {"initial_version": true}
    }
  ],
  "message": "Template versions retrieved successfully",
  "meta": {
    "total": 2,
    "limit": 10,
    "page": 1,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  }
}
```

---

### Available Templates (After Seeding)

After running `python scripts/seed_templates.py`, these templates are available:

| Template ID | Type | Description | Required Variables |
|------------|------|-------------|-------------------|
| `welcome_email` | email | Welcome new users | `name`, `company_name`, `verification_link` |
| `password_reset` | email | Password reset | `name`, `reset_link`, `expiry_hours` |
| `order_confirmation` | email | Order confirmation | `name`, `order_id`, `total`, `order_date`, `items`, `tracking_url` |
| `order_shipped` | push | Order shipped notification | `name`, `order_id`, `tracking_url` |
| `promotional_offer` | email | Marketing promotion | `name`, `discount`, `promo_code`, `expiry_date`, `shop_url` |
| `account_alert` | push | Security alert | `alert_message` |
| `payment_received` | email | Payment confirmation | `name`, `amount`, `payment_method`, `transaction_id`, `payment_date` |
| `subscription_reminder` | email | Subscription renewal | `name`, `plan_name`, `renewal_date`, `amount`, `payment_method`, `account_url` |
| `new_message` | push | New message notification | `sender_name`, `message_preview` |
| `account_verification` | email | Email verification | `name`, `verification_code`, `verification_link`, `expiry_minutes` |

---