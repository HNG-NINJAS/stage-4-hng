#!/bin/bash

# Simple start script - always uses the correct compose file
# This prevents accidentally using the wrong docker-compose command

echo "=========================================="
echo "Starting Notification System"
echo "=========================================="
echo ""
echo "Using minimal setup (4 services, no port conflicts)"
echo ""

# Stop any running containers
echo "Stopping any running containers..."
docker-compose down 2>/dev/null
docker-compose -f docker-compose.minimal.yml down 2>/dev/null
echo ""

# Start minimal setup
echo "Starting services..."
docker-compose -f docker-compose.minimal.yml up -d
echo ""

# Wait
echo "Waiting for services to be ready (30 seconds)..."
sleep 30
echo ""

# Seed templates
echo "Seeding templates..."
docker-compose -f docker-compose.minimal.yml exec -T template-service python scripts/seed_templates.py
echo ""

# Show status
echo "Service Status:"
docker-compose -f docker-compose.minimal.yml ps
echo ""

echo "✅ System is ready!"
echo ""
echo "Service URLs:"
echo "  API Gateway:      http://localhost:3000"
echo "  Template Service: http://localhost:3004/docs"
echo "  Push Service:     http://localhost:3003/docs"
echo "  Email Service:    http://localhost:3005/docs"
echo "  RabbitMQ UI:      http://localhost:15672 (admin/admin123)"
echo ""
echo "Test the system:"
echo "  bash scripts/test_complete_system.sh"
echo ""
echo "Record video:"
echo "  bash scripts/recording_script.sh"
echo ""
