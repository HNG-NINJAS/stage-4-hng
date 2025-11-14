# EC2 Setup Required Before Deployment

## Error: docker-compose: command not found

This means your EC2 instance hasn't been set up yet with Docker and Docker Compose.

## Quick Fix

### Step 1: SSH to Your EC2 Instance

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

### Step 2: Run the Setup Script

```bash
# Download setup script
curl -fsSL https://raw.githubusercontent.com/HNG-NINJAS/stage-4-hng/main/scripts/setup-ec2.sh -o setup-ec2.sh

# Make it executable
chmod +x setup-ec2.sh

# Run it
./setup-ec2.sh
```

The script will install:
- ✅ Docker
- ✅ Docker Compose
- ✅ Git
- ✅ Other utilities
- ✅ Configure firewall

### Step 3: Logout and Login Again (Important!)

```bash
# Logout
exit

# Login again
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

**Why?** The setup script adds your user to the `docker` group. You need to logout/login for this to take effect.

### Step 4: Verify Installation

```bash
# Check Docker
docker --version
# Should show: Docker version 24.x.x

# Check Docker Compose
docker-compose --version
# Should show: docker-compose version 1.x.x or 2.x.x

# Check you can run Docker without sudo
docker ps
# Should work without permission errors
```

### Step 5: Re-run GitHub Actions

Now that EC2 is set up, go back to GitHub and re-run the workflow:

1. Go to: https://github.com/HNG-NINJAS/stage-4-hng/actions
2. Click on the failed workflow
3. Click **Re-run jobs** → **Re-run failed jobs**

## What the Setup Script Does

```bash
# Updates system
sudo apt-get update && sudo apt-get upgrade -y

# Installs Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Installs Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Installs Git
sudo apt-get install -y git

# Configures firewall
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 3000/tcp    # API Gateway
sudo ufw allow 3003/tcp    # Push Service
sudo ufw allow 3004/tcp    # Template Service
sudo ufw allow 3005/tcp    # Email Service
sudo ufw allow 15672/tcp   # RabbitMQ UI
sudo ufw --force enable
```

## Manual Installation (Alternative)

If you prefer to install manually:

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo apt-get update
sudo apt-get install -y git

# Logout and login again
exit
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Verify
docker --version
docker-compose --version
```

## Troubleshooting

### Issue: "Permission denied" when running docker

**Solution**: You need to logout and login again after setup
```bash
exit
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

### Issue: "Cannot connect to Docker daemon"

**Solution**: Start Docker service
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### Issue: Setup script fails

**Solution**: Check internet connection and try manual installation above

## After Setup

Once setup is complete:
1. ✅ Docker and Docker Compose installed
2. ✅ Firewall configured
3. ✅ Ready for deployment
4. ✅ GitHub Actions will work

Just push to GitHub or re-run the workflow!

## One-Time Setup

You only need to run the setup script **once** per EC2 instance. After that, all deployments will work automatically via GitHub Actions.

## Summary

```bash
# 1. SSH to EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# 2. Run setup
curl -fsSL https://raw.githubusercontent.com/HNG-NINJAS/stage-4-hng/main/scripts/setup-ec2.sh -o setup-ec2.sh
chmod +x setup-ec2.sh
./setup-ec2.sh

# 3. Logout and login
exit
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# 4. Verify
docker --version
docker-compose --version

# 5. Re-run GitHub Actions
# Done! ✅
```
