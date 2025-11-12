# Template Service Documentation

Welcome to the Template Service documentation. This service manages notification templates with multi-language support, version control, and event-driven architecture.

## 📚 Documentation Index

### Getting Started
- [Quick Start Guide](./getting-started.md) - Setup and run the service
- [API Reference](./api-reference.md) - Complete API documentation

### Integration Guides
- [Integration Overview](./integration/overview.md) - Integration patterns and best practices
- [Python Client](./integration/python-client.md) - Python/FastAPI integration
- [TypeScript/NestJS Client](./integration/typescript-client.md) - Node.js/NestJS integration
- [C# Client](./integration/csharp-client.md) - .NET integration
- [Event Streaming](./integration/events.md) - RabbitMQ event integration

### Operations
- [Deployment](./operations/deployment.md) - Docker and production deployment
- [Monitoring](./operations/monitoring.md) - Health checks, metrics, and logging
- [Database](./operations/database.md) - Schema and migrations

## 🚀 Quick Links

- **Local Development**: http://localhost:3004
- **API Documentation**: http://localhost:3004/docs
- **Health Check**: http://localhost:3004/health
- **Metrics**: http://localhost:3004/metrics

## 🎯 Key Features

- ✅ Template CRUD with version control
- ✅ Jinja2 variable substitution
- ✅ Multi-language support (i18n)
- ✅ RabbitMQ event publishing
- ✅ Redis caching
- ✅ Circuit breaker & retry logic
- ✅ Prometheus metrics
- ✅ OpenAPI documentation

## 🔌 Service Endpoints

| Environment | URL |
|------------|-----|
| Local | `http://localhost:3004` |
| Docker | `http://template-service:3004` |
| Production | Configure as needed |

## 📋 Requirements

- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (optional)
- RabbitMQ 3.12+ (optional)

## 🆘 Support

For issues or questions:
1. Check the [API Reference](./api-reference.md)
2. Review [Integration Guides](./integration/overview.md)
3. Contact the Template Service team
