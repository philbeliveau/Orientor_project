#!/bin/bash

# Start backend with correct environment variables for local development
echo "🚀 Starting backend with local database configuration..."

# Clear any Railway environment variables
unset RAILWAY_ENVIRONMENT
unset DATABASE_PUBLIC_URL
unset RAILWAY_DATABASE_URL

# Set local database configuration
export DATABASE_URL="postgresql://postgres:Mac.phil.007@localhost:5432/navigo_local"
export LOCAL_DATABASE_URL="postgresql://postgres:Mac.phil.007@localhost:5432/navigo_local"
export ENV="development"

# Debug info
echo "Environment variables:"
echo "  DATABASE_URL: $DATABASE_URL"
echo "  LOCAL_DATABASE_URL: $LOCAL_DATABASE_URL"
echo "  ENV: $ENV"

# Start the server
echo "Starting uvicorn server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload