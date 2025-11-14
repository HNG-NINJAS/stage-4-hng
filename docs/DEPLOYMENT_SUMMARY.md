# AWS EC2 Deployment - Complete Setup

## ✅ What's Been Created

### 1. GitHub Actions CI/CD Pipeline
- `.github/workflows/deploy.yml` - Automated deployment workflow
- Triggers on push to main/master branch
- SSH deployment to EC2
- Health checks after deployment

### 2. EC2 Setup Scripts
- `scripts/setup-ec2.sh` - EC2 instance preparation script
  - Installs Docker & Docker Compose
  - Configures firewall (UFW)
  - Sets up project directory
  
- `scripts/setup-ssl.sh` - SSL certificate setup with Let's Encrypt
  - Installs nginx & certbot
  - Configures SSL certificates
  - Sets up auto-renewal

### 3. Production Configuration
- `.env.production` - Production environment template
  - Database credentials
  - Redis & RabbitMQ passwords
  - Service URLs
  - Security settings

### 4. Nginx Configuration
- `nginx/nginx.conf` - Reverse proxy configuration
  - HTTPS redirect
  - SSL/TLS security
  - Security headers
  - Service routing
  - Restricted RabbitMQ access

### 5. Documentation
- `docs/AWS_DEPLOYMENT.md` - Complete deployment guide
  - EC2 instance setup
  - GitHub secrets configuration
  - Deployment steps
  - Troubleshooting
  - Security best practices

## 🚀 Quick Start

### Step 1: Launch EC2 Instance
```bash
# Instance: Ubuntu 22.04 LTS
# Type: t3.medium or t3.large
# Storage: 20 GB minimum
# Security Group: Ports 22, 3000, 3003, 3004, 3005, 15672
```

### Step 2: Setup EC2
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/notification-system/main/scripts/setup-ec2.sh -o setup-ec2.sh
chmod +x setup-ec2.sh
./setup-ec2.sh
```

### Step 3: Configure GitHub Secrets
Go to GitHub → Settings → Secrets and variables → Actions

Add:
- `EC2_HOST` - Your EC2 public IP
- `EC2_USER` - ubuntu
- `EC2_SSH_KEY` - Your private key content

### Step 4: Clone & Configure
```bash
cd ~/notification-system
git clone https://github.com/YOUR_USERNAME/notification-system.git .
cp .env.production .env
nano .env  # Update passwords
```

### Step 5: Deploy
```bash
# Manual first deployment
./start.sh

# Or push to GitHub main branch for automatic deployment
git push origin main
```

## 📊 Service URLs

### Without SSL (HTTP)
- API Gateway: http://YOUR_EC2_IP:3000
- Template Service: http://YOUR_EC2_IP:3004/docs
- Push Service: http://YOUR_EC2_IP:3003/docs
- Email Service: http://YOUR_EC2_IP:3005/docs
- RabbitMQ UI: http://YOUR_EC2_IP:15672

### With SSL (HTTPS) - Optional
```bash
# Setup SSL with your domain
./scripts/setup-ssl.sh your-domain.com
```

- API Gateway: https://your-domain.com
- Template Service: https://your-domain.com/docs/templates
- Push Service: https://your-domain.com/docs/push
- Email Service: https://your-domain.com/docs/email
- RabbitMQ UI: https://your-domain.com/rabbitmq

## 🔒 Security Checklist

- [ ] Update all passwords in `.env`
- [ ] Restrict RabbitMQ UI to your IP only
- [ ] Enable SSL/TLS for production
- [ ] Configure firewall rules
- [ ] Set up regular backups
- [ ] Enable CloudWatch monitoring
- [ ] Review security group settings

## 💰 Cost Estimate

- **t3.medium**: ~$30/month
- **t3.large**: ~$60/month
- **Data transfer**: ~$5-10/month
- **Total**: ~$35-70/month

## 📝 Required GitHub Secrets

| Secret | Description | Example |
|--------|-------------|---------|
| `EC2_HOST` | EC2 public IP | 54.123.45.67 |
| `EC2_USER` | EC2 username | ubuntu |
| `EC2_SSH_KEY` | SSH private key | -----BEGIN RSA PRIVATE KEY----- ... |

## 🔄 Deployment Flow

```
Developer pushes code
       ↓
GitHub Actions triggers
       ↓
SSH to EC2 instance
       ↓
Pull latest code
       ↓
Build Docker images
       ↓
Deploy with docker-compose
       ↓
Run health checks
       ↓
Notify success/failure
```

## 🛠️ Monitoring & Maintenance

### Check Service Status
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
cd ~/notification-system
docker-compose -f docker-compose.minimal.yml ps
```

### View Logs
```bash
docker-compose -f docker-compose.minimal.yml logs -f
```

### Health Check
```bash
curl http://localhost:3000/health
curl http://localhost:3004/health
curl http://localhost:3003/health
curl http://localhost:3005/health
```

### Backup Database
```bash
docker-compose -f docker-compose.minimal.yml exec postgres_template \
  pg_dump -U admin template_service > backup_$(date +%Y%m%d).sql
```

## 🐛 Troubleshooting

### Deployment Fails
1. Check GitHub Actions logs
2. SSH to EC2 and check Docker logs
3. Verify environment variables
4. Check firewall rules

### Services Won't Start
```bash
docker-compose -f docker-compose.minimal.yml logs [service-name]
docker-compose -f docker-compose.minimal.yml restart
```

### Port Conflicts
```bash
sudo lsof -i :3000
sudo ufw status
```

## 📚 Documentation Links

- **Complete Guide**: [docs/AWS_DEPLOYMENT.md](./AWS_DEPLOYMENT.md)
- **Demo Guide**: [../DEMO_GUIDE.md](../DEMO_GUIDE.md)
- **API Examples**: [../EXAMPLE_REQUESTS.md](../EXAMPLE_REQUESTS.md)
- **Architecture**: [../README.md](../README.md)

## ✨ Features

✅ Automated CI/CD with GitHub Actions
✅ One-command EC2 setup
✅ SSL/HTTPS support
✅ Security hardened
✅ Health monitoring
✅ Auto-renewal certificates
✅ Firewall configured
✅ Production ready

## 🎯 Next Steps

1. Follow [docs/AWS_DEPLOYMENT.md](./AWS_DEPLOYMENT.md) for detailed setup
2. Configure GitHub secrets
3. Deploy to EC2
4. Set up SSL (optional)
5. Configure monitoring
6. Set up automated backups

---

**Ready to deploy!** 🚀
