# Environment Setup Explained

## You're Right! 

The `.env.production` file doesn't need credentials if using `docker-compose.minimal.yml` because that file has **hardcoded credentials**.

## Two Scenarios

### Scenario 1: Using docker-compose.minimal.yml (Current)
**Credentials**: Hardcoded in docker-compose file
- PostgreSQL: `admin/admin123`
- Redis: `redis123`
- RabbitMQ: `admin/admin123`

**`.env` file**: Not needed for infrastructure credentials

### Scenario 2: Using docker-compose.prod.yml (Secure)
**Credentials**: From `.env` file
- PostgreSQL: `${POSTGRES_PASSWORD}`
- Redis: `${REDIS_PASSWORD}`
- RabbitMQ: `${RABBITMQ_PASS}`

**`.env` file**: Required with strong passwords

## Current Setup

✅ Workflow uses `docker-compose.minimal.yml`
✅ `.env.production` updated to clarify this
✅ Both options documented

## Files Updated

1. **`.env.production`** - Now explains it's for docker-compose.prod.yml
2. **`docs/DOCKER_COMPOSE_CHOICE.md`** - Explains both options

## Quick Answer

**Q**: Do I need to set passwords in .env?
**A**: Not if using docker-compose.minimal.yml (current setup)

**Q**: Are hardcoded passwords secure?
**A**: No, but OK for demo. Use docker-compose.prod.yml for production.

**Q**: How to switch to secure mode?
**A**: See `docs/DOCKER_COMPOSE_CHOICE.md`
