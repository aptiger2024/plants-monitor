#!/bin/bash

# Plant Moisture Monitor - Docker Setup Verification Script
# Run this to verify all Docker files are in place and valid

echo "=========================================="
echo "Plant Moisture Monitor - Docker Verification"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

# Function to check file exists
check_file() {
    local file=$1
    local description=$2

    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $description ($file)"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $description ($file) - NOT FOUND"
        ((FAILED++))
    fi
}

# Function to check directory exists
check_dir() {
    local dir=$1
    local description=$2

    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $description ($dir)"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} $description ($dir) - Will be created"
    fi
}

# Function to validate YAML/JSON syntax
validate_yaml() {
    local file=$1

    if command -v python3 &> /dev/null; then
        python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓${NC} YAML syntax valid"
            ((PASSED++))
        else
            echo -e "${RED}✗${NC} YAML syntax invalid"
            ((FAILED++))
        fi
    else
        echo -e "${YELLOW}⚠${NC} Python not available for YAML validation"
    fi
}

# Function to check Python syntax
check_python_syntax() {
    local file=$1

    if command -v python3 &> /dev/null; then
        python3 -m py_compile "$file" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓${NC} Python syntax valid"
            ((PASSED++))
        else
            echo -e "${RED}✗${NC} Python syntax invalid"
            ((FAILED++))
        fi
    fi
}

echo "Checking required files..."
echo "=========================="

# Docker files
check_file "docker-compose.yml" "Docker Compose configuration"
check_file "Dockerfile.api" "API Dockerfile"
check_file "nginx.conf" "Nginx configuration"
check_file ".dockerignore" "Docker ignore file"

# Application files
check_file "backend.py" "FastAPI backend"
check_file "dashboard.html" "Web dashboard"
check_file "requirements.txt" "Python dependencies"

# Documentation
check_file "PORTAINER_QUICK_START.md" "Portainer quick start guide"
check_file "DOCKER_DEPLOYMENT.md" "Docker deployment guide"
check_file "DOCKER_SETUP_SUMMARY.md" "Docker setup summary"
check_file "API_DOCS.md" "API documentation"
check_file "INTEGRATION_GUIDE.md" "Integration guide"

echo ""
echo "Checking file contents..."
echo "========================="

# Validate docker-compose.yml
if [ -f "docker-compose.yml" ]; then
    echo "Validating docker-compose.yml..."
    validate_yaml "docker-compose.yml"
fi

# Validate backend.py
if [ -f "backend.py" ]; then
    echo "Checking backend.py syntax..."
    check_python_syntax "backend.py"
fi

# Check requirements.txt format
if [ -f "requirements.txt" ]; then
    echo -n "Checking requirements.txt... "
    if grep -q "fastapi\|sqlalchemy\|uvicorn" requirements.txt; then
        echo -e "${GREEN}✓${NC} (Contains expected packages)"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} (Missing expected packages)"
        ((FAILED++))
    fi
fi

# Check Dockerfile
if [ -f "Dockerfile.api" ]; then
    echo -n "Checking Dockerfile.api... "
    if grep -q "FROM python\|uvicorn" Dockerfile.api; then
        echo -e "${GREEN}✓${NC} (Valid Dockerfile structure)"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} (Missing expected commands)"
        ((FAILED++))
    fi
fi

# Check nginx.conf
if [ -f "nginx.conf" ]; then
    echo -n "Checking nginx.conf... "
    if grep -q "upstream\|location\|proxy_pass" nginx.conf; then
        echo -e "${GREEN}✓${NC} (Valid Nginx configuration)"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} (Missing expected directives)"
        ((FAILED++))
    fi
fi

echo ""
echo "Checking directories..."
echo "======================="

check_dir "esphome-config" "ESPHome configuration"

echo ""
echo "Checking Docker prerequisites..."
echo "================================"

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker is installed ($(docker --version))"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Docker is NOT installed"
    ((FAILED++))
fi

# Check if Docker Compose is available
if docker compose version &> /dev/null 2>&1 || docker-compose --version &> /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Docker Compose is available"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Docker Compose not found (will be available on server)"
fi

# Check if Docker daemon is running
if docker ps &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker daemon is running"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Docker daemon is not running (will work on server)"
fi

echo ""
echo "File size check..."
echo "================="

echo -n "backend.py: "
if [ -f "backend.py" ]; then
    SIZE=$(wc -c < backend.py)
    echo "$SIZE bytes"
    if [ $SIZE -gt 5000 ]; then
        echo -e "${GREEN}✓${NC} Backend is substantial"
        ((PASSED++))
    fi
fi

echo -n "dashboard.html: "
if [ -f "dashboard.html" ]; then
    SIZE=$(wc -c < dashboard.html)
    echo "$SIZE bytes"
    if [ $SIZE -gt 10000 ]; then
        echo -e "${GREEN}✓${NC} Dashboard is substantial"
        ((PASSED++))
    fi
fi

echo ""
echo "Summary"
echo "======="
echo -e "${GREEN}Passed:${NC} $PASSED"
echo -e "${RED}Failed:${NC} $FAILED"

echo ""
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Docker setup is ready for deployment.${NC}"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please review and fix issues above.${NC}"
    exit 1
fi
