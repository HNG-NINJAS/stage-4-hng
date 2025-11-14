# Notification System

A complete distributed microservices-based notification system with API Gateway, Template Service, Push Service, Email Service, and User Service.

## 🚀 Quick Start

```bash
# Start the system (one command)
./start.sh
```

This starts all services, seeds templates, and shows status.

**Test it:**
```bash
bash scripts/test_complete_system.sh
```

**See [GETTING_STARTED.md](./GETTING_STARTED.md) for detailed instructions.**

## 📋 System Overview

The system consists of 5 microservices working together:

```
┌─────────────────┐
│   API Gateway   │ :3000 (Node.js/Express)
│  Entry Point    │
└────────┬────────┘
         │
         ├─► RabbitMQ ─► Push Service :3003 ─► Template Service :3004
         │               (Python/FastAPI)      (Python/FastAPI)
         │
         ├─► RabbitMQ ─► Email Service :3005 ─► Template Service :3004
         │               (Python/FastAPI)       (Python/FastAPI)
         │
         └─► User Service :3001 (NestJS/TypeScript)
```

### Services

| Service              | Port | Technology        | Status  | Description                    |
| -------------------- | ---- | ----------------- | ------- | ------------------------------ |
| **API Gateway**      | 3000 | Node.js/Express   | ✅ Ready | Routes requests to services    |
| **Template Service** | 3004 | Python/FastAPI    | ✅ Ready | Manages notification templates |
| **Push Service**     | 3003 | Python/FastAPI    | ✅ Ready | Sends push notifications (FCM) |
| **Email Service**    | 3005 | Python/FastAPI    | ✅ Ready | Sends emails (mock mode)       |
| **User Service**     | 3001 | NestJS/TypeScript | ✅ Ready | Manages users & preferences    |

### Infrastructure

- **RabbitMQ** :5672, :15672 - Message queue
- **Redis** :6379 - Caching
- **PostgreSQL** :5433 - Template database (avoids port 5432 conflict)
- **Prometheus** :9090 - Metrics (optional)
- **Grafana** :3005 - Dashboards (optional)

## 🎯 Features

- ✅ **API Gateway** - Single entry point for all notifications
- ✅ **Template Management** - Multi-language templates with versioning
- ✅ **Push Notifications** - Firebase Cloud Messaging integration (mock mode)
- ✅ **Email Notifications** - SMTP integration (mock mode)
- ✅ **User Management** - User profiles and preferences
- ✅ **Message Queue** - RabbitMQ for async processing
- ✅ **Caching** - Redis for performance
- ✅ **Health Checks** - All services have health endpoints
- ✅ **Monitoring** - Prometheus metrics and Grafana dashboards
- ✅ **Docker** - Complete containerized deployment

## 📚 Documentation

### Getting Started
- **[GETTING_STARTED.md](./GETTING_STARTED.md)** - Quick start guide (5 minutes)
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Local and server deployment
- **[EXAMPLE_REQUESTS.md](./EXAMPLE_REQUESTS.md)** - API examples

### For Presentation
- **[DEMO_GUIDE.md](./DEMO_GUIDE.md)** - Complete demo script

### Architecture
- **[SYSTEM_SUMMARY.md](./SYSTEM_SUMMARY.md)** - System overview
- **[PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)** - File structure

### Service Documentation
- [API Gateway](./services/api-gateway/README.md)
- [Template Service](./services/template-service/README.md)
- [Push Service](./services/push-service/README.md)
- [Email Service](./services/email-service/README.md)
- [User Service](./services/user-service/packages/README.md)

## 🔌 Service Ports

| Service          | Port  | URL                       |
| ---------------- | ----- | ------------------------- |
| API Gateway      | 3000  | http://localhost:3000     |
| Push Service     | 3003  | http://localhost:3003     |
| Template Service | 3004  | http://localhost:3004     |
| Email Service    | 3005  | http://localhost:3005     |
| PostgreSQL       | 5433  | localhost:5433 (internal) |
| RabbitMQ         | 5672  | localhost:5672 (internal) |
| RabbitMQ UI      | 15672 | http://localhost:15672    |
| Redis            | 6379  | localhost:6379 (internal) |

**Note:** Port 5433 is used for PostgreSQL to avoid conflicts with local PostgreSQL on port 5432.

## 🔌 API Endpoints

### API Gateway (Port 3000)

#### Send Push Notification
```bash
POST /notify/push
{
  "user_id": "user-123",
  "template_id": "welcome_notification",
  "template_data": {"name": "John", "app_name": "MyApp"},
  "device_token": "fcm-token-here"
}
```

#### Send Email Notification
```bash
POST /notify/email
{
  "user_id": "user-456",
  "template_id": "welcome_email",
  "template_data": {"name": "Jane", "company_name": "Acme"},
  "recipient_email": "jane@example.com"
}
```

See [EXAMPLE_REQUESTS.md](./EXAMPLE_REQUESTS.md) for complete API examples.

## 🧪 Testing

### Run All Tests

```bash
bash scripts/test_all_services.sh
```

### Test Individual Services

```bash
# API Gateway
curl http://localhost:3000/health

# Template Service
curl http://localhost:3004/health

# Push Service
curl http://localhost:3003/health

# Email Service
curl http://localhost:3005/health

# User Service
curl http://localhost:3001/health
```

### Send Test Notifications

```bash
# Push notification
curl -X POST http://localhost:3000/notify/push \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "template_id": "welcome_notification",
    "template_data": {"name": "Test", "app_name": "MyApp"},
    "device_token": "test-token"
  }'

# Email notification
curl -X POST http://localhost:3000/notify/email \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "template_id": "welcome_email",
    "template_data": {"name": "Test", "company_name": "TestCo"},
    "recipient_email": "test@example.com"
  }'
```

## 📊 Monitoring

### Service URLs

- **API Gateway**: http://localhost:3000
- **Template Service**: http://localhost:3004/docs
- **Push Service**: http://localhost:3003/docs
- **Email Service**: http://localhost:3005/docs
- **User Service**: http://localhost:3001/health
- **RabbitMQ UI**: http://localhost:15672 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3005 (admin/admin123)

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api-gateway
docker-compose logs -f push-service
docker-compose logs -f email-service
```

### Check Queues

```bash
# RabbitMQ queues
docker-compose exec rabbitmq rabbitmqctl list_queues

# Or use web UI
open http://localhost:15672
```

## 🏗️ Architecture

### Message Flow

1. **Client** sends request to **API Gateway** (HTTP)
2. **API Gateway** publishes message to **RabbitMQ** queue
3. **Worker Service** (Push/Email) consumes message from queue
4. **Worker** fetches template from **Template Service** (HTTP)
5. **Worker** renders template with user data
6. **Worker** sends notification (FCM/SMTP)
7. **Worker** acknowledges message in queue

### Service Communication

- **API Gateway → RabbitMQ**: Publishes messages to queues
- **Workers → RabbitMQ**: Consume messages from queues
- **Workers → Template Service**: HTTP requests for templates
- **All Services → Redis**: Caching
- **All Services → PostgreSQL**: Data persistence

## 🛠️ Development

### Prerequisites

- Docker and Docker Compose
- 8GB RAM available
- Ports 3000-3005, 5432-5433, 5672, 6379, 15672 available

### Start Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d api-gateway

# Rebuild and start
docker-compose up -d --build api-gateway
```

### Stop Services

```bash
# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Local Development

Each service can be run locally. See service-specific READMEs for details.

## 🔧 Configuration

### Environment Variables

Services are configured via environment variables in `docker-compose.yml`:

- **API Gateway**: Port, service URLs, RabbitMQ URL
- **Template Service**: Database URL, Redis URL, RabbitMQ URL
- **Push Service**: RabbitMQ URL, Template Service URL, FCM credentials
- **Email Service**: RabbitMQ URL, Template Service URL, SMTP settings
- **User Service**: Database URL, JWT secret, Redis URL

### Mock Mode

Both Push and Email services run in **mock mode** by default:
- **Push Service**: Logs notifications instead of sending to FCM
- **Email Service**: Logs emails instead of sending via SMTP

To enable real sending:
1. **Push Service**: Add Firebase credentials and set `FCM_CREDENTIALS_PATH`
2. **Email Service**: Set `MOCK_MODE=False` and configure SMTP settings

## 🚀 Production Deployment

### Checklist

- [ ] Set `ENVIRONMENT=production` for all services
- [ ] Configure real FCM credentials for Push Service
- [ ] Configure real SMTP for Email Service
- [ ] Set strong passwords for databases and Redis
- [ ] Enable authentication on RabbitMQ
- [ ] Set up SSL/TLS certificates
- [ ] Configure monitoring and alerting
- [ ] Set up log aggregation
- [ ] Configure backup strategy
- [ ] Set resource limits in docker-compose.yml

### Scaling

```bash
# Scale workers
docker-compose up -d --scale push-service=3
docker-compose up -d --scale email-service=3
```

## 🐛 Troubleshooting

### Services not starting?

```bash
# Check logs
docker-compose logs [service-name]

# Check status
docker-compose ps
```

### Port conflicts?

```bash
# Check what's using the port
lsof -i :3000

# Change port in docker-compose.yml
```

### Database issues?

```bash
# Check database
docker-compose exec postgres_template psql -U admin -d template_service

# Run migrations
docker-compose exec template-service alembic upgrade head
```

### RabbitMQ issues?

```bash
# Check status
docker-compose exec rabbitmq rabbitmq-diagnostics status

# Check queues
docker-compose exec rabbitmq rabbitmqctl list_queues
```

### Clear everything and restart

```bash
docker-compose down -v
docker-compose up -d
sleep 30
docker-compose exec template-service python scripts/seed_templates.py
```

## 📝 License

MIT License

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## � Monitotring & Health Checks

### Quick Health Check

```bash
# Check all services
./scripts/health-check.sh

# Or manually
curl http://YOUR_EC2_IP:3000/health  # API Gateway
curl http://YOUR_EC2_IP:3004/health  # Template Service
curl http://YOUR_EC2_IP:3003/health  # Push Service
curl http://YOUR_EC2_IP:3005/health  # Email Service
```

### Monitor Logs

```bash
# Check for errors
./scripts/monitor-logs.sh

# View live logs
docker-compose -f docker-compose.minimal.yml logs -f

# View specific service
docker-compose -f docker-compose.minimal.yml logs api-gateway
```

### RabbitMQ Dashboard

Access at: `http://YOUR_EC2_IP:15672`
- Username: `admin`
- Password: `admin123`

For complete monitoring guide, see [docs/MONITORING.md](./docs/MONITORING.md)

## 📧 Support

For issues or questions:
1. Check service logs: `docker-compose logs [service-name]`
2. Run health checks: `./scripts/health-check.sh`
3. Review [docs/MONITORING.md](./docs/MONITORING.md)
4. Check service-specific READMEs
5. Open an issue on GitHub

## 🎉 Acknowledgments

Built with:
- Node.js & Express
- Python & FastAPI
- NestJS & TypeScript
- RabbitMQ
- Redis
- PostgreSQL
- Docker

---

**Ready to test?** See [QUICK_START.md](./QUICK_START.md) or [TEST_SYSTEM.md](./TEST_SYSTEM.md)
