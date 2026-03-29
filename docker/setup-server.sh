#!/bin/bash
# Garmin Workout Creator - Docker Server Setup Script

set -e

echo "=================================="
echo "Garmin Workout Creator Setup"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env

    echo ""
    echo -e "${YELLOW}Generating security keys...${NC}"

    # Generate SECRET_KEY
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i.bak "s/your-secret-key-here/$SECRET_KEY/" .env
    echo -e "${GREEN}✓ Generated SECRET_KEY${NC}"

    # Generate ENCRYPTION_KEY
    ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    sed -i.bak "s|your-encryption-key-here|$ENCRYPTION_KEY|" .env
    echo -e "${GREEN}✓ Generated ENCRYPTION_KEY${NC}"

    # Clean up backup file
    rm .env.bak

    echo ""
    echo -e "${YELLOW}⚠ IMPORTANT: Edit .env and add your API keys:${NC}"
    echo "  - GOOGLE_API_KEY (required)"
    echo "  - DB_USER and DB_PASSWORD (set secure values)"
    echo ""
    read -p "Press Enter when you've updated the .env file..."
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

echo ""
echo -e "${YELLOW}Checking .env configuration...${NC}"

# Source .env file
source .env

# Check required variables
MISSING_VARS=()

if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your-google-gemini-api-key" ]; then
    MISSING_VARS+=("GOOGLE_API_KEY")
fi

if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-secret-key-here" ]; then
    MISSING_VARS+=("SECRET_KEY")
fi

if [ -z "$ENCRYPTION_KEY" ] || [ "$ENCRYPTION_KEY" = "your-encryption-key-here" ]; then
    MISSING_VARS+=("ENCRYPTION_KEY")
fi

if [ -z "$DB_PASSWORD" ] || [ "$DB_PASSWORD" = "change-this-secure-password" ]; then
    MISSING_VARS+=("DB_PASSWORD")
fi

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo -e "${RED}Error: Missing or unconfigured environment variables:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    echo ""
    echo "Please edit docker/.env and set these variables"
    exit 1
fi

echo -e "${GREEN}✓ All required environment variables are set${NC}"
echo ""

# Ask which compose file to use
echo "Which environment do you want to start?"
echo "1) Development (with hot reload)"
echo "2) Production (optimized)"
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        COMPOSE_FILE="docker-compose.yml"
        ENV_TYPE="development"
        ;;
    2)
        COMPOSE_FILE="docker-compose.prod.yml"
        ENV_TYPE="production"
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${YELLOW}Building and starting $ENV_TYPE environment...${NC}"
echo ""

# Build and start services
docker-compose -f $COMPOSE_FILE build
docker-compose -f $COMPOSE_FILE up -d

echo ""
echo -e "${GREEN}✓ Services starting...${NC}"
echo ""

# Wait for services to be healthy
echo "Waiting for services to become healthy..."
sleep 10

# Check service status
echo ""
docker-compose -f $COMPOSE_FILE ps

echo ""
echo "=================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=================================="
echo ""
echo "Your application is now running:"
echo ""
echo "  Frontend:  http://localhost"
echo "  API:       http://localhost/api"
echo "  Health:    http://localhost/health"
echo ""
echo "Useful commands:"
echo "  View logs:    docker-compose -f $COMPOSE_FILE logs -f"
echo "  Stop server:  docker-compose -f $COMPOSE_FILE down"
echo "  Restart:      docker-compose -f $COMPOSE_FILE restart"
echo ""
echo "For more information, see docker/README.md"
echo ""
