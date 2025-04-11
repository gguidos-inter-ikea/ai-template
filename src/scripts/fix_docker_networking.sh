#!/bin/bash
# Script to fix common Docker networking issues with MongoDB and Redis
# Meant to be run from the project root directory

# Text colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if docker-compose is installed
if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: docker compose is not installed${NC}"
    echo "Please install Docker Compose first"
    exit 1
fi

# Determine docker compose command
DOCKER_COMPOSE="docker compose"
if ! command -v docker compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
fi

echo -e "${BLUE}=== Docker Networking Fix Script ===${NC}"
echo "This script will help resolve common networking issues with MongoDB and Redis in Docker."
echo ""

# 1. Check if containers are running
echo -e "${BLUE}Step 1: Checking container status...${NC}"
$DOCKER_COMPOSE ps

# 2. Check Docker networks
echo -e "\n${BLUE}Step 2: Checking Docker networks...${NC}"
NETWORK_NAME=$(grep -o 'network:.*' docker-compose.yml | head -1 | awk '{print $2}')
if [ -z "$NETWORK_NAME" ]; then
    echo -e "${YELLOW}Could not automatically determine network name from docker-compose.yml${NC}"
    NETWORK_NAME="default"
fi

echo "Looking for network: $NETWORK_NAME"
NETWORK_EXISTS=$(docker network ls | grep -c "$NETWORK_NAME")

if [ "$NETWORK_EXISTS" -eq 0 ]; then
    echo -e "${YELLOW}Network $NETWORK_NAME not found, creating it...${NC}"
    docker network create "$NETWORK_NAME"
else
    echo -e "${GREEN}Network $NETWORK_NAME exists${NC}"
fi

# 3. Verify .env file settings
echo -e "\n${BLUE}Step 3: Checking .env file database settings...${NC}"
if [ ! -f .env ]; then
    echo -e "${YELLOW}No .env file found. Creating one from .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}Created .env file from .env.example${NC}"
    else
        echo -e "${RED}No .env.example file found. Creating a basic .env file...${NC}"
        cat > .env << EOF
MONGODB_URI=mongodb://mongodb:27017
MONGODB_DBNAME=app
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
EOF
        echo -e "${GREEN}Created basic .env file with Docker network settings${NC}"
    fi
else
    # Check MongoDB settings
    MONGODB_URI=$(grep MONGODB_URI .env | cut -d '=' -f2)
    if [ -z "$MONGODB_URI" ]; then
        echo -e "${YELLOW}MONGODB_URI not found in .env, adding it...${NC}"
        echo "MONGODB_URI=mongodb://mongodb:27017" >> .env
    elif [[ $MONGODB_URI == *"localhost"* ]]; then
        echo -e "${YELLOW}MONGODB_URI is set to localhost, which won't work in Docker.${NC}"
        echo -e "${YELLOW}Changing it to use the service name...${NC}"
        sed -i.bak 's/mongodb:\/\/localhost/mongodb:\/\/mongodb/g' .env
        echo -e "${GREEN}Updated MONGODB_URI to use service name${NC}"
    else
        echo -e "${GREEN}MONGODB_URI looks good: $MONGODB_URI${NC}"
    fi
    
    # Check Redis settings
    REDIS_HOST=$(grep REDIS_HOST .env | cut -d '=' -f2)
    if [ -z "$REDIS_HOST" ]; then
        echo -e "${YELLOW}REDIS_HOST not found in .env, adding it...${NC}"
        echo "REDIS_HOST=redis" >> .env
    elif [ "$REDIS_HOST" == "localhost" ]; then
        echo -e "${YELLOW}REDIS_HOST is set to localhost, which won't work in Docker.${NC}"
        echo -e "${YELLOW}Changing it to use the service name...${NC}"
        sed -i.bak 's/REDIS_HOST=localhost/REDIS_HOST=redis/g' .env
        echo -e "${GREEN}Updated REDIS_HOST to use service name${NC}"
    else
        echo -e "${GREEN}REDIS_HOST looks good: $REDIS_HOST${NC}"
    fi
    
    # Check Redis DB is within range
    REDIS_DB=$(grep REDIS_DB .env | cut -d '=' -f2)
    if ! [[ "$REDIS_DB" =~ ^[0-9]+$ ]] || [ "$REDIS_DB" -gt 15 ]; then
        echo -e "${YELLOW}REDIS_DB is invalid or out of range (0-15).${NC}"
        echo -e "${YELLOW}Setting it to 0...${NC}"
        sed -i.bak 's/REDIS_DB=.*/REDIS_DB=0/g' .env
        echo -e "${GREEN}Updated REDIS_DB to 0${NC}"
    else
        echo -e "${GREEN}REDIS_DB looks good: $REDIS_DB${NC}"
    fi
fi

# 4. Restart containers
echo -e "\n${BLUE}Step 4: Restarting containers...${NC}"
echo -e "${YELLOW}Stopping containers...${NC}"
$DOCKER_COMPOSE down
echo -e "${YELLOW}Starting containers...${NC}"
$DOCKER_COMPOSE up -d

# 5. Verify connectivity from app container
echo -e "\n${BLUE}Step 5: Verifying connectivity...${NC}"
echo "Waiting 5 seconds for containers to initialize..."
sleep 5

echo -e "${YELLOW}Testing connection from app to MongoDB...${NC}"
$DOCKER_COMPOSE exec -T app ping -c 2 mongodb || echo -e "${RED}Could not ping MongoDB from app container${NC}"

echo -e "${YELLOW}Testing connection from app to Redis...${NC}"
$DOCKER_COMPOSE exec -T app ping -c 2 redis || echo -e "${RED}Could not ping Redis from app container${NC}"

# 6. Run the connection test script
echo -e "\n${BLUE}Step 6: Running database connection test script...${NC}"
$DOCKER_COMPOSE exec -T app python -m src.scripts.test_db_connection || echo -e "${RED}Database connection test failed${NC}"

echo -e "\n${GREEN}Fix script completed!${NC}"
echo "If you're still experiencing issues, check the troubleshooting tips in src/scripts/README.md" 