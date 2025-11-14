# Deployment Guide

## Local Deployment

### Quick Start
```bash
./start.sh
```

### Manual Start
```bash
docker-compose -f docker-compose.minimal.yml up -d
sleep 30
docker-compose -f docker-compose.minimal.yml exec template-service python scripts/seed_templates.py
```

## Server Deployment

### 1. Prepare Server

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again
exit
```

### 2. Upload Project

```bash
# From local machine
rsync -avz --exclude 'node_modules' --exclude '.git' \
  ./ user@your-server.com:~/notification-system/
```

### 3. Configure Firewall

```bash
# On server
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 3000/tcp  # API Gateway
sudo ufw allow 15672/tcp # RabbitMQ UI (optional)
sudo ufw enable
```

### 4. Deploy

```bash
# On server
cd notification-system

# Build
docker-compose -f docker-compose.minimal.yml build

# Start
docker-compose -f docker-compose.minimal.yml up -d

# Wait
sleep 30

# Seed templates
docker-compose -f docker-compose.minimal.yml exec template-service python scripts/seed_templates.py
```

### 5. Test

```bash
# Replace YOUR_SERVER_IP
curl http://YOUR_SERVER_IP:3000/health
curl http://YOUR_SERVER_IP:3004/health
curl http://YOUR_SERVER_IP:3003/health
curl http://YOUR_SERVER_IP:3005/health
```

## Service URLs

**Local:**
- API Gateway: http://localhost:3000
- Template Service: http://localhost:3004/docs
- Push Service: http://localhost:3003/docs
- Email Service: http://localhost:3005/docs
- RabbitMQ UI: http://localhost:15672

**Server:**
- API Gateway: http://YOUR_SERVER_IP:3000
- Template Service: http://YOUR_SERVER_IP:3004/docs
- Push Service: http://YOUR_SERVER_IP:3003/docs
- Email Service: http://YOUR_SERVER_IP:3005/docs
- RabbitMQ UI: http://YOUR_SERVER_IP:15672

## Ports Used

| Service | Port | Description |
|---------|------|-------------|
| API Gateway | 3000 | Main entry point |
| Push Service | 3003 | Push notifications |
| Template Service | 3004 | Template management |
| Email Service | 3005 | Email notifications |
| PostgreSQL | 5433 | Database (not 5432!) |
| RabbitMQ | 5672 | Message queue |
| RabbitMQ UI | 15672 | Management interface |
| Redis | 6379 | Cache |

**Note:** Port 5433 is used to avoid conflicts with local PostgreSQL on port 5432.

## Production Configuration

For production, update passwords in docker-compose.prod.yml:

```yaml
environment:
  RABBITMQ_USER: ${RABBITMQ_USER}
  RABBITMQ_PASS: ${RABBITMQ_PASS}
  REDIS_PASSWORD: ${REDIS_PASSWORD}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

## Monitoring

```bash
# Check status
docker-compose -f docker-compose.minimal.yml ps

# View logs
docker-compose -f docker-compose.minimal.yml logs -f

# Check resources
docker stats
```

## Maintenance

### Restart Services
```bash
docker-compose -f docker-compose.minimal.yml restart
```

### Update Services
```bash
git pull
docker-compose -f docker-compose.minimal.yml build
docker-compose -f docker-compose.minimal.yml up -d
```

### Backup Database
```bash
docker-compose -f docker-compose.minimal.yml exec postgres_template \
  pg_dump -U admin template_service > backup_$(date +%Y%m%d).sql
```

## Troubleshooting

### Services won't start
```bash
docker-compose -f docker-compose.minimal.yml logs [service-name]
```

### Port conflicts
The system uses port 5433 (not 5432) to avoid conflicts.

### Database issues
```bash
docker-compose -f docker-compose.minimal.yml exec postgres_template \
  psql -U admin -d template_service
```

### Fresh start
```bash
docker-compose -f docker-compose.minimal.yml down -v
docker-compose -f docker-compose.minimal.yml up -d
```
