# Monitoring & Troubleshooting Guide

## 🔍 How to Monitor Your Notification System

### 1. Health Check Endpoints

Each service exposes a `/health` endpoint:

```bash
# Check all services
curl http://YOUR_EC2_IP:3000/health  # API Gateway
curl http://YOUR_EC2_IP:3004/health  # Template Service
curl http://YOUR_EC2_IP:3003/health  # Push Service
curl http://YOUR_EC2_IP:3005/health  # Email Service
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "api-gateway",
  "timestamp": "2025-11-14T12:00:00.000Z"
}
```

### 2. Docker Container Status

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Check running containers
docker ps

# Expected output: All containers should be "Up"
# CONTAINER ID   IMAGE                    STATUS
# abc123         api-gateway              Up 2 hours
# def456         template-service         Up 2 hours
# ghi789         push-service             Up 2 hours
# jkl012         email-service            Up 2 hours
# mno345         rabbitmq                 Up 2 hours
# pqr678         redis                    Up 2 hours
# stu901         postgres                 Up 2 hours
```

### 3. Service Logs

```bash
# View all logs
docker-compose -f docker-compose.minimal.yml logs

# Follow logs in real-time
docker-compose -f docker-compose.minimal.yml logs -f

# View specific service logs
docker-compose -f docker-compose.minimal.yml logs api-gateway
docker-compose -f docker-compose.minimal.yml logs template-service
docker-compose -f docker-compose.minimal.yml logs push-service
docker-compose -f docker-compose.minimal.yml logs email-service

# View last 100 lines
docker-compose -f docker-compose.minimal.yml logs --tail=100

# View logs with timestamps
docker-compose -f docker-compose.minimal.yml logs -t
```

### 4. RabbitMQ Management UI

Access the RabbitMQ dashboard:

```
URL: http://YOUR_EC2_IP:15672
Username: admin
Password: admin123 (or your configured password)
```

**What to Monitor:**
- ✅ Queues: Should show message counts
- ✅ Connections: Services should be connected
- ✅ Channels: Active channels for each service
- ✅ Message rates: Messages being processed

### 5. Resource Usage

```bash
# Check Docker container resource usage
docker stats

# Shows:
# - CPU usage
# - Memory usage
# - Network I/O
# - Block I/O

# Check system resources
htop  # or top

# Check disk space
df -h

# Check memory
free -h
```

## 🚨 Detecting Failures

### Method 1: Automated Health Checks (Recommended)

Create a monitoring script:

```bash
# Create health check script
cat > ~/health-monitor.sh << 'EOF'
#!/bin/bash

SERVICES=(
  "http://localhost:3000/health:API Gateway"
  "http://localhost:3004/health:Template Service"
  "http://localhost:3003/health:Push Service"
  "http://localhost:3005/health:Email Service"
)

echo "=== Health Check $(date) ==="

for service in "${SERVICES[@]}"; do
  IFS=':' read -r url name <<< "$service"
  
  if curl -f -s "$url" > /dev/null 2>&1; then
    echo "✅ $name - Healthy"
  else
    echo "❌ $name - FAILED"
    # Send alert (email, Slack, etc.)
    # curl -X POST https://hooks.slack.com/... -d "Service $name is down"
  fi
done

echo ""
EOF

chmod +x ~/health-monitor.sh

# Run it
./health-monitor.sh

# Schedule it with cron (every 5 minutes)
crontab -e
# Add: */5 * * * * /home/ubuntu/health-monitor.sh >> /home/ubuntu/health-monitor.log 2>&1
```

### Method 2: GitHub Actions Monitoring

The deployment workflow already includes health checks:

```yaml
# In .github/workflows/deploy.yml
- name: Health Check via SSH
  run: |
    curl -f http://localhost:3000/health || exit 1
    curl -f http://localhost:3004/health || exit 1
    curl -f http://localhost:3003/health || exit 1
    curl -f http://localhost:3005/health || exit 1
```

If deployment fails, you'll get a notification in GitHub Actions.

### Method 3: Docker Health Checks

Services have built-in Docker health checks:

```bash
# Check health status
docker ps --format "table {{.Names}}\t{{.Status}}"

# Healthy output:
# NAMES                    STATUS
# api-gateway              Up 2 hours (healthy)
# template-service         Up 2 hours (healthy)
# push-service             Up 2 hours (healthy)

# Unhealthy output:
# NAMES                    STATUS
# api-gateway              Up 2 hours (unhealthy)  ⚠️
```

### Method 4: Log Monitoring

Watch for errors in logs:

```bash
# Monitor for errors
docker-compose -f docker-compose.minimal.yml logs -f | grep -i error

# Monitor for specific service errors
docker-compose -f docker-compose.minimal.yml logs -f api-gateway | grep -i error

# Count errors in last hour
docker-compose -f docker-compose.minimal.yml logs --since 1h | grep -i error | wc -l
```

## 📊 What to Monitor

### Critical Metrics

1. **Service Availability**
   - All health endpoints return 200 OK
   - All Docker containers are "Up"

2. **Message Queue**
   - RabbitMQ is running
   - Messages are being processed (not stuck)
   - No excessive queue buildup

3. **Database**
   - PostgreSQL is running
   - Connection pool not exhausted

4. **Cache**
   - Redis is running
   - Memory usage under control

5. **Resource Usage**
   - CPU < 80%
   - Memory < 80%
   - Disk space > 20% free

### Warning Signs

🚨 **Service is Down:**
```bash
# Health check fails
curl http://localhost:3000/health
# Returns: Connection refused or 500 error
```

🚨 **Container Restarting:**
```bash
docker ps
# Shows: Restarting (1) 10 seconds ago
```

🚨 **High Error Rate:**
```bash
docker-compose logs --tail=100 | grep -i error
# Shows many error messages
```

🚨 **Queue Buildup:**
- RabbitMQ UI shows thousands of unprocessed messages
- Messages not being consumed

🚨 **High Resource Usage:**
```bash
docker stats
# Shows: CPU > 90% or Memory > 90%
```

## 🔧 Troubleshooting Common Issues

### Issue 1: Service Won't Start

**Check:**
```bash
# View logs
docker-compose -f docker-compose.minimal.yml logs service-name

# Common causes:
# - Port already in use
# - Database connection failed
# - Missing environment variables
```

**Fix:**
```bash
# Restart service
docker-compose -f docker-compose.minimal.yml restart service-name

# Or rebuild
docker-compose -f docker-compose.minimal.yml up -d --build service-name
```

### Issue 2: Service is Unhealthy

**Check:**
```bash
# Check health endpoint
curl -v http://localhost:3000/health

# Check dependencies
docker-compose -f docker-compose.minimal.yml ps
# Ensure RabbitMQ, Redis, PostgreSQL are healthy
```

**Fix:**
```bash
# Restart unhealthy service
docker-compose -f docker-compose.minimal.yml restart service-name

# Check logs for root cause
docker-compose -f docker-compose.minimal.yml logs service-name
```

### Issue 3: Messages Not Being Processed

**Check:**
```bash
# Check RabbitMQ
# Go to: http://YOUR_EC2_IP:15672
# Look at queue depths

# Check worker logs
docker-compose -f docker-compose.minimal.yml logs push-service | grep -i worker
docker-compose -f docker-compose.minimal.yml logs email-service | grep -i worker
```

**Fix:**
```bash
# Restart workers
docker-compose -f docker-compose.minimal.yml restart push-service
docker-compose -f docker-compose.minimal.yml restart email-service
```

### Issue 4: High Memory Usage

**Check:**
```bash
docker stats --no-stream

# Identify which container is using too much memory
```

**Fix:**
```bash
# Restart the problematic service
docker-compose -f docker-compose.minimal.yml restart service-name

# Or restart all services
docker-compose -f docker-compose.minimal.yml restart
```

### Issue 5: Database Connection Errors

**Check:**
```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.minimal.yml ps postgres_template

# Check logs
docker-compose -f docker-compose.minimal.yml logs postgres_template
```

**Fix:**
```bash
# Restart PostgreSQL
docker-compose -f docker-compose.minimal.yml restart postgres_template

# Wait for it to be healthy
sleep 10

# Restart dependent services
docker-compose -f docker-compose.minimal.yml restart template-service
```

## 📈 Advanced Monitoring (Optional)

### Option 1: Prometheus + Grafana

Add monitoring stack to docker-compose:

```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      
  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### Option 2: ELK Stack (Elasticsearch, Logstash, Kibana)

For centralized logging:

```yaml
services:
  elasticsearch:
    image: elasticsearch:8.11.0
    
  logstash:
    image: logstash:8.11.0
    
  kibana:
    image: kibana:8.11.0
    ports:
      - "5601:5601"
```

### Option 3: Uptime Monitoring Services

Use external services:
- **UptimeRobot** (free): https://uptimerobot.com
- **Pingdom**: https://pingdom.com
- **StatusCake**: https://statuscake.com

Configure them to check:
- http://YOUR_EC2_IP:3000/health
- http://YOUR_EC2_IP:3004/health
- http://YOUR_EC2_IP:3003/health
- http://YOUR_EC2_IP:3005/health

### Option 4: AWS CloudWatch

Enable CloudWatch monitoring:

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure metrics
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json
```

## 🔔 Setting Up Alerts

### Email Alerts

```bash
# Install mailutils
sudo apt-get install -y mailutils

# Create alert script
cat > ~/alert.sh << 'EOF'
#!/bin/bash
SERVICE=$1
STATUS=$2

echo "Service $SERVICE is $STATUS" | mail -s "Alert: $SERVICE $STATUS" your-email@example.com
EOF

chmod +x ~/alert.sh

# Use in health check script
if ! curl -f http://localhost:3000/health; then
  ./alert.sh "API Gateway" "DOWN"
fi
```

### Slack Alerts

```bash
# Create Slack webhook
# Go to: https://api.slack.com/messaging/webhooks

# Send alert
curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
  -H 'Content-Type: application/json' \
  -d '{"text":"🚨 API Gateway is down!"}'
```

## 📝 Monitoring Checklist

Daily:
- [ ] Check all health endpoints
- [ ] Review error logs
- [ ] Check RabbitMQ queue depths
- [ ] Verify all containers are running

Weekly:
- [ ] Review resource usage trends
- [ ] Check disk space
- [ ] Review application logs for patterns
- [ ] Test backup/restore procedures

Monthly:
- [ ] Review and update monitoring scripts
- [ ] Test disaster recovery
- [ ] Update dependencies
- [ ] Review security patches

## 🎯 Quick Commands Reference

```bash
# Health checks
curl http://localhost:3000/health
curl http://localhost:3004/health
curl http://localhost:3003/health
curl http://localhost:3005/health

# Container status
docker ps
docker-compose -f docker-compose.minimal.yml ps

# Logs
docker-compose -f docker-compose.minimal.yml logs -f
docker-compose -f docker-compose.minimal.yml logs --tail=100

# Resource usage
docker stats
htop
df -h
free -h

# Restart services
docker-compose -f docker-compose.minimal.yml restart
docker-compose -f docker-compose.minimal.yml restart service-name

# Full restart
docker-compose -f docker-compose.minimal.yml down
docker-compose -f docker-compose.minimal.yml up -d
```

## 🆘 Emergency Procedures

### Complete System Failure

```bash
# 1. SSH to EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# 2. Stop everything
docker-compose -f docker-compose.minimal.yml down

# 3. Check system resources
df -h
free -h
docker system df

# 4. Clean up if needed
docker system prune -a --volumes

# 5. Restart
docker-compose -f docker-compose.minimal.yml up -d

# 6. Wait for services
sleep 30

# 7. Verify
docker-compose -f docker-compose.minimal.yml ps
curl http://localhost:3000/health
```

### Data Corruption

```bash
# Restore from backup
docker-compose -f docker-compose.minimal.yml exec postgres_template \
  psql -U admin -d template_service < backup.sql
```

## 📞 Support

If issues persist:
1. Check GitHub Actions logs
2. Review service logs
3. Check RabbitMQ UI
4. Verify EC2 security groups
5. Check system resources

Your notification system is now monitored! 🎉
