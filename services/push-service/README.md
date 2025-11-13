# Push Service

Microservice for sending push notifications via Firebase Cloud Messaging (FCM).

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Architecture](#architecture)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

## Features

- ✅ Consumes messages from RabbitMQ queue
- ✅ Integrates with Template Service for content
- ✅ Sends push notifications via Firebase FCM
- ✅ Circuit breaker and retry logic
- ✅ Dead letter queue for failed messages
- ✅ Health checks and metrics
- ✅ Mock mode for testing (no FCM credentials needed)

## Prerequisites

- Python 3.11+
- Docker & Docker Compose (for infrastructure)
- RabbitMQ (via Docker)
- Template Service running (see `../template-service`)
- (Optional) Firebase project with FCM enabled

## Quick Start

### Local Development (Without Docker)

**Important:** When running locally, the `.env` file uses `localhost` for service URLs. When running in Docker, docker-compose.yml sets environment variables with Docker hostnames.

```bash
# 1. Set up environment
cp .env.example .env
# Note: .env uses localhost URLs for local development

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start infrastructure (RabbitMQ, Template Service, Redis)
# From repo root
docker-compose up -d rabbitmq template-service redis

# 5. Verify infrastructure is running
docker ps | grep -E "rabbitmq|template-service|redis"

# 6. Run service
uvicorn app.main:app --reload --port 3003
```

**Access:**
- Service: http://localhost:3003
- API Docs: http://localhost:3003/docs
- Health: http://localhost:3003/health

### With Docker

**Note:** docker-compose.yml automatically sets environment variables with Docker hostnames (`rabbitmq`, `template-service`, `redis`).

```bash
# From repo root
docker-compose up -d push-service

# View logs
docker-compose logs -f push-service

# Check health
curl http://localhost:3003/health
```

## Project Structure

```
push-service/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app & lifespan management
│   ├── config.py                  # Configuration settings
│   ├── models.py                  # Pydantic models
│   ├── services/
│   │   ├── fcm_service.py        # Firebase Cloud Messaging client
│   │   ├── notification_service.py # Business logic
│   │   └── template_client.py    # Template Service HTTP client
│   ├── workers/
│   │   └── queue_consumer.py     # RabbitMQ consumer
│   └── utils/
│       └── response.py            # API response helpers
├── scripts/
│   ├── test_push_service.sh      # Health check test script
│   └── publish_test_notification.py # Publish test message
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Container image
├── .env.example                   # Environment template
├── .env                          # Local config (git-ignored)
└── README.md                      # This file
```

## Configuration

### Environment Variables

| Variable | Description | Local Dev | Docker |
|----------|-------------|-----------|--------|
| `RABBITMQ_URL` | RabbitMQ connection URL | `amqp://admin:admin123@localhost:5672/` | `amqp://admin:admin123@rabbitmq:5672/` |
| `TEMPLATE_SERVICE_URL` | Template Service URL | `http://localhost:3004` | `http://template-service:3004` |
| `REDIS_URL` | Redis connection URL | `redis://:redis123@localhost:6379/1` | `redis://:redis123@redis:6379/1` |
| `FCM_CREDENTIALS_PATH` | Path to Firebase credentials JSON | Optional (mock mode) | Optional (mock mode) |
| `WORKER_ENABLED` | Enable RabbitMQ worker | `True` | `True` |
| `WORKER_PREFETCH_COUNT` | Messages to prefetch | `10` | `10` |
| `PORT` | Service port | `3003` | `3003` |
| `LOG_LEVEL` | Logging level | `INFO` | `INFO` |

**Configuration Files:**
- `.env` - Local development (uses `localhost`)
- `.env.example` - Template with both local and Docker examples
- `docker-compose.yml` - Sets environment variables for Docker deployment

### Firebase Setup (Optional)

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create new project
3. Go to Project Settings → Service Accounts
4. Generate new private key
5. Save as `firebase-credentials.json`
6. Set `FCM_CREDENTIALS_PATH=/app/firebase-credentials.json`

**Note:** Service runs in **mock mode** without FCM credentials (for testing).

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service info |
| GET | `/health` | Health check |
| GET | `/ready` | Readiness probe |
| GET | `/live` | Liveness probe |
| GET | `/metrics` | Prometheus metrics |
| GET | `/docs` | API documentation |

## Message Format

Push Service consumes messages from `push.queue`:
```json
{
  "message_id": "uuid",
  "correlation_id": "trace-id",
  "user_id": "123",
  "template_id": "order_shipped",
  "template_data": {
    "name": "John Doe",
    "order_id": "ORD-123",
    "tracking_url": "https://track.com/123"
  },
  "device_token": "fcm-device-token-here",
  "language_code": "en",
  "priority": "high",
  "retry_count": 0
}
```

## Testing

### 1. Test Service Health

```bash
# Run test script
bash scripts/test_push_service.sh

# Or manually
curl http://localhost:3003/health
curl http://localhost:3003/ready
```

### 2. Publish Test Notification

```bash
# Ensure Template Service is running and seeded
docker-compose up -d template-service
# Seed templates if needed: cd ../template-service && python scripts/seed_templates.py

# Publish test message to queue
python scripts/publish_test_notification.py

# Expected output:
# 📤 Publishing test notification...
#    RabbitMQ URL: amqp://admin:admin123@localhost:5672/
# ✅ Message published successfully!
```

### 3. Verify Message Processing

```bash
# Watch Push Service logs
docker-compose logs -f push-service

# You should see:
# 📥 Received push notification request
# 📱 [MOCK] Sending push notification:
# ✅ Push notification sent to user test-user-123
```

### 4. Check RabbitMQ Queue

Open RabbitMQ Management UI:
```bash
open http://localhost:15672
# Login: admin / admin123
# Navigate to Queues → push.queue
```

### Test Scripts

- `scripts/test_push_service.sh` - Tests health, readiness, and metrics endpoints
- `scripts/publish_test_notification.py` - Publishes a test message to the queue

## Architecture

```
┌─────────────────────┐
│  API Gateway /      │
│  Other Services     │
└──────────┬──────────┘
           │ publishes message
           ▼
┌─────────────────────┐
│   RabbitMQ Queue    │
│   (push.queue)      │
│   - Durable         │
│   - DLQ enabled     │
└──────────┬──────────┘
           │ consumes
           ▼
┌─────────────────────┐
│   Push Service      │
│   - Worker Thread   │
│   - Prefetch: 10    │
│   - Retry: 3x       │
└──────────┬──────────┘
           │
           ├─► Template Service
           │   (fetch & render template)
           │
           └─► Firebase FCM
               (send push notification)
                      │
                      ▼
               ┌──────────────┐
               │ User Device  │
               │ (iOS/Android)│
               └──────────────┘
```

**Flow:**
1. Service publishes message to `push.queue`
2. Push Service worker consumes message
3. Fetches template from Template Service
4. Renders template with user data
5. Sends push notification via FCM
6. Acknowledges message or sends to DLQ on failure

## Monitoring

### Prometheus Metrics
```bash
curl http://localhost:3003/metrics
```

**Available metrics:**
- `push_notifications_sent_total`
- `push_notifications_failed_total`
- `push_notification_duration_seconds`

### Health Check
```bash
curl http://localhost:3003/health
```

## Troubleshooting

### "Temporary failure in name resolution" Error

**Problem:** Service can't resolve hostnames like `rabbitmq`, `template-service`, `redis`

**Solution:**
- **Running locally?** Update `.env` to use `localhost` instead of Docker hostnames:
  ```bash
  RABBITMQ_URL=amqp://admin:admin123@localhost:5672/
  TEMPLATE_SERVICE_URL=http://localhost:3004
  REDIS_URL=redis://:redis123@localhost:6379/1
  ```
- **Running in Docker?** Use Docker hostnames (already set in docker-compose.yml)

### "PRECONDITION_FAILED - inequivalent arg" Error

**Problem:** Queue already exists with different configuration

**Solution:**
```bash
# Delete and recreate the queue
docker-compose exec rabbitmq rabbitmqctl delete_queue push.queue
# Restart push service to recreate queue
docker-compose restart push-service
```

### Worker Not Starting

```bash
# Check logs
docker-compose logs push-service

# Check RabbitMQ connection from container
docker-compose exec push-service python -c "import pika; pika.BlockingConnection(pika.URLParameters('amqp://admin:admin123@rabbitmq:5672/'))"

# Verify RabbitMQ is healthy
docker-compose ps rabbitmq
curl http://localhost:15672/api/healthchecks/node  # admin:admin123
```

### Messages Not Being Consumed

```bash
# 1. Check RabbitMQ queue has messages
open http://localhost:15672  # admin/admin123
# Go to Queues → push.queue

# 2. Check worker is enabled
docker-compose exec push-service env | grep WORKER_ENABLED

# 3. Check worker thread is alive
curl http://localhost:3003/health | jq '.data.dependencies.worker'
# Should return: "running"

# 4. Check for errors in logs
docker-compose logs --tail=50 push-service
```

### Template Service Connection Failed

```bash
# Check Template Service is running
curl http://localhost:3004/health

# Check from Push Service container
docker-compose exec push-service curl http://template-service:3004/health

# Check network connectivity
docker-compose exec push-service ping -c 3 template-service
```

### Port Already in Use

```bash
# Check what's using port 3003
lsof -i :3003

# Kill the process or change PORT in .env
PORT=3005 uvicorn app.main:app --reload
```

## Production Deployment

### Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=False`
- [ ] Set `LOG_LEVEL=WARNING` or `ERROR`
- [ ] Configure Firebase FCM credentials
- [ ] Set appropriate `WORKER_PREFETCH_COUNT` based on load
- [ ] Configure health check intervals
- [ ] Set up monitoring and alerting
- [ ] Configure resource limits (CPU/Memory)

### With Firebase FCM

1. Add Firebase credentials to container:
```yaml
push-service:
  volumes:
    - ./firebase-credentials.json:/app/firebase-credentials.json:ro
  environment:
    FCM_CREDENTIALS_PATH: /app/firebase-credentials.json
    FCM_PROJECT_ID: your-project-id
    ENVIRONMENT: production
    DEBUG: "False"
    LOG_LEVEL: WARNING
```

2. Verify FCM is working (not in mock mode):
```bash
curl http://localhost:3003/health | jq '.data.dependencies.fcm'
# Should return: "configured" (not "mock_mode")
```

### Scaling

```bash
# Run multiple instances (competing consumers)
docker-compose up -d --scale push-service=3

# Each instance will consume from the same queue
# RabbitMQ distributes messages across instances
```

**Scaling Considerations:**
- Adjust `WORKER_PREFETCH_COUNT` based on message processing time
- Monitor queue depth and consumer utilization
- Consider FCM rate limits (1 million messages per minute per project)

### Monitoring

**Key Metrics to Monitor:**
- `push_notifications_sent_total` - Total successful sends
- `push_notifications_failed_total` - Total failures
- `push_notification_duration_seconds` - Processing time
- Queue depth in RabbitMQ
- Worker thread health status
- FCM API response times

**Alerts to Set Up:**
- Worker thread down
- High failure rate (> 5%)
- Queue depth growing (> 1000 messages)
- High processing latency (> 5s)
- Template Service unavailable

## License

MIT