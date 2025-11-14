#!/bin/bash
# Log Monitoring Script
# Monitors logs for errors and warnings

set -e

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "Log Monitor - Checking for Errors"
echo "=========================================="
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose not found${NC}"
    exit 1
fi

# Get logs from last hour
SINCE=${1:-1h}

echo "Checking logs from last $SINCE..."
echo ""

# Count errors
ERROR_COUNT=$(docker-compose -f docker-compose.minimal.yml logs --since $SINCE 2>/dev/null | grep -i error | wc -l)
WARNING_COUNT=$(docker-compose -f docker-compose.minimal.yml logs --since $SINCE 2>/dev/null | grep -i warning | wc -l)

echo "Summary:"
echo "--------"
echo -e "Errors:   ${RED}$ERROR_COUNT${NC}"
echo -e "Warnings: ${YELLOW}$WARNING_COUNT${NC}"
echo ""

if [ $ERROR_COUNT -gt 0 ]; then
    echo "Recent Errors:"
    echo "--------------"
    docker-compose -f docker-compose.minimal.yml logs --since $SINCE 2>/dev/null | grep -i error | tail -10
    echo ""
fi

if [ $WARNING_COUNT -gt 0 ]; then
    echo "Recent Warnings:"
    echo "----------------"
    docker-compose -f docker-compose.minimal.yml logs --since $SINCE 2>/dev/null | grep -i warning | tail -10
    echo ""
fi

# Check container status
echo "Container Status:"
echo "-----------------"
docker-compose -f docker-compose.minimal.yml ps

echo ""
echo "=========================================="

if [ $ERROR_COUNT -eq 0 ]; then
    echo "✅ No errors found in last $SINCE"
else
    echo "⚠️  Found $ERROR_COUNT errors in last $SINCE"
fi
