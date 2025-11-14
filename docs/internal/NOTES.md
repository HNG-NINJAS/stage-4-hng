# Internal Notes (Local Only - Not in Git)

## System Status

✅ All services working
✅ All tests passing (13/13)
✅ Documentation cleaned up
✅ Ready for deployment

## Important Notes

### Port Configuration
- System uses port **5433** (not 5432) to avoid conflicts with local PostgreSQL
- Always use `docker-compose -f docker-compose.minimal.yml`

### User Service
- Not included in minimal setup due to port conflicts
- Fully implemented but optional
- Can be deployed separately if needed

### What Works
- Push notifications (mock mode)
- Email notifications (mock mode)
- Template management
- Multi-language support
- Message queuing
- Health monitoring

### Quick Commands
```bash
# Start
./start.sh

# Test
bash scripts/test_complete_system.sh

# Stop
docker-compose -f docker-compose.minimal.yml down

# Logs
docker-compose -f docker-compose.minimal.yml logs -f
```

### For Demo
- Show push and email notifications
- Show template management
- Show RabbitMQ UI
- Explain User Service is separate microservice
- Show code and documentation

### Deployment
- Use docker-compose.minimal.yml
- Port 5433 for PostgreSQL
- All services on notification_network
- Mock mode by default (no external dependencies)

## Troubleshooting

### Port Conflicts
Use minimal setup - it uses port 5433

### Services Won't Start
```bash
docker-compose -f docker-compose.minimal.yml logs [service-name]
```

### Fresh Start
```bash
docker-compose -f docker-compose.minimal.yml down -v
./start.sh
```

## Files Not in Git

This directory (docs/internal/) is excluded from git.
Use it for personal notes, credentials, etc.
