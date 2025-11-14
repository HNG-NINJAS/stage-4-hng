# Complete Demo Guide (Without User Service)

## Understanding the Architecture 

The notification system has **two independent parts**:

1. **Notification Flow** (Core) - Sends notifications
   - API Gateway
   - Template Service
   - Push Service
   - Email Service

2. **User Management** (Optional) - Manages users
   - User Service (authentication, preferences, CRUD)

**Key Point:** You can send notifications WITHOUT having users in a database!

## How to Demo All Features

### 1. Welcome Email Demo

**You don't need user-service to send welcome emails!**

```bash
# Send welcome email to ANY email address
curl -X POST http://localhost:3000/notify/email \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "new-user-123",
    "template_id": "welcome_email",
    "template_data": {
      "name": "John Doe",
      "company_name": "Acme Corp"
    },
    "recipient_email": "john.doe@example.com"
  }'
```

**Explanation:** 
- `user_id` is just a reference ID (doesn't need to exist in database)
- `recipient_email` is where the email goes
- Template Service renders the content
- Email Service sends it

### 2. Password Reset Email Demo

```bash
# Send password reset email
curl -X POST http://localhost:3000/notify/email \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-456",
    "template_id": "password_reset",
    "template_data": {
      "name": "Jane Smith",
      "reset_link": "https://app.example.com/reset?token=abc123xyz"
    },
    "recipient_email": "jane.smith@example.com"
  }'
```

### 3. Order Shipped Notification Demo

```bash
# Send order shipped notification
curl -X POST http://localhost:3000/notify/push \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "customer-789",
    "template_id": "order_shipped",
    "template_data": {
      "name": "Alice Johnson",
      "order_id": "ORD-12345",
      "tracking_url": "https://track.example.com/12345"
    },
    "device_token": "ExponentPushToken[xxxxxxxxxxxxxx]"
  }'
```

### 4. Multi-Language Support Demo

```bash
# Send Spanish welcome email
curl -X POST http://localhost:3000/notify/email \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-es-001",
    "template_id": "welcome_email",
    "template_data": {
      "name": "Carlos García",
      "company_name": "Mi Empresa"
    },
    "recipient_email": "carlos@example.com",
    "language_code": "es"
  }'
```

## What About User CRUD?

### Option 1: Explain the Architecture (Recommended)

**During presentation, say:**

"The notification system is designed with microservices architecture. We have:

1. **Notification Services** (running now) - Handle sending notifications
2. **User Service** (separate) - Handles user authentication and CRUD

The User Service is independent and optional. The notification services work with ANY user data - they don't require users to be in a database. This makes the system flexible and scalable."

### Option 2: Show User Service Documentation

Show the User Service README which documents all the CRUD operations:

```bash
# Show during demo
cat services/user-service/packages/README.md
```

Point out the endpoints:
- POST /users/register - User registration
- POST /auth/login - User login
- GET /users/me - Get user profile
- PUT /users/:id - Update user
- DELETE /users/:id - Delete user
- GET /users/:id/preferences - Get preferences
- PUT /users/:id/preferences - Update preferences

**Say:** "These endpoints are fully implemented and documented. The User Service can be deployed separately when user management is needed."

### Option 3: Show the Code

Open the User Service code and show:
- `services/user-service/packages/src/users/users.controller.ts` - CRUD endpoints
- `services/user-service/packages/src/auth/auth.controller.ts` - Authentication
- `services/user-service/packages/src/preferences/preferences.controller.ts` - Preferences

## Complete Demo Script

### Part 1: System Overview (2 minutes)

**Show:**
```bash
# Show running services
docker-compose -f docker-compose.minimal.yml ps

# Show architecture
cat README.md | head -50
```

**Say:**
"This is a microservices notification system with 4 core services:
- API Gateway for routing
- Template Service for managing notification templates
- Push Service for mobile notifications
- Email Service for email notifications

Plus RabbitMQ for message queuing, Redis for caching, and PostgreSQL for data storage."

### Part 2: Health Checks (1 minute)

```bash
curl http://localhost:3000/health | jq
curl http://localhost:3004/health | jq
curl http://localhost:3003/health | jq
curl http://localhost:3005/health | jq
```

**Say:**
"All services are healthy and ready to process notifications."

### Part 3: Template Management (2 minutes)

```bash
# List templates
curl http://localhost:3004/api/v1/templates | jq

# Get specific template
curl http://localhost:3004/api/v1/templates/welcome_email | jq

# Show template rendering
curl -X POST http://localhost:3004/api/v1/templates/welcome_email/render \
  -H "Content-Type: application/json" \
  -d '{
    "data": {"name": "Demo User", "company_name": "Demo Corp"},
    "language_code": "en"
  }' | jq
```

**Say:**
"The Template Service manages all notification templates with support for multiple languages and variable substitution."

### Part 4: Send Welcome Email (2 minutes)

```bash
# Send welcome email
curl -X POST http://localhost:3000/notify/email \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo-user-001",
    "template_id": "welcome_email",
    "template_data": {
      "name": "John Doe",
      "company_name": "Acme Corp"
    },
    "recipient_email": "john@example.com"
  }' | jq

# Show logs
docker-compose -f docker-compose.minimal.yml logs email-service | tail -20
```

**Say:**
"The request goes through API Gateway, gets queued in RabbitMQ, consumed by Email Service, template is rendered, and email is sent. In mock mode, we log the email content."

### Part 5: Send Password Reset (1 minute)

```bash
curl -X POST http://localhost:3000/notify/email \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-002",
    "template_id": "password_reset",
    "template_data": {
      "name": "Jane Smith",
      "reset_link": "https://app.example.com/reset?token=xyz123"
    },
    "recipient_email": "jane@example.com"
  }' | jq
```

**Say:**
"Password reset emails work the same way - any template can be used with any data."

### Part 6: Push Notification (2 minutes)

```bash
curl -X POST http://localhost:3000/notify/push \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "mobile-user-003",
    "template_id": "welcome_notification",
    "template_data": {
      "name": "Alice Johnson",
      "app_name": "MyApp"
    },
    "device_token": "ExponentPushToken[demo]"
  }' | jq

# Show logs
docker-compose -f docker-compose.minimal.yml logs push-service | tail -20
```

**Say:**
"Push notifications follow the same pattern - queued, processed, and sent to Firebase Cloud Messaging."

### Part 7: Multi-Language Support (1 minute)

```bash
# Spanish email
curl -X POST http://localhost:3000/notify/email \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-es-004",
    "template_id": "welcome_email",
    "template_data": {
      "name": "Carlos García",
      "company_name": "Mi Empresa"
    },
    "recipient_email": "carlos@example.com",
    "language_code": "es"
  }' | jq
```

**Say:**
"The system supports multiple languages. Templates can have translations for different locales."

### Part 8: RabbitMQ & Monitoring (2 minutes)

```bash
# Open RabbitMQ UI
open http://localhost:15672
```

**Say:**
"RabbitMQ manages the message queues. We can see the queues, message flow, and consumers in real-time."

**Show:**
- Queues tab
- push.queue and email.queue
- Message rates
- Consumers

### Part 9: API Documentation (1 minute)

```bash
# Open API docs
open http://localhost:3004/docs
```

**Say:**
"All services have OpenAPI documentation. Here you can see all available endpoints and try them interactively."

### Part 10: User Service Discussion (2 minutes)

**Show the README:**
```bash
cat services/user-service/packages/README.md | head -100
```

**Say:**
"The User Service is a separate microservice that handles:
- User registration and authentication
- User profile management
- Notification preferences
- Push token management

It's fully implemented with JWT authentication, Prisma ORM, and PostgreSQL. The service is independent and can be deployed separately when user management features are needed.

For this demo, we're focusing on the notification flow, which works with any user data - it doesn't require users to be in a database. This separation of concerns is a key benefit of microservices architecture."

**Show the code structure:**
```bash
ls -la services/user-service/packages/src/
```

**Point out:**
- `auth/` - Authentication endpoints
- `users/` - User CRUD operations
- `preferences/` - Notification preferences
- `push-tokens/` - Device token management

## Handling Questions

### Q: "Can you show user registration?"

**A:** "The User Service is fully implemented with registration endpoints. Let me show you the code and documentation."

```bash
# Show the controller
cat services/user-service/packages/src/users/users.controller.ts | head -50

# Show the README
cat services/user-service/packages/README.md | grep -A 20 "User Registration"
```

### Q: "How do users get added to the system?"

**A:** "The User Service provides REST APIs for user management. Applications can register users via POST /users/register, which creates the user in PostgreSQL with hashed passwords. The notification services then reference these users by ID."

### Q: "Why isn't User Service running?"

**A:** "For this demo, we're focusing on the notification flow. The User Service is independent and optional - notifications work with any user data. In production, you'd deploy User Service separately when you need user authentication and management features."

### Q: "Can you show the database schema?"

**A:** "Yes, here's the Prisma schema that defines the user data model."

```bash
cat services/user-service/packages/prisma/schema.prisma
```

## Deployment Without User Service

### Local Deployment

```bash
./start.sh
```

### Server Deployment

```bash
# On server
docker-compose -f docker-compose.minimal.yml build
docker-compose -f docker-compose.minimal.yml up -d
sleep 30
docker-compose -f docker-compose.minimal.yml exec template-service python scripts/seed_templates.py
```

### What Gets Deployed

- ✅ API Gateway (Port 3000)
- ✅ Template Service (Port 3004)
- ✅ Push Service (Port 3003)
- ✅ Email Service (Port 3005)
- ✅ RabbitMQ (Ports 5672, 15672)
- ✅ Redis (Port 6379)
- ✅ PostgreSQL (Port 5433)

### Service URLs

```
API Gateway:        http://YOUR_SERVER_IP:3000
Template Service:   http://YOUR_SERVER_IP:3004/docs
Push Service:       http://YOUR_SERVER_IP:3003/docs
Email Service:      http://YOUR_SERVER_IP:3005/docs
RabbitMQ UI:        http://YOUR_SERVER_IP:15672
```

## Summary

**You CAN demonstrate:**
- ✅ Welcome emails
- ✅ Password reset emails
- ✅ Order notifications
- ✅ Push notifications
- ✅ Multi-language support
- ✅ Template management
- ✅ Message queuing
- ✅ Health monitoring

**Without needing:**
- ❌ Users in database
- ❌ User authentication
- ❌ User CRUD operations running

**For User CRUD questions:**
- Show the documentation
- Show the code
- Explain it's a separate microservice
- Emphasize the benefits of separation

## Key Talking Points

1. **Microservices Architecture**: "Each service is independent and can be deployed separately."

2. **Separation of Concerns**: "Notification services don't need to know about user authentication - they just send notifications."

3. **Flexibility**: "The system works with any user data - from your database, from an API, or hardcoded for testing."

4. **Scalability**: "Each service can be scaled independently based on load."

5. **Production Ready**: "All services are fully implemented, documented, and ready for production deployment."

## Status: ✅ READY TO DEMO

You can demonstrate ALL features without User Service running!
