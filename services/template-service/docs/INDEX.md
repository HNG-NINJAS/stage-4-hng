# Documentation Index

> **Complete guide to Template Service documentation**

## 📖 Documentation Map

```
docs/
├── README.md                    # Documentation home
├── INDEX.md                     # This file - complete navigation
├── SUMMARY.md                   # Documentation structure overview
├── ARCHITECTURE.md              # System architecture and design
│
├── Getting Started
│   ├── getting-started.md       # Quick start guide
│   ├── development.md           # Development setup
│   └── api-reference.md         # Complete API reference
│
├── integration/                 # Integration guides
│   ├── README.md               # Integration overview
│   ├── overview.md             # Patterns and best practices
│   ├── python-client.md        # Python/FastAPI integration
│   ├── typescript-client.md    # TypeScript/NestJS integration
│   ├── csharp-client.md        # C#/.NET integration
│   └── events.md               # RabbitMQ event integration
│
├── examples/                    # Code examples
│   ├── README.md               # Examples overview
│   ├── python_client.py        # Python client example
│   ├── nodejs_client.js        # Node.js client example
│   └── csharp_client.cs        # C# client example
│
└── operations/                  # Operations guides
    ├── deployment.md           # Deployment guide
    ├── monitoring.md           # Monitoring and observability
    └── database.md             # Database operations
```

## 🎯 Find What You Need

### I want to...

#### Get Started
- **Run the service locally** → [Getting Started](./getting-started.md)
- **Understand the API** → [API Reference](./api-reference.md)
- **See the architecture** → [Architecture](./ARCHITECTURE.md)
- **Set up development environment** → [Development Guide](./development.md)

#### Integrate with My Service
- **Choose integration method** → [Integration Overview](./integration/overview.md)
- **Use Python/FastAPI** → [Python Client](./integration/python-client.md)
- **Use TypeScript/NestJS** → [TypeScript Client](./integration/typescript-client.md)
- **Use C#/.NET** → [C# Client](./integration/csharp-client.md)
- **Subscribe to events** → [Event Integration](./integration/events.md)
- **See working examples** → [Code Examples](./examples/README.md)

#### Deploy to Production
- **Deploy with Docker** → [Deployment Guide](./operations/deployment.md)
- **Deploy to Kubernetes** → [Deployment Guide](./operations/deployment.md#kubernetes-deployment)
- **Set up monitoring** → [Monitoring Guide](./operations/monitoring.md)
- **Configure alerts** → [Monitoring Guide](./operations/monitoring.md#alerting)
- **Manage database** → [Database Operations](./operations/database.md)

#### Develop & Contribute
- **Set up dev environment** → [Development Guide](./development.md)
- **Understand code structure** → [Development Guide](./development.md#project-structure)
- **Run tests** → [Development Guide](./development.md#testing-guidelines)
- **Create migrations** → [Development Guide](./development.md#database-migrations)
- **Follow coding standards** → [Development Guide](./development.md#coding-standards)

#### Troubleshoot Issues
- **Service not starting** → [Getting Started](./getting-started.md#troubleshooting)
- **Database issues** → [Database Operations](./operations/database.md#troubleshooting)
- **Deployment problems** → [Deployment Guide](./operations/deployment.md#troubleshooting)
- **Performance issues** → [Monitoring Guide](./operations/monitoring.md#troubleshooting)

## 📚 Documentation by Role

### For Developers

**Essential Reading:**
1. [Getting Started](./getting-started.md) - Set up local environment
2. [API Reference](./api-reference.md) - Understand the API
3. [Integration Overview](./integration/overview.md) - Choose integration method
4. [Code Examples](./examples/README.md) - See working implementations

**Language-Specific:**
- Python → [Python Client](./integration/python-client.md)
- TypeScript/Node.js → [TypeScript Client](./integration/typescript-client.md)
- C#/.NET → [C# Client](./integration/csharp-client.md)

**Advanced:**
- [Architecture](./ARCHITECTURE.md) - System design
- [Event Integration](./integration/events.md) - Async communication
- [Development Guide](./development.md) - Contributing

### For DevOps Engineers

**Essential Reading:**
1. [Deployment Guide](./operations/deployment.md) - Deploy to production
2. [Monitoring Guide](./operations/monitoring.md) - Set up observability
3. [Database Operations](./operations/database.md) - Manage database

**Deployment:**
- [Docker Deployment](./operations/deployment.md#docker-deployment)
- [Kubernetes Deployment](./operations/deployment.md#kubernetes-deployment)
- [Environment Variables](./operations/deployment.md#environment-variables)

**Operations:**
- [Health Checks](./operations/monitoring.md#health-checks)
- [Prometheus Metrics](./operations/monitoring.md#prometheus-metrics)
- [Alerting](./operations/monitoring.md#alerting)
- [Database Backup](./operations/database.md#backup--restore)

### For Architects

**Essential Reading:**
1. [Architecture](./ARCHITECTURE.md) - System design and patterns
2. [Integration Overview](./integration/overview.md) - Integration patterns
3. [API Reference](./api-reference.md) - API capabilities

**Design Decisions:**
- [System Overview](./ARCHITECTURE.md#system-overview)
- [Data Flow](./ARCHITECTURE.md#data-flow)
- [Event Architecture](./ARCHITECTURE.md#event-architecture)
- [Scalability](./ARCHITECTURE.md#scalability)

### For Product Managers

**Essential Reading:**
1. [README](../README.md) - Feature overview
2. [API Reference](./api-reference.md) - Capabilities
3. [Integration Overview](./integration/overview.md) - Use cases

## 🔍 Quick Reference

### Common Tasks

| Task | Documentation |
|------|---------------|
| Create a template | [API Reference - Create Template](./api-reference.md#create-template) |
| Render a template | [API Reference - Render Template](./api-reference.md#render-template) |
| Add translation | [API Reference - Add Translation](./api-reference.md#add-translation) |
| List templates | [API Reference - List Templates](./api-reference.md#list-templates) |
| Check health | [API Reference - Health Check](./api-reference.md#health-check) |
| View metrics | [API Reference - Prometheus Metrics](./api-reference.md#prometheus-metrics) |

### Integration Patterns

| Pattern | Documentation |
|---------|---------------|
| REST API (sync) | [Integration Overview](./integration/overview.md#1-rest-api-synchronous) |
| RabbitMQ Events (async) | [Event Integration](./integration/events.md) |
| Caching | [Integration Overview](./integration/overview.md#caching-strategy) |
| Circuit Breaker | [Integration Overview](./integration/overview.md#4-implement-circuit-breaker) |
| Fallback Strategy | [Integration Overview](./integration/overview.md#2-implement-fallback-strategy) |

### Operations

| Operation | Documentation |
|-----------|---------------|
| Deploy with Docker | [Deployment - Docker](./operations/deployment.md#docker-deployment) |
| Deploy to Kubernetes | [Deployment - Kubernetes](./operations/deployment.md#kubernetes-deployment) |
| Run migrations | [Database - Migrations](./operations/database.md#migrations) |
| Backup database | [Database - Backup](./operations/database.md#backup--restore) |
| Set up monitoring | [Monitoring Guide](./operations/monitoring.md) |
| Configure alerts | [Monitoring - Alerting](./operations/monitoring.md#alerting) |

## 📝 Documentation Standards

### File Organization
- **Root docs/** - Main documentation files
- **integration/** - Integration guides by language/framework
- **examples/** - Working code examples
- **operations/** - Deployment and operations guides

### Naming Conventions
- Use lowercase with hyphens: `getting-started.md`
- Be descriptive: `python-client.md` not `client1.md`
- Group related docs in subdirectories

### Content Structure
1. Brief description at the top
2. Clear headings (##, ###)
3. Working code examples
4. Links to related documentation
5. Next steps at the end

## 🔗 External Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [Redis Documentation](https://redis.io/documentation)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

## 🆘 Getting Help

1. **Check the docs** - Use this index to find relevant documentation
2. **Search the repo** - Look for similar issues or examples
3. **Review examples** - Check [Code Examples](./examples/README.md)
4. **Ask the team** - Reach out in your team chat

## 📅 Documentation Maintenance

### Last Updated
- Documentation structure: 2025-11-12
- API Reference: Current with v1.0.0
- Integration guides: Current with v1.0.0

### Contributing
When updating documentation:
1. Follow existing structure and style
2. Test all code examples
3. Update this index if adding new docs
4. Keep cross-references up to date
5. Update the "Last Updated" section

---

**Need something not listed here?** Check [SUMMARY.md](./SUMMARY.md) for the complete documentation structure.
