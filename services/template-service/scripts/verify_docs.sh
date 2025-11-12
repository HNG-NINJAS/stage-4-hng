#!/bin/bash
# Script to verify documentation structure and links

set -e

echo "🔍 Verifying Template Service Documentation..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

# Function to check if file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $1 - MISSING"
        ((FAILED++))
    fi
}

# Function to check if directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $1/ - MISSING"
        ((FAILED++))
    fi
}

echo "📁 Checking Documentation Structure..."
echo ""

# Root documentation files
echo "Root Documentation:"
check_file "README.md"
check_file "docs/README.md"
check_file "docs/getting-started.md"
check_file "docs/api-reference.md"
check_file "docs/ARCHITECTURE.md"
check_file "docs/deployment.md"
check_file "docs/development.md"
check_file "docs/SUMMARY.md"
echo ""

# Examples
echo "Examples:"
check_dir "docs/examples"
check_file "docs/examples/README.md"
check_file "docs/examples/python_client.py"
check_file "docs/examples/nodejs_client.js"
check_file "docs/examples/csharp_client.cs"
echo ""

# Integration guides
echo "Integration Guides:"
check_dir "docs/integration"
check_file "docs/integration/README.md"
check_file "docs/integration/overview.md"
check_file "docs/integration/python-client.md"
check_file "docs/integration/typescript-client.md"
check_file "docs/integration/csharp-client.md"
check_file "docs/integration/events.md"
echo ""

# Operations
echo "Operations:"
check_dir "docs/operations"
check_file "docs/operations/monitoring.md"
check_file "docs/operations/database.md"
echo ""

# Check for old redundant files
echo "🗑️  Checking for Redundant Files..."
echo ""

REDUNDANT_FILES=(
    "INTEGRATION.md"
    "INTEGRATION2.md"
    "INTEGRATION3.md"
)

for file in "${REDUNDANT_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${YELLOW}⚠${NC} $file - Should be removed (redundant)"
        ((FAILED++))
    else
        echo -e "${GREEN}✓${NC} $file - Properly removed"
        ((PASSED++))
    fi
done
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Verification Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}Passed:${NC} $PASSED"
echo -e "${RED}Failed:${NC} $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All documentation checks passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some documentation checks failed!${NC}"
    exit 1
fi
