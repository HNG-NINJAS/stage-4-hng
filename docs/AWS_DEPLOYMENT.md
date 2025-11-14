# AWS EC2 Deployment with GitHub Actions

## Overview

This guide sets up automated deployment to AWS EC2 using GitHub Actions CI/CD pipeline.

## Architecture

```
GitHub Repository
       ↓ (push to main)
GitHub Actions
       ↓ (SSH deploy)
AWS EC2 Instance
       ↓ (docker-compose)
Notification System
```

## Prerequisites

1. AWS Account
2. GitHub Repository
3. Basic knowledge of AWS EC2

## Step 1: Create EC2 Instance

### 1.1 Launch EC2 Instance

1. Go to AWS Console → EC2
2. Click "Launch Instance"
3. Choose **Ubuntu Server 22.04 LTS**
4. Instance type: **t3.medium** (minimum) or **t3.large** (recommended)
5. Create or select key pair
6. Security Group settings:

| Type | Protocol | Port Range | Source | Description |
|------|----------|------------|--------|-------------|
| SSH | TCP | 22 | Your IP | SSH access |
| HTTP | TCP | 3000 | 0.0.0.0/0 | API Gateway |
| Custom TCP | TCP | 3003 | 0.0.0.0/0 | Push Service |
| Custom TCP | TCP | 3004 | 0.0.0.0/0 | Template Service |
| Custom TCP | TCP | 3005 | 0.0.0.0/0 | Email Service |
| Custom TCP | TCP | 15672 | Your IP | RabbitMQ UI |

7. Storage: **20 GB** minimum
8. Launch instance

### 1.2 Connect to EC2

```bash
# Connect via SSH
ssh -i your-key.pem ubuntu@your-ec2-public-ip

# Or use EC2 Instance Connect from AWS Console
```

### 1.3 Setup EC2

```bash
# Download and run setup script
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/notification-system/main/scripts/setup-ec2.sh -o setup-ec2.sh
chmod +x setup-ec2.sh
./setup-ec2.sh

# Logout and login again for Docker group changes
exit
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

## Step 2: Configure GitHub Secrets for SSH Deployment

**Note**: This deployment uses **SSH only** - no AWS credentials needed!

See **[SSH_DEPLOYMENT_GUIDE.md](./SSH_DEPLOYMENT_GUIDE.md)** for detailed SSH setup and troubleshooting.

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these **3 secrets** (SSH-based deployment):

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `EC2_HOST` | your-ec2-public-ip | EC2 public IP address |
| `EC2_USER` | ubuntu | EC2 username (default: ubuntu) |
| `EC2_SSH_KEY` | Your private key content | Full SSH private key (.pem file) |

### 2.1 Get SSH Private Key

```bash
# Display your private key
cat your-key.pem

# Or copy to clipboard (macOS)
cat your-key.pem | pbcopy

# Or copy to clipboard (Linux with xclip)
cat your-key.pem | xclip -selection clipboard
```

**Important**: Copy the **entire content** including:
- `-----BEGIN RSA PRIVATE KEY-----` (or `BEGIN OPENSSH PRIVATE KEY`)
- All the key content
- `-----END RSA PRIVATE KEY-----` (or `END OPENSSH PRIVATE KEY`)

Example format:
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
(many lines of key data)
...
-----END RSA PRIVATE KEY-----
```

**Note**: The deployment uses **SSH only** - no AWS credentials needed in GitHub secrets!

## Step 3: Clone Repository on EC2

```bash
# On EC2 instance
mkdir -p ~/notification-system
cd ~/notification-system
git clone https://github.com/YOUR_USERNAME/notification-system.git .

# Set up environment
cp .env.production .env

# Edit environment variables
nano .env
```

Update these values in `.env`:
- `POSTGRES_PASSWORD`
- `REDIS_PASSWORD`
- `RABBITMQ_PASS`
- `JWT_SECRET`

## Step 4: Test Manual Deployment

```bash
# On EC2 instance
./start.sh

# Check services
docker-compose -f docker-compose.minimal.yml ps

# Test endpoints
curl http://localhost:3000/health
curl http://localhost:3004/health
curl http://localhost:3003/health
curl http://localhost:3005/health
```

## Step 5: Test GitHub Actions

1. Make a small change to your repository
2. Commit and push to main branch
3. Go to GitHub → Actions tab
4. Watch the deployment workflow

## Step 6: Verify Deployment

After GitHub Actions completes:

```bash
# Check your services
curl http://YOUR_EC2_PUBLIC_IP:3000/health
curl http://YOUR_EC2_PUBLIC_IP:3004/health
curl http://YOUR_EC2_PUBLIC_IP:3003/health
curl http://YOUR_EC2_PUBLIC_IP:3005/health
```

## Service URLs

Replace `YOUR_EC2_PUBLIC_IP` with your actual EC2 public IP:

- **API Gateway**: http://YOUR_EC2_PUBLIC_IP:3000
- **Template Service**: http://YOUR_EC2_PUBLIC_IP:3004/docs
- **Push Service**: http://YOUR_EC2_PUBLIC_IP:3003/docs
- **Email Service**: http://YOUR_EC2_PUBLIC_IP:3005/docs
- **RabbitMQ UI**: http://YOUR_EC2_PUBLIC_IP:15672 (admin/your-password)

## Monitoring

### Check Deployment Status

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@your-ec2-public-ip

# Check services
cd ~/notification-system
docker-compose -f docker-compose.minimal.yml ps

# Check logs
docker-compose -f docker-compose.minimal.yml logs -f
```

### Health Monitoring

```bash
# Create health check script
cat > ~/health-check.sh << 'EOF'
#!/bin/bash
echo "Checking services..."
curl -f http://localhost:3000/health && echo " ✅ API Gateway"
curl -f http://localhost:3004/health && echo " ✅ Template Service"
curl -f http://localhost:3003/health && echo " ✅ Push Service"
curl -f http://localhost:3005/health && echo " ✅ Email Service"
EOF

chmod +x ~/health-check.sh

# Run health check
./health-check.sh
```

## Troubleshooting

### Deployment Fails

1. Check GitHub Actions logs
2. SSH to EC2 and check:
   ```bash
   cd ~/notification-system
   docker-compose -f docker-compose.minimal.yml logs
   ```

### Services Won't Start

```bash
# Check Docker
docker ps
docker-compose -f docker-compose.minimal.yml ps

# Check logs
docker-compose -f docker-compose.minimal.yml logs [service-name]

# Restart services
docker-compose -f docker-compose.minimal.yml restart
```

### Port Issues

```bash
# Check what's using ports
sudo lsof -i :3000
sudo lsof -i :3004

# Check firewall
sudo ufw status
```

### GitHub Actions SSH Issues

**Common SSH problems:**

1. **SSH Key Format**
   - Verify `EC2_SSH_KEY` contains the full private key
   - Include `-----BEGIN` and `-----END` lines
   - No extra spaces or line breaks

2. **Connection Issues**
   - Check `EC2_HOST` is the public IP (not private IP)
   - Verify security group allows SSH (port 22) from anywhere (0.0.0.0/0)
   - GitHub Actions uses dynamic IPs, so you can't restrict to specific IPs

3. **Permission Issues**
   - Ensure EC2 user is `ubuntu` (default for Ubuntu AMI)
   - Verify the SSH key matches the one used when launching EC2

4. **Test SSH Connection Manually**
   ```bash
   # From your local machine
   ssh -i your-key.pem ubuntu@YOUR_EC2_IP
   
   # If this works, GitHub Actions should work too
   ```

## Security Best Practices

1. **Use strong passwords** in `.env`
2. **Restrict RabbitMQ UI** to your IP only
3. **Enable SSL/TLS** for production (use nginx reverse proxy)
4. **Regular updates**:
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```
5. **Monitor logs** regularly
6. **Backup database** regularly:
   ```bash
   docker-compose -f docker-compose.minimal.yml exec postgres_template \
     pg_dump -U admin template_service > backup_$(date +%Y%m%d).sql
   ```

## Cost Optimization

- **t3.medium**: ~$30/month
- **t3.large**: ~$60/month
- Use **Reserved Instances** for 1-year commitment (30-50% savings)
- Set up **CloudWatch billing alerts**

## Scaling

For higher traffic:

1. Use **Application Load Balancer**
2. **Auto Scaling Group** with multiple EC2 instances
3. **RDS** for managed PostgreSQL
4. **ElastiCache** for managed Redis
5. **Amazon MQ** for managed RabbitMQ

## Additional Resources

- **SSH Deployment Guide**: [SSH_DEPLOYMENT_GUIDE.md](./SSH_DEPLOYMENT_GUIDE.md) - Detailed SSH setup and troubleshooting
- **Quick Start**: [../AWS_QUICK_START.md](../AWS_QUICK_START.md) - 5-minute setup guide
- **Deployment Summary**: [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md) - Quick reference

## Next Steps

1. Set up **SSL certificates** (Let's Encrypt) - see `scripts/setup-ssl.sh`
2. Configure **nginx reverse proxy** - see `nginx/nginx.conf`
3. Set up **CloudWatch monitoring**
4. Configure **log aggregation**
5. Set up **automated backups**
