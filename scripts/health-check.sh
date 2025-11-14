#!/bin/bash
# Health Check Script for Notification System
# Run this to check if all services are healthy

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Notification System Health Check"
echo "=========================================="
echo ""

# Function to check service health
check_service() {
    local url=$1
    local name=$2
    
    if curl -f -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name - Healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ $name - FAILED${NC}"
        return 1
    fi
}

# Check if running locally or on EC2
if [ -z "$1" ]; then
    HOST="localhost"
else
    HOST=$1
fi

echo "Checking services on: $HOST"
echo ""

# Track failures
FAILURES=0

# Check each service
check_service "http://$HOST:3000/health" "API Gateway" || ((FAILURES++))
check_service "http://$HOST:3004/health" "Template Service" || ((FAILURES++))
check_service "http://$HOST:3003/health" "Push Service" || ((FAILURES++))
check_service "http://$HOST:3005/health" "Email Service" || ((FAILURES++))

echo ""
echo "=========================================="

if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✅ All services are healthy!${NC}"
    exit 0
else
    echo -e "${RED}❌ $FAILURES service(s) failed!${NC}"
    exit 1
fi
