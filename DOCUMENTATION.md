# Documentation Index

## Quick Links

| Document | Purpose | Audience |
|----------|---------|----------|
| [README.md](./README.md) | Project overview | Everyone |
| [GETTING_STARTED.md](./GETTING_STARTED.md) | Quick start (5 min) | Developers |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | Deployment guide | DevOps |
| [EXAMPLE_REQUESTS.md](./EXAMPLE_REQUESTS.md) | API examples | Developers |
| [DEMO_GUIDE.md](./DEMO_GUIDE.md) | Demo script | Presenters |

## Documentation Structure

```
notification-system/
├── README.md                    # Main documentation
├── GETTING_STARTED.md           # Quick start guide
├── DEPLOYMENT.md                # Deployment instructions
├── EXAMPLE_REQUESTS.md          # API examples
├── DEMO_GUIDE.md                # Presentation guide
├── SYSTEM_SUMMARY.md            # Architecture overview
├── PROJECT_STRUCTURE.md         # File structure
├── DOCUMENTATION.md             # This file
│
├── docs/                        # Additional documentation
│   ├── DOCKER_COMPOSE_EXPLAINED.md
│   └── internal/                # Internal notes (not in git)
│
├── services/                    # Service-specific docs
│   ├── api-gateway/README.md
│   ├── template-service/README.md
│   ├── push-service/README.md
│   ├── email-service/README.md
│   └── user-service/packages/README.md
│
└── scripts/                     # Utility scripts
    ├── test_complete_system.sh
    ├── recording_script.sh
    └── start_minimal.sh
```

## Getting Started Path

1. **First Time Setup**
   - Read [README.md](./README.md) for overview
   - Follow [GETTING_STARTED.md](./GETTING_STARTED.md)
   - Run `./start.sh`

2. **Testing**
   - Run `bash scripts/test_complete_system.sh`
   - Try examples from [EXAMPLE_REQUESTS.md](./EXAMPLE_REQUESTS.md)

3. **Deployment**
   - Follow [DEPLOYMENT.md](./DEPLOYMENT.md)
   - Deploy to server

4. **Presentation**
   - Review [DEMO_GUIDE.md](./DEMO_GUIDE.md)

## Key Commands

```bash
# Start system
./start.sh

# Test system
bash scripts/test_complete_system.sh

# View logs
docker-compose -f docker-compose.minimal.yml logs -f

# Stop system
docker-compose -f docker-compose.minimal.yml down
```

## Service URLs

- API Gateway: http://localhost:3000
- Template Service: http://localhost:3004/docs
- Push Service: http://localhost:3003/docs
- Email Service: http://localhost:3005/docs
- RabbitMQ UI: http://localhost:15672 (admin/admin123)

## Support

For issues:
1. Check service logs: `docker-compose -f docker-compose.minimal.yml logs [service]`
2. Review [GETTING_STARTED.md](./GETTING_STARTED.md) troubleshooting section
3. Check service-specific READMEs in `services/` directories

## Contributing

When adding documentation:
- Keep it concise and actionable
- Use clear examples
- Update this index
- Follow existing formatting
