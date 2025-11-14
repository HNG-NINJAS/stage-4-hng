# AWS EC2 Deployment - Quick Start Guide

## 🚀 5-Minute Setup

### 1. Launch EC2 Instance (AWS Console)
- **AMI**: Ubuntu Server 22.04 LTS
- **Type**: t3.medium or t3.large
- **Storage**: 20 GB
- **Security Group**: Open ports 22, 3000, 3003, 3004, 3005, 15672
- Download your `.pem` key file

### 2. Setup EC2 (SSH to instance)
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Run setup script
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/notification-system/main/scripts/setup-ec2.sh -o setup-ec2.sh
chmod +x setup-ec2.sh
./setup-ec2.sh

# Logout and login again
exit
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

### 3. Clone & Configure
```bash
cd ~/notification-system
git clone https://github.com/YOUR_USERNAME/notification-system.git .

# Setup environment
cp .env.production .env
nano .env  # Update these:
# - POSTGRES_PASSWORD
# - REDIS_PASSWORD
# - RABBITMQ_PASS
# - JWT_SECRET
```

### 4. Deploy
```bash
./start.sh
```

### 5. Test
```bash
curl http://localhost:3000/health
curl http://localhost:3004/health
curl http://localhost:3003/health
curl http://localhost:3005/health
```

## 🤖 GitHub Actions Auto-Deploy

### Configure GitHub Secrets
Go to: GitHub → Your Repo → Settings → Secrets and variables → Actions

Add these 3 secrets:

| Secret Name | Value |
|-------------|-------|
| `EC2_HOST` | Your EC2 public IP (e.g., 54.123.45.67) |
| `EC2_USER` | `ubuntu` |
| `EC2_SSH_KEY` | Content of your `.pem` file |

### Deploy
```bash
# Just push to main branch
git push origin main

# GitHub Actions will automatically:
# 1. SSH to your EC2
# 2. Pull latest code
# 3. Build & deploy
# 4. Run health checks
```

## 🌐 Access Your Services

Replace `YOUR_EC2_IP` with your actual EC2 public IP:

- **API Gateway**: http://YOUR_EC2_IP:3000
- **Template Service**: http://YOUR_EC2_IP:3004/docs
- **Push Service**: http://YOUR_EC2_IP:3003/docs
- **Email Service**: http://YOUR_EC2_IP:3005/docs
- **RabbitMQ UI**: http://YOUR_EC2_IP:15672 (admin/your-password)

## 🔒 Optional: Setup SSL

```bash
# Point your domain to EC2 IP first
# Then run:
./scripts/setup-ssl.sh your-domain.com

# Access via HTTPS:
# https://your-domain.com
```

## 📊 Monitor

```bash
# Check services
docker-compose -f docker-compose.minimal.yml ps

# View logs
docker-compose -f docker-compose.minimal.yml logs -f

# Restart if needed
docker-compose -f docker-compose.minimal.yml restart
```

## 💰 Cost
- **t3.medium**: ~$30/month
- **t3.large**: ~$60/month

## 📚 Full Documentation
- **Complete Guide**: [docs/AWS_DEPLOYMENT.md](./docs/AWS_DEPLOYMENT.md)
- **Deployment Summary**: [docs/DEPLOYMENT_SUMMARY.md](./docs/DEPLOYMENT_SUMMARY.md)

---

**That's it!** Your notification system is now running on AWS EC2 with automated deployments. 🎉
