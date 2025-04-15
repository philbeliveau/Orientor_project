#!/bin/bash

# Function to stop background processes on exit
cleanup() {
    echo "Stopping servers..."
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID
    fi
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID
    fi
    exit
}

# Register cleanup function to run on exit
trap cleanup EXIT INT TERM

# Checking if .env files exist
if [ ! -f "./backend/.env" ]; then
    echo "Error: backend/.env file not found."
    echo "Please create this file with your API keys before running."
    exit 1
fi

echo "============================================"
echo "🚀 Starting OaSIS Vector Search Development"
echo "============================================"

# Start the FastAPI backend
echo "📡 Starting FastAPI Backend on http://localhost:8000"
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Give the backend a moment to start
sleep 2

# Start the Next.js frontend
echo "🌐 Starting Next.js Frontend on http://localhost:3000"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Development environment is running!"
echo "- Frontend: http://localhost:3000"
echo "- Backend: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo ""
echo "💡 To view the vector search demo, visit: http://localhost:3000/vector-search"
echo ""
echo "Press Ctrl+C to stop all servers."

# Wait for user to press Ctrl+C
wait 