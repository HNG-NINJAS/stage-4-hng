# Getting Started

## Quick Start (5 Minutes)

### Prerequisites
- Docker and Docker Compose installed
- 8GB RAM available
- Ports 3000-3005, 5433, 5672, 6379, 15672 available

### Start the System

```bash
# One command to start everything
./start.sh
```

This will:
1. Start all 4 services (API Gateway, Template, Push, Email)
2. Start infrastructure (RabbitMQ, Redis, PostgreSQL)
3. Seed sample templates
4. Show service status

### Verify It's Working

```bash
# Run tests
bash scripts/test_complete_system.sh

# Check health
curl http://localhost:3000/health
```

### Send Test Notifications

**Push Notification:**
```bash
curl -X POST http://localhost:3000/notify/push \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "template_id": "welcome_notification",
    "template_data": {"name": "John", "app_name": "MyApp"},
    "device_token": "test-token"
  }'
```

**Email Notification:**
```bash
curl -X POST http://localhost:3000/notify/email \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-456",
    "template_id": "welcome_email",
    "template_data": {"name": "Jane", "company_name": "Acme"},
    "recipient_email": "jane@example.com"
  }'
```

### View Logs

```bash
# All services
docker-compose -f docker-compose.minimal.yml logs -f

# Specific service
docker-compose -f docker-compose.minimal.yml logs push-service
```

### Access UIs

- **API Gateway**: http://localhost:3000
- **Template Service API**: http://localhost:3004/docs
- **Push Service API**: http://localhost:3003/docs
- **Email Service API**: http://localhost:3005/docs
- **RabbitMQ Management**: http://localhost:15672 (admin/admin123)

## Next Steps

- **For Demo**: See [DEMO_GUIDE.md](./DEMO_GUIDE.md)
- **For Deployment**: See [DEPLOYMENT.md](./DEPLOYMENT.md)
- **For API Examples**: See [EXAMPLE_REQUESTS.md](./EXAMPLE_REQUESTS.md)
- **For Architecture**: See [README.md](./README.md)

## Troubleshooting

### Services won't start?
```bash
docker-compose -f docker-compose.minimal.yml logs
```

### Port conflicts?
The system uses port 5433 (not 5432) to avoid conflicts with local PostgreSQL.

### Need fresh start?
```bash
docker-compose -f docker-compose.minimal.yml down -v
./start.sh
```

## Common Commands

```bash
# Start
./start.sh

# Stop
docker-compose -f docker-compose.minimal.yml down

# Restart
docker-compose -f docker-compose.minimal.yml restart

# View logs
docker-compose -f docker-compose.minimal.yml logs -f

# Check status
docker-compose -f docker-compose.minimal.yml ps
```
