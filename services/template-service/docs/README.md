# Template Service Documentation

Welcome to the Template Service documentation. This service manages notification templates with multi-language support, version control, and event-driven architecture.

## 🚀 Quick Links

- **[Quick Reference](./QUICK_REFERENCE.md)** - Fast lookup for common operations
- **[FAQ](./FAQ.md)** - Frequently asked questions
- **[Complete Index](./INDEX.md)** - Navigate all documentation by role and task
- **[Getting Started](./getting-started.md)** - Set up and run the service
- **[API Reference](./api-reference.md)** - Complete API documentation

## 📚 Documentation Index

### Getting Started
- [Quick Start Guide](./getting-started.md) - Setup and run the service
- [Development Guide](./development.md) - Development setup and workflow
- [API Reference](./api-reference.md) - Complete API documentation
- [Architecture](./ARCHITECTURE.md) - System design and architecture

### Integration Guides
- [Integration Overview](./integration/overview.md) - Integration patterns and best practices
- [Python Client](./integration/python-client.md) - Python/FastAPI integration
- [TypeScript/NestJS Client](./integration/typescript-client.md) - Node.js/NestJS integration
- [C# Client](./integration/csharp-client.md) - .NET integration
- [Event Streaming](./integration/events.md) - RabbitMQ event integration
- [Code Examples](./examples/README.md) - Ready-to-use client implementations

### Operations
- [Deployment](./operations/deployment.md) - Docker and Kubernetes deployment
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

## 🆘 Getting Help

1. **Common questions** → [FAQ](./FAQ.md)
2. **Quick answers** → [Quick Reference](./QUICK_REFERENCE.md)
3. **Find documentation** → [Complete Index](./INDEX.md)
4. **API questions** → [API Reference](./api-reference.md)
5. **Integration help** → [Integration Guides](./integration/overview.md)
6. **Contact team** → Reach out in your team chat

## 📖 Documentation Resources

- **[FAQ.md](./FAQ.md)** - Frequently asked questions and troubleshooting
- **[INDEX.md](./INDEX.md)** - Complete navigation guide organized by role and task
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Common commands and code snippets
- **[SUMMARY.md](./SUMMARY.md)** - Documentation structure overview
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System design and architecture
- **[DOCUMENTATION_REVIEW.md](./DOCUMENTATION_REVIEW.md)** - Documentation quality assessment
