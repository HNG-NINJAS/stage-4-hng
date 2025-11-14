# Example API Requests

Complete collection of curl commands to test the notification system.

## API Gateway Endpoints

### Health Check

```bash
curl http://localhost:3000/health
```

### Service Info

```bash
curl http://localhost:3000/
```

## Push Notifications

### Send Push Notification

```bash
curl -X POST http://localhost:3000/notify/push \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "template_id": "welcome_notification",
    "template_data": {
      "name": "John Doe",
      "app_name": "MyApp"
    },
    "device_token": "ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]",
    "language_code": "en",
    "priority": "high"
  }'
```

### Send Order Shipped Push Notification

```bash
curl -X POST http://localhost:3000/notify/push \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-456",
    "template_id": "order_shipped",
    "template_data": {
      "name": "Jane Smith",
      "order_id": "ORD-12345",
      "tracking_url": "https://track.example.com/12345"
    },
    "device_token": "test-device-token",
    "language_code": "en",
    "priority": "normal"
  }'
```

## Email Notifications

### Send Welcome Email

```bash
curl -X POST http://localhost:3000/notify/email \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-789",
    "template_id": "welcome_email",
    "template_data": {
      "name": "Alice Johnson",
      "company_name": "Acme Corp"
    },
    "recipient_email": "alice@example.com",
    "language_code": "en"
  }'
```

### Send Password Reset Email

```bash
curl -X POST http://localhost:3000/notify/email \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-101",
    "template_id": "password_reset",
    "template_data": {
      "name": "Bob Wilson",
      "reset_link": "https://app.example.com/reset?token=abc123"
    },
    "recipient_email": "bob@example.com",
    "language_code": "en"
  }'
```

### Send Spanish Email

```bash
curl -X POST http://localhost:3000/notify/email \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-202",
    "template_id": "welcome_email",
    "template_data": {
      "name": "Carlos García",
      "company_name": "Mi Empresa"
    },
    "recipient_email": "carlos@example.com",
    "language_code": "es"
  }'
```

## Template Service (Direct Access)

### List All Templates

```bash
curl http://localhost:3004/api/v1/templates
```

### Get Specific Template

```bash
curl http://localhost:3004/api/v1/templates/welcome_email
```

### Render Template

```bash
curl -X POST http://localhost:3004/api/v1/templates/welcome_email/render \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "name": "Test User",
      "company_name": "Test Company"
    },
    "language_code": "en"
  }'
```

### Create New Template

```bash
curl -X POST http://localhost:3004/api/v1/templates \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "custom_notification",
    "name": "Custom Notification",
    "type": "push",
    "subject": "Hello {{name}}!",
    "body": "This is a custom message for {{name}}.",
    "is_active": true
  }'
```

### Add Translation

```bash
curl -X POST http://localhost:3004/api/v1/templates/welcome_email/translations \
  -H "Content-Type: application/json" \
  -d '{
    "language_code": "fr",
    "subject": "Bienvenue {{name}}!",
    "body": "Bonjour {{name}}, bienvenue chez {{company_name}}!"
  }'
```

## Push Service (Direct Access)

### Health Check

```bash
curl http://localhost:3003/health
```

### Service Info

```bash
curl http://localhost:3003/
```

## Email Service (Direct Access)

### Health Check

```bash
curl http://localhost:3005/health
```

### Service Info

```bash
curl http://localhost:3005/
```

## User Service (Direct Access)

### Health Check

```bash
curl http://localhost:3001/health
```

## Batch Testing

### Send 10 Push Notifications

```bash
for i in {1..10}; do
  curl -X POST http://localhost:3000/notify/push \
    -H "Content-Type: application/json" \
    -d "{
      \"user_id\": \"user-$i\",
      \"template_id\": \"welcome_notification\",
      \"template_data\": {
        \"name\": \"User $i\",
        \"app_name\": \"MyApp\"
      },
      \"device_token\": \"token-$i\"
    }"
  echo ""
  sleep 0.5
done
```

### Send 10 Email Notifications

```bash
for i in {1..10}; do
  curl -X POST http://localhost:3000/notify/email \
    -H "Content-Type: application/json" \
    -d "{
      \"user_id\": \"user-$i\",
      \"template_id\": \"welcome_email\",
      \"template_data\": {
        \"name\": \"User $i\",
        \"company_name\": \"Test Company\"
      },
      \"recipient_email\": \"user$i@example.com\"
    }"
  echo ""
  sleep 0.5
done
```

## Error Testing

### Missing Required Fields

```bash
curl -X POST http://localhost:3000/notify/push \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123"
  }'
```

Expected: 400 Bad Request

### Invalid Template ID

```bash
curl -X POST http://localhost:3000/notify/email \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "template_id": "nonexistent_template",
    "template_data": {},
    "recipient_email": "test@example.com"
  }'
```

Expected: Template not found error in logs

## Monitoring

### Check RabbitMQ Queues

```bash
# Via API (requires auth)
curl -u admin:admin123 http://localhost:15672/api/queues

# Via CLI
docker-compose exec rabbitmq rabbitmqctl list_queues
```

### Check Redis

```bash
docker-compose exec redis redis-cli -a redis123 INFO
```

### Check Database

```bash
# Template Service DB
docker-compose exec postgres_template psql -U admin -d template_service -c "SELECT COUNT(*) FROM templates;"

# User Service DB
docker-compose exec postgres_user psql -U admin -d user_service -c "\dt"
```

## Using with Postman

Import these as a Postman collection:

1. Create new collection "Notification System"
2. Add environment variables:
   - `base_url`: http://localhost:3000
   - `template_service_url`: http://localhost:3004
3. Import requests from this file

## Using with HTTPie

If you prefer HTTPie:

```bash
# Push notification
http POST localhost:3000/notify/push \
  user_id=user-123 \
  template_id=welcome_notification \
  template_data:='{"name":"John","app_name":"MyApp"}' \
  device_token=test-token

# Email notification
http POST localhost:3000/notify/email \
  user_id=user-456 \
  template_id=welcome_email \
  template_data:='{"name":"Jane","company_name":"Acme"}' \
  recipient_email=jane@example.com
```

## Response Examples

### Successful Push Notification

```json
{
  "success": true,
  "message": "Push notification queued successfully",
  "data": {
    "message_id": "550e8400-e29b-41d4-a716-446655440000",
    "correlation_id": "550e8400-e29b-41d4-a716-446655440001",
    "status": "queued"
  }
}
```

### Successful Email Notification

```json
{
  "success": true,
  "message": "Email notification queued successfully",
  "data": {
    "message_id": "550e8400-e29b-41d4-a716-446655440002",
    "correlation_id": "550e8400-e29b-41d4-a716-446655440003",
    "status": "queued"
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": "VALIDATION_ERROR",
  "message": "Missing required fields: user_id, template_id, device_token"
}
```
