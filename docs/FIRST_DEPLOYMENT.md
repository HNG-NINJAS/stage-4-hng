# First Time Deployment to EC2

## Overview

The GitHub Actions workflow now handles **automatic setup** on first deployment. You don't need to manually clone the repository!

## What Happens on First Deployment

When you push to GitHub for the first time:

1. ✅ GitHub Actions connects via SSH
2. ✅ Detects no project directory exists
3. ✅ Automatically clones the repository
4. ✅ Creates `.env` from `.env.production`
5. ✅ Builds Docker images
6. ✅ Starts all services
7. ✅ Seeds templates
8. ✅ Runs health checks

## Prerequisites

### 1. EC2 Instance Setup

Your EC2 must have Docker and Docker Compose installed:

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Run setup script
curl -fsSL https://raw.githubusercontent.com/HNG-NINJAS/stage-4-hng/main/scripts/setup-ec2.sh -o setup-ec2.sh
chmod +x setup-ec2.sh
./setup-ec2.sh

# Logout and login again (important for Docker group)
exit
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

### 2. GitHub Secrets Configured

Make sure these 3 secrets are set:
- `EC2_HOST` - Your EC2 public IP
- `EC2_USER` - `ubuntu`
- `EC2_SSH_KEY` - Your `.pem` file content

## First Deployment Steps

### Step 1: Push to GitHub

```bash
# From your local machine
git add .
git commit -m "Initial deployment"
git push origin main
```

### Step 2: Watch GitHub Actions

1. Go to: https://github.com/HNG-NINJAS/stage-4-hng/actions
2. Click on the running workflow
3. Watch the deployment progress

You should see:
```
📁 First time setup - cloning repository...
⚙️ Creating .env file from production template...
🔨 Building Docker images...
🚀 Starting services...
✅ Deployment completed successfully!
```

### Step 3: Update Environment Variables

After first deployment, SSH to EC2 and update passwords:

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
cd ~/notification-system
nano .env
```

Update these values:
```bash
POSTGRES_PASSWORD=your_strong_password_here
REDIS_PASSWORD=your_redis_password_here
RABBITMQ_PASS=your_rabbitmq_password_here
JWT_SECRET=your_very_long_random_secret_here
```

Save and restart services:
```bash
docker-compose -f docker-compose.minimal.yml restart
```

### Step 4: Verify Deployment

```bash
# Check services are running
docker-compose -f docker-compose.minimal.yml ps

# Test endpoints
curl http://localhost:3000/health
curl http://localhost:3004/health
curl http://localhost:3003/health
curl http://localhost:3005/health
```

From your local machine:
```bash
curl http://YOUR_EC2_IP:3000/health
curl http://YOUR_EC2_IP:3004/health
curl http://YOUR_EC2_IP:3003/health
curl http://YOUR_EC2_IP:3005/health
```

## Subsequent Deployments

After the first deployment, future pushes will:

1. ✅ Pull latest code (no cloning)
2. ✅ Keep your `.env` file (no overwrite)
3. ✅ Rebuild and restart services
4. ✅ Run health checks

## Troubleshooting First Deployment

### Issue: "git: command not found"

**Solution**: Run the EC2 setup script
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
curl -fsSL https://raw.githubusercontent.com/HNG-NINJAS/stage-4-hng/main/scripts/setup-ec2.sh -o setup-ec2.sh
chmod +x setup-ec2.sh
./setup-ec2.sh
```

### Issue: "docker: command not found"

**Solution**: 
1. Run setup script
2. Logout and login again (important!)
```bash
exit
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

### Issue: "Permission denied" for Docker

**Solution**: User needs to be in docker group
```bash
sudo usermod -aG docker ubuntu
exit
# Login again
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

### Issue: Services fail to start

**Solution**: Check logs
```bash
cd ~/notification-system
docker-compose -f docker-compose.minimal.yml logs
```

### Issue: Port already in use

**Solution**: Stop conflicting services
```bash
# Check what's using the port
sudo lsof -i :3000

# Stop the service
sudo systemctl stop <service-name>
```

## Manual First Deployment (Alternative)

If you prefer to set up manually before using GitHub Actions:

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Clone repository
git clone https://github.com/HNG-NINJAS/stage-4-hng.git ~/notification-system
cd ~/notification-system

# Setup environment
cp .env.production .env
nano .env  # Update passwords

# Deploy
./start.sh

# Verify
docker-compose -f docker-compose.minimal.yml ps
```

Then future GitHub Actions pushes will just update the code.

## Security Reminder

⚠️ **Important**: After first deployment, always update these in `.env`:
- `POSTGRES_PASSWORD`
- `REDIS_PASSWORD`
- `RABBITMQ_PASS`
- `JWT_SECRET`

Don't use the default values from `.env.production`!

## Service URLs

After successful deployment:

- **API Gateway**: http://YOUR_EC2_IP:3000
- **Template Service**: http://YOUR_EC2_IP:3004/docs
- **Push Service**: http://YOUR_EC2_IP:3003/docs
- **Email Service**: http://YOUR_EC2_IP:3005/docs
- **RabbitMQ UI**: http://YOUR_EC2_IP:15672

## Next Steps

1. ✅ First deployment complete
2. Update `.env` passwords on EC2
3. Test all service endpoints
4. Set up SSL (optional): `./scripts/setup-ssl.sh your-domain.com`
5. Configure monitoring
6. Set up automated backups

## Workflow Summary

```
First Push:
  → Clone repo
  → Create .env
  → Build images
  → Start services
  → ✅ Done

Subsequent Pushes:
  → Pull latest code
  → Rebuild images
  → Restart services
  → ✅ Done
```

Your deployment is now automated! 🚀
