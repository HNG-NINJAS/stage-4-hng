#!/bin/bash
# SSL Setup Script for Notification System
# Run this on your EC2 instance after setting up a domain

set -e

DOMAIN=${1:-"your-domain.com"}

if [ "$DOMAIN" = "your-domain.com" ]; then
    echo "Usage: ./setup-ssl.sh your-actual-domain.com"
    exit 1
fi

echo "=========================================="
echo "Setting up SSL for $DOMAIN"
echo "=========================================="

# Install nginx
echo "📦 Installing nginx..."
sudo apt-get update
sudo apt-get install -y nginx

# Install certbot
echo "🔒 Installing certbot..."
sudo apt-get install -y certbot python3-certbot-nginx

# Stop nginx temporarily
sudo systemctl stop nginx

# Get SSL certificate
echo "📜 Getting SSL certificate..."
sudo certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# Copy nginx configuration
echo "⚙️ Setting up nginx configuration..."
sudo cp nginx/nginx.conf /etc/nginx/sites-available/notification-system

# Update domain in nginx config
sudo sed -i "s/your-domain.com/$DOMAIN/g" /etc/nginx/sites-available/notification-system

# Enable site
sudo ln -sf /etc/nginx/sites-available/notification-system /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Start nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Set up auto-renewal
echo "🔄 Setting up SSL auto-renewal..."
sudo crontab -l 2>/dev/null | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | sudo crontab -

echo "✅ SSL setup completed!"
echo ""
echo "Your services are now available at:"
echo "  https://$DOMAIN - API Gateway"
echo "  https://$DOMAIN/docs/templates - Template Service"
echo "  https://$DOMAIN/docs/push - Push Service"
echo "  https://$DOMAIN/docs/email - Email Service"
echo "  https://$DOMAIN/rabbitmq - RabbitMQ UI (restricted)"
echo ""
echo "🔒 SSL certificate will auto-renew"
