# Docker Compose Configuration Explained

This document explains our `docker-compose.yml` file for the entire Notification System team.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Services Breakdown](#services-breakdown)
4. [Networks & Volumes](#networks--volumes)
5. [Starting Services](#starting-services)
6. [Troubleshooting](#troubleshooting)

---

## Overview

Our `docker-compose.yml` orchestrates **all microservices and infrastructure** for the Notification System. It includes:

- **3 Infrastructure Services** (RabbitMQ, Redis, PostgreSQL)
- **5 Microservices** (API Gateway, User, Template, Email, Push)
- **3 Monitoring Tools** (Prometheus, Grafana, Jaeger)

**Benefits of Docker Compose:**

- ✅ Start entire system with one command
- ✅ Services can find each other by name
- ✅ Automatic network configuration
- ✅ Easy to scale services
- ✅ Consistent environment for all team members

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network                            │
│                 (notification_network)                       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   RabbitMQ   │  │    Redis     │  │  PostgreSQL  │     │
│  │   :5672      │  │    :6379     │  │   :5432/5433 │     │
│  │ Management   │  │              │  │              │     │
│  │   :15672     │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         ▲                 ▲                  ▲              │
│         │                 │                  │              │
│  ┌──────┴─────────────────┴──────────────────┴───────┐     │
│  │                                                     │     │
│  │              Microservices Layer                   │     │
│  │                                                     │     │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐          │     │
│  │  │   API    │ │   User   │ │ Template │          │     │
│  │  │ Gateway  │ │ Service  │ │ Service  │          │     │
│  │  │  :3000   │ │  :3001   │ │  :3004   │          │     │
│  │  └──────────┘ └──────────┘ └──────────┘          │     │
│  │                                                     │     │
│  │  ┌──────────┐ ┌──────────┐                       │     │
│  │  │  Email   │ │   Push   │                       │     │
│  │  │ Service  │ │ Service  │                       │     │
│  │  │  :3002   │ │  :3003   │                       │     │
│  │  └──────────┘ └──────────┘                       │     │
│  └─────────────────────────────────────────────────┘     │
│                          │                                 │
│                          ▼                                 │
│  ┌───────────────────────────────────────────────┐       │
│  │          Monitoring Layer                      │       │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐│       │
│  │  │ Prometheus │ │  Grafana   │ │   Jaeger   ││       │
│  │  │   :9090    │ │   :3005    │ │  :16686    ││       │
│  │  └────────────┘ └────────────┘ └────────────┘│       │
│  └───────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## Services Breakdown

### 1. RabbitMQ (Message Queue)

```yaml
rabbitmq:
  image: rabbitmq:3.12-management
  container_name: notification_rabbitmq
  ports:
    - "5672:5672" # AMQP protocol port
    - "15672:15672" # Management UI port
  environment:
    RABBITMQ_DEFAULT_USER: admin
    RABBITMQ_DEFAULT_PASS: admin123
  volumes:
    - rabbitmq_data:/var/lib/rabbitmq
  networks:
    - notification_network
  healthcheck:
    test: rabbitmq-diagnostics -q ping
    interval: 10s
    timeout: 5s
    retries: 5
```

**Purpose**: Asynchronous message queue for service-to-service communication

**Ports:**

- `5672`: AMQP port (services connect here)
- `15672`: Web Management UI (http://localhost:15672)

**Credentials:**

- Username: `admin`
- Password: `admin123`

**Used By:**

- API Gateway → publishes notification requests
- Email Service → consumes email queue
- Push Service → consumes push queue
- Template Service → publishes template events

**Health Check**: Pings RabbitMQ every 10 seconds

**Data Persistence**: `rabbitmq_data` volume stores messages

---

### 2. Redis (Cache & Session Store)

```yaml
redis:
  image: redis:7-alpine
  container_name: notification_redis
  ports:
    - "6379:6379"
  command: redis-server --appendonly yes --requirepass redis123
  volumes:
    - redis_data:/data
  networks:
    - notification_network
  healthcheck:
    test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
    interval: 10s
    timeout: 5s
    retries: 5
```

**Purpose**: Caching layer for performance optimization

**Port:** `6379` (standard Redis port)

**Password:** `redis123`

**Connection String:** `redis://:redis123@redis:6379/0`

**Used By:**

- Template Service → caches frequently accessed templates
- User Service → caches user preferences
- API Gateway → rate limiting, session storage

**Features:**

- `---appendonly yes`: Data persistence (survives restarts)
- `---requirepass redis123`: Password protection

**Data Persistence**: `redis_data` volume stores cached data

### 3. PostgreSQL Databases

PostgreSQL - User Service

```yaml
postgres_user:
  image: postgres:15-alpine
  container_name: notification_postgres_user
  environment:
    POSTGRES_DB: user_service
    POSTGRES_USER: admin
    POSTGRES_PASSWORD: admin123
  ports:
    - "5432:5432"
  volumes:
    - postgres_user_data:/var/lib/postgresql/data
  networks:
    - notification_network
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U admin -d user_service"]
    interval: 10s
    timeout: 5s
    retries: 5
```

**Purpose**: Database for User Service (user data, preferences)

**Port:** `5432` (standard PostgreSQL port)

**Connection String:**

```
postgresql://admin:admin123@postgres_user:5432/user_service
```

From Host Machine:

```
psql -h localhost -p 5432 -U admin -d user_service
# Password: admin123
```

**Used By:** User Service only

**Data Persistence:** `postgres_user_data` volume stores user data
PostgreSQL - Template Service

```yaml
postgres_template:
  image: postgres:15-alpine
  container_name: notification_postgres_template
  environment:
    POSTGRES_DB: template_service
    POSTGRES_USER: admin
    POSTGRES_PASSWORD: admin123
  ports:
    - "5433:5432" # Note: External port 5433, internal port 5432
  volumes:
    - postgres_template_data:/var/lib/postgresql/data
  networks:
    - notification_network
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U admin -d template_service"]
    interval: 10s
    timeout: 5s
    retries: 5
```

**Purpose**: Database for Template Service (templates, versions, translations)

**Ports:**

- External: `5433` (from your laptop)
- Internal: `5432` (from other containers)

**Why Different External Port?**

- Avoids port conflict with User Service PostgreSQL
- Both services can run simultaneously

**Connection Strings:**

From Docker containers:

```
postgresql://admin:admin123@postgres_template:5432/template_service
```

From your laptop:

```
postgresql://admin:admin123@localhost:5433/template_service
```

**Used By:** Template Service only

**Data Persistence:** `postgres_template_data` volume stores template data

### 4. Prometheus (Metrics Collection)

```yaml
prometheus:
  image: prom/prometheus:latest
  container_name: notification_prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus
  command:
    - "--config.file=/etc/prometheus/prometheus.yml"
    - "--storage.tsdb.path=/prometheus"
  networks:
    - notification_network
  restart: unless-stopped
```

**Purpose**: Collects metrics from all services
**Port:** `9090` → http://localhost:9090
**Configuration:** `monitoring/prometheus.yml` (scrape configs)

**Scrapes Metrics From:**

- API Gateway `:3000/metrics`
- User Service `:3001/metrics`
- Template Service `:3004/metrics`
- Email Service `:3002/metrics`
- Push Service `:3003/metrics`

**Features:**

- Time-series database
- Query language (PromQL)
- Alerting capabilities

**Data Persistence:** `prometheus_data` volume

### 5. Grafana (Metrics Visualization)

```yaml
grafana:
  image: grafana/grafana:latest
  container_name: notification_grafana
  ports:
    - "3005:3000" # External 3005, internal 3000
  environment:
    - GF_SECURITY_ADMIN_USER=admin
    - GF_SECURITY_ADMIN_PASSWORD=admin123
    - GF_USERS_ALLOW_SIGN_UP=false
  volumes:
    - grafana_data:/var/lib/grafana
    - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
  networks:
    - notification_network
  restart: unless-stopped
```

**Purpose**: Visualize metrics from Prometheus
**Port:** `3005` → http://localhost:3005
**Credentials:**

- Username: `admin`
- Password: `admin123`

**Features:**

- Beautiful dashboards
- Alerts and notifications
- Multiple data sources

**Connects To:** Prometheus for metrics data
**Data Persistence:** `grafana_data` volume (dashboards, settings)

### 6. Jaeger (Distributed Tracing)

```yml
jaeger:
  image: jaegertracing/all-in-one:latest
  container_name: notification_jaeger
  ports:
    - "16686:16686" # Jaeger UI
    - "14268:14268" # HTTP collector
    - "6831:6831/udp" # Compact thrift protocol
  environment:
    - COLLECTOR_ZIPKIN_HOST_PORT=:9411
  networks:
    - notification_network
  restart: unless-stopped
```

**Purpose**: Track requests across microservices (distributed tracing)

**Ports:**

- `16686`: Web UI → http://localhost:16686
- `14268`: HTTP collector (services send traces here)
- `6831`: UDP collector

**Features:**

- Trace requests through multiple services
- Identify bottlenecks
- Visualize service dependencies
- Debug distributed systems

**How It Works:**

```
User Request → API Gateway (trace starts)
            → User Service (trace continues)
            → Template Service (trace continues)
            → Email Service (trace ends)
```

Each service adds its span to the trace with correlation IDs.

### 7. Template Service

```yml
template-service:
  build:
    context: ./services/template-service
    dockerfile: Dockerfile
  container_name: notification_template_service
  ports:
    - "3004:3004"
  environment:
    DATABASE_URL: postgresql://admin:admin123@postgres_template:5432/template_service
    REDIS_URL: redis://:redis123@redis:6379/0
    RABBITMQ_URL: amqp://admin:admin123@rabbitmq:5672/
    SERVICE_NAME: template-service
    SERVICE_VERSION: 1.0.0
    PORT: 3004
    ENVIRONMENT: development
    DEBUG: "True"
    LOG_LEVEL: INFO
  depends_on:
    postgres_template:
      condition: service_healthy
    redis:
      condition: service_healthy
    rabbitmq:
      condition: service_healthy
  networks:
    - notification_network
  volumes:
    - ./services/template-service:/app
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:3004/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
  restart: unless-stopped
```

**Purpose:** Manages notification templates
**Port:** `3004` → http://localhost:3004
**Build Context:** Builds from `./services/template-service/Dockerfile`
**Environment Variables:**

- `DATABASE_URL`: Connection to postgres_template
- `REDIS_URL`: Connection to Redis
- `RABBITMQ_URL`: Connection to RabbitMQ
