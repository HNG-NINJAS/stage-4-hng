# API Gateway

Minimal API Gateway for the Notification System. Routes notification requests to appropriate services via RabbitMQ.

## Features

- ✅ Single entry point for all notification requests
- ✅ Routes push notifications to Push Service
- ✅ Routes email notifications to Email Service
- ✅ RabbitMQ message queue integration
- ✅ Health checks for all dependencies
- ✅ Correlation ID tracking

## Endpoints

### POST /notify/push
Send push notification

**Request:**
```json
{
  "user_id": "user-123",
  "template_id": "welcome_notification",
  "template_data": {
    "name": "John Doe"
  },
  "device_token": "fcm-token-here",
  "language_code": "en",
  "priority": "high"
}
```

### POST /notify/email
Send email notification

**Request:**
```json
{
  "user_id": "user-123",
  "template_id": "welcome_email",
  "template_data": {
    "name": "John Doe"
  },
  "recipient_email": "john@example.com",
  "language_code": "en"
}
```

### GET /health
Health check endpoint

## Quick Start

```bash
npm install
npm run dev
```

## Docker

```bash
docker-compose up -d api-gateway
```
