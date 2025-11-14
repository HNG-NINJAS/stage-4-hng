# Project Structure

Complete file structure of the Notification System.

```
notification-system/
│
├── README.md                          # Main documentation
├── START_HERE.md                      # Quick start guide (START HERE!)
├── QUICK_START.md                     # 5-minute setup guide
├── TEST_SYSTEM.md                     # Complete testing guide
├── EXAMPLE_REQUESTS.md                # Curl command examples
├── SYSTEM_SUMMARY.md                  # Architecture summary
├── DEPLOYMENT.md                      # Production deployment guide
├── PROJECT_STRUCTURE.md               # This file
├── docker-compose.yml                 # Complete system orchestration
├── .gitignore                         # Git ignore rules
│
├── docs/                              # Documentation
│   └── DOCKER_COMPOSE_EXPLAINED.md    # Docker setup explained
│
├── scripts/                           # Utility scripts
│   ├── test_all_services.sh          # Test all services
│   └── seed_and_test.sh              # One-command setup
│
└── services/                          # Microservices
    │
    ├── api-gateway/                   # API Gateway (Node.js/Express)
    │   ├── src/
    │   │   └── index.ts              # Main application
    │   ├── package.json              # Dependencies
    │   ├── tsconfig.json             # TypeScript config
    │   ├── Dockerfile                # Container image
    │   ├── .dockerignore             # Docker ignore
    │   ├── .gitignore                # Git ignore
    │   ├── .env                      # Environment variables
    │   └── README.md                 # Service documentation
    │
    ├── template-service/              # Template Service (Python/FastAPI)
    │   ├── app/
    │   │   ├── __init__.py
    │   │   ├── main.py               # FastAPI application
    │   │   ├── config.py             # Configuration
    │   │   ├── models.py             # Pydantic models
    │   │   ├── database.py           # Database connection
    │   │   ├── api/                  # API routes
    │   │   │   ├── templates.py      # Template endpoints
    │   │   │   ├── health.py         # Health checks
    │   │   │   └── metrics.py        # Prometheus metrics
    │   │   ├── services/             # Business logic
    │   │   ├── utils/                # Utilities
    │   │   │   ├── rabbitmq.py       # RabbitMQ client
    │   │   │   └── cache.py          # Redis cache
    │   │   └── workers/              # Background workers
    │   ├── alembic/                  # Database migrations
    │   │   ├── versions/             # Migration files
    │   │   └── env.py                # Alembic config
    │   ├── scripts/
    │   │   └── seed_templates.py     # Seed sample templates
    │   ├── tests/                    # Unit tests
    │   ├── requirements.txt          # Python dependencies
    │   ├── requirements-dev.txt      # Dev dependencies
    │   ├── alembic.ini               # Alembic config
    │   ├── Dockerfile                # Container image
    │   ├── .dockerignore             # Docker ignore
    │   ├── .gitignore                # Git ignore
    │   ├── .env                      # Environment variables
    │   └── README.md                 # Service documentation
    │
    ├── push-service/                  # Push Service (Python/FastAPI)
    │   ├── app/
    │   │   ├── __init__.py
    │   │   ├── main.py               # FastAPI application
    │   │   ├── config.py             # Configuration
    │   │   ├── models.py             # Pydantic models
    │   │   ├── services/
    │   │   │   ├── fcm_service.py    # Firebase FCM client
    │   │   │   ├── notification_service.py  # Business logic
    │   │   │   └── template_client.py       # Template Service client
    │   │   ├── workers/
    │   │   │   └── queue_consumer.py # RabbitMQ consumer
    │   │   └── utils/
    │   │       └── response.py       # API responses
    │   ├── scripts/
    │   │   ├── test_push_service.sh  # Test script
    │   │   └── publish_test_notification.py  # Test publisher
    │   ├── requirements.txt          # Python dependencies
    │   ├── Dockerfile                # Container image
    │   ├── .dockerignore             # Docker ignore
    │   ├── .gitignore                # Git ignore
    │   ├── .env                      # Environment variables
    │   ├── .env.example              # Environment template
    │   └── README.md                 # Service documentation
    │
    ├── email-service/                 # Email Service (Python/FastAPI)
    │   ├── app/
    │   │   ├── __init__.py
    │   │   ├── main.py               # FastAPI application
    │   │   ├── config.py             # Configuration
    │   │   ├── models.py             # Pydantic models
    │   │   ├── services/
    │   │   │   ├── email_service.py  # Email sending logic
    │   │   │   └── template_client.py # Template Service client
    │   │   └── workers/
    │   │       └── queue_consumer.py # RabbitMQ consumer
    │   ├── requirements.txt          # Python dependencies
    │   ├── Dockerfile                # Container image
    │   ├── .dockerignore             # Docker ignore
    │   ├── .gitignore                # Git ignore
    │   ├── .env                      # Environment variables
    │   └── README.md                 # Service documentation
    │
    └── user-service/                  # User Service (NestJS/TypeScript)
        └── packages/
            ├── src/
            │   ├── main.ts           # Application entry
            │   ├── app.module.ts     # Root module
            │   ├── auth/             # Authentication
            │   │   ├── auth.controller.ts
            │   │   ├── auth.service.ts
            │   │   ├── auth.module.ts
            │   │   ├── guards/       # JWT guards
            │   │   ├── decorators/   # Custom decorators
            │   │   └── dto/          # Data transfer objects
            │   ├── users/            # User management
            │   │   ├── users.controller.ts
            │   │   ├── users.service.ts
            │   │   ├── users.module.ts
            │   │   └── dto/
            │   ├── preferences/      # Notification preferences
            │   │   ├── preferences.controller.ts
            │   │   ├── preferences.service.ts
            │   │   ├── preferences.module.ts
            │   │   └── dto/
            │   ├── push-tokens/      # Device tokens
            │   │   ├── push-tokens.controller.ts
            │   │   ├── push-tokens.service.ts
            │   │   ├── push-tokens.module.ts
            │   │   └── dto/
            │   ├── health/           # Health checks
            │   │   ├── health.controller.ts
            │   │   └── health.module.ts
            │   ├── prisma/           # Database ORM
            │   │   ├── prisma.service.ts
            │   │   └── prisma.module.ts
            │   └── common/           # Shared utilities
            ├── prisma/
            │   ├── schema.prisma     # Database schema
            │   └── seed.ts           # Database seeding
            ├── test/                 # Tests
            ├── package.json          # Dependencies
            ├── tsconfig.json         # TypeScript config
            ├── nest-cli.json         # NestJS config
            ├── Dockerfile            # Container image
            ├── .gitignore            # Git ignore
            └── README.md             # Service documentation
```

## Key Files

### Root Level

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Orchestrates all services and infrastructure |
| `START_HERE.md` | Quick start guide - **START HERE!** |
| `README.md` | Main documentation and overview |
| `QUICK_START.md` | 5-minute setup guide |
| `TEST_SYSTEM.md` | Complete testing guide |
| `EXAMPLE_REQUESTS.md` | Curl command examples |
| `SYSTEM_SUMMARY.md` | Architecture and system summary |
| `DEPLOYMENT.md` | Production deployment guide |
| `PROJECT_STRUCTURE.md` | This file |

### Scripts

| File | Purpose |
|------|---------|
| `scripts/test_all_services.sh` | Tests all services and infrastructure |
| `scripts/seed_and_test.sh` | One-command setup and test |

### API Gateway

| File | Purpose |
|------|---------|
| `src/index.ts` | Main Express application |
| `package.json` | Node.js dependencies |
| `Dockerfile` | Container image definition |
| `.env` | Environment configuration |

### Template Service

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI application |
| `app/config.py` | Configuration settings |
| `app/api/templates.py` | Template CRUD endpoints |
| `alembic/versions/` | Database migrations |
| `scripts/seed_templates.py` | Seed sample templates |
| `requirements.txt` | Python dependencies |

### Push Service

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI application |
| `app/services/fcm_service.py` | Firebase FCM integration |
| `app/services/notification_service.py` | Business logic |
| `app/workers/queue_consumer.py` | RabbitMQ consumer |
| `scripts/publish_test_notification.py` | Test message publisher |

### Email Service

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI application |
| `app/services/email_service.py` | Email sending logic (mock) |
| `app/workers/queue_consumer.py` | RabbitMQ consumer |

### User Service

| File | Purpose |
|------|---------|
| `src/main.ts` | NestJS application entry |
| `src/auth/` | Authentication module |
| `src/users/` | User management module |
| `src/preferences/` | Notification preferences |
| `src/push-tokens/` | Device token management |
| `prisma/schema.prisma` | Database schema |

## Service Ports

| Service | Port | Protocol |
|---------|------|----------|
| API Gateway | 3000 | HTTP |
| User Service | 3001 | HTTP |
| Push Service | 3003 | HTTP |
| Template Service | 3004 | HTTP |
| Email Service | 3005 | HTTP |
| RabbitMQ | 5672 | AMQP |
| RabbitMQ Management | 15672 | HTTP |
| Redis | 6379 | Redis |
| PostgreSQL (Template) | 5433 | PostgreSQL |
| PostgreSQL (User) | 5432 | PostgreSQL |
| Prometheus | 9090 | HTTP |
| Grafana | 3005 | HTTP |

## Technology Stack

### Languages
- **TypeScript** - API Gateway, User Service
- **Python** - Template Service, Push Service, Email Service

### Frameworks
- **Express** - API Gateway
- **FastAPI** - Template Service, Push Service, Email Service
- **NestJS** - User Service

### Databases
- **PostgreSQL** - Template Service, User Service
- **Redis** - Caching

### Message Queue
- **RabbitMQ** - Async communication

### Monitoring
- **Prometheus** - Metrics collection
- **Grafana** - Visualization

### Container
- **Docker** - Containerization
- **Docker Compose** - Orchestration

## Data Flow

### Push Notification
```
Client
  → API Gateway (POST /notify/push)
  → RabbitMQ (push.queue)
  → Push Service (consumer)
  → Template Service (render template)
  → Firebase FCM (send notification)
```

### Email Notification
```
Client
  → API Gateway (POST /notify/email)
  → RabbitMQ (email.queue)
  → Email Service (consumer)
  → Template Service (render template)
  → SMTP Server (send email)
```

## Configuration Files

### Docker
- `docker-compose.yml` - Service orchestration
- `Dockerfile` - Each service has its own

### Environment
- `.env` - Each service has environment variables
- `.env.example` - Template for environment variables

### TypeScript
- `tsconfig.json` - TypeScript configuration
- `nest-cli.json` - NestJS configuration

### Python
- `requirements.txt` - Python dependencies
- `alembic.ini` - Database migration config

## Getting Started

1. **Read**: [START_HERE.md](./START_HERE.md)
2. **Setup**: Run `bash scripts/seed_and_test.sh`
3. **Test**: See [TEST_SYSTEM.md](./TEST_SYSTEM.md)
4. **Examples**: See [EXAMPLE_REQUESTS.md](./EXAMPLE_REQUESTS.md)
5. **Deploy**: See [DEPLOYMENT.md](./DEPLOYMENT.md)

## Documentation Index

| Document | Purpose | Audience |
|----------|---------|----------|
| START_HERE.md | Quick start | Everyone |
| README.md | Overview | Everyone |
| QUICK_START.md | Setup guide | Developers |
| TEST_SYSTEM.md | Testing | Developers |
| EXAMPLE_REQUESTS.md | API examples | Developers |
| SYSTEM_SUMMARY.md | Architecture | Architects |
| DEPLOYMENT.md | Production | DevOps |
| PROJECT_STRUCTURE.md | File structure | Developers |

## Service Documentation

Each service has its own README:
- [API Gateway README](./services/api-gateway/README.md)
- [Template Service README](./services/template-service/README.md)
- [Push Service README](./services/push-service/README.md)
- [Email Service README](./services/email-service/README.md)
- [User Service README](./services/user-service/packages/README.md)
