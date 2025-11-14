#!/bin/bash

# Test User Service Build
echo "=========================================="
echo "Testing User Service Build"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Attempting to build user-service...${NC}"
echo ""

# Try to build
if docker-compose build user-service 2>&1 | tee /tmp/user-service-build.log; then
    echo ""
    echo -e "${GREEN}✅ User Service built successfully!${NC}"
    echo ""
    echo "You can now use the full system:"
    echo "  docker-compose up -d"
    echo ""
    exit 0
else
    echo ""
    echo -e "${RED}❌ User Service build failed${NC}"
    echo ""
    echo "Build log saved to: /tmp/user-service-build.log"
    echo ""
    echo -e "${YELLOW}SOLUTION: Use minimal setup (4 services)${NC}"
    echo ""
    echo "The minimal setup works perfectly without user-service:"
    echo "  bash scripts/start_minimal.sh"
    echo ""
    echo "Or manually:"
    echo "  docker-compose -f docker-compose.minimal.yml build"
    echo "  docker-compose -f docker-compose.minimal.yml up -d"
    echo ""
    echo "This is recommended for:"
    echo "  ✅ Video recording"
    echo "  ✅ Server deployment"
    echo "  ✅ Live demonstration"
    echo ""
    exit 1
fi
