#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BLUE='\033[0;34m'

echo -e "${BLUE}Starting test suite...${NC}\n"

# Function to run tests and check exit code
run_test() {
    echo -e "${BLUE}Running $1...${NC}"
    $2
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1 passed${NC}\n"
    else
        echo -e "${RED}✗ $1 failed${NC}\n"
        exit 1
    fi
}

# Check if we're running in Docker
if [ -f /.dockerenv ]; then
    # Inside Docker container
    TEST_CMD="pytest"
else
    # Local environment - use docker-compose exec
    TEST_CMD="docker compose exec -T api pytest"
fi

# Run linting first
run_test "Code formatting check" "black --check src tests"
run_test "Flake8 check" "flake8 src tests"
run_test "Type checking" "mypy src"

# Run unit tests
run_test "Unit tests" "$TEST_CMD tests/unit/ -v"

# Run integration tests
echo -e "${BLUE}Flushing Redis before integration tests...${NC}"
docker compose exec -T redis redis-cli FLUSHDB

run_test "Integration tests" "$TEST_CMD tests/integration/ -v"

# Run coverage report
echo -e "${BLUE}Generating coverage report...${NC}"
$TEST_CMD tests/ --cov=src --cov-report=html --cov-report=term

echo -e "${GREEN}All tests completed successfully!${NC}"
echo "Coverage report available in htmlcov/index.html" 