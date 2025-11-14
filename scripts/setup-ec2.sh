#!/bin/bash
# EC2 Setup Script for Notification System
# Run this script on your EC2 instance to prepare it for deployment

set -e

echo "=========================================="
echo "Setting up EC2 for Notification System"
echo "=========================================="

# Update system
echo "📦 Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
echo "📚 Installing Git..."
sudo apt-get install -y git

# Install other utilities
echo "🛠️ Installing utilities..."
sudo apt-get install -y curl wget htop unzip

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 3000/tcp    # API Gateway
sudo ufw allow 3003/tcp    # Push Service
sudo ufw allow 3004/tcp    # Template Service
sudo ufw allow 3005/tcp    # Email Service
sudo ufw allow 15672/tcp   # RabbitMQ UI
sudo ufw --force enable

# Create project directory
echo "📁 Creating project directory..."
mkdir -p ~/notification-system

# Create logs directory
mkdir -p ~/notification-system/logs

echo "✅ EC2 setup completed!"
echo ""
echo "Next steps:"
echo "1. Clone your repository to ~/notification-system"
echo "2. Update .env file with production values"
echo "3. Run: ./start.sh"
echo ""
echo "Service URLs will be:"
echo "  API Gateway:      http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3000"
echo "  Template Service: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3004/docs"
echo "  Push Service:     http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3003/docs"
echo "  Email Service:    http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3005/docs"
echo "  RabbitMQ UI:      http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):15672"
echo ""
echo "🎉 Ready for deployment!"
echo ""
echo "⚠️  IMPORTANT: Logout and login again for Docker group changes to take effect"
