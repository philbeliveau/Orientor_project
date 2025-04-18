#!/bin/bash

# Exit on error
set -e

echo "Starting Reactive Resume with Orientor integration..."

# Check if Reactive-Resume directory exists
if [ ! -d "Reactive-Resume" ]; then
  echo "Reactive-Resume directory not found. Cloning repository..."
  git clone https://github.com/AmruthPillai/Reactive-Resume.git
  cd Reactive-Resume
else
  cd Reactive-Resume
  echo "Reactive-Resume directory found. Pulling latest changes..."
  git pull
fi

# Copy environment configuration if it doesn't exist
if [ ! -f ".env" ]; then
  echo "Creating .env file from .env.example..."
  cp .env.example .env
  
  # Ask for JWT secret key to ensure it matches with Orientor backend
  read -p "Enter your Orientor JWT secret key: " jwt_secret
  sed -i '' "s/your-orientor-secret-key/$jwt_secret/g" .env
  
  echo "Environment file created. You may need to edit .env to configure database and other settings."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Docker is not running. Please start Docker and try again."
  exit 1
fi

# Run with Docker Compose
echo "Starting Reactive Resume with Docker Compose..."
docker-compose -f compose.yml up --build

# Provide instructions
echo ""
echo "==================================================="
echo "Reactive Resume is now running!"
echo "- Web UI: http://localhost:3100"
echo "- API: http://localhost:3100/api"
echo ""
echo "To stop the services, press Ctrl+C"
echo "===================================================" 