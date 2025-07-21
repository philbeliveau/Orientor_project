#!/bin/bash
# Railway Build Optimization Test Script
# Tests different build strategies to find the fastest approach

set -e

echo "🚀 Railway Build Optimization Script"
echo "===================================="
echo "Testing different build strategies for optimal performance"
echo ""

# Function to show options
show_options() {
    echo "Available optimization strategies:"
    echo ""
    echo "1. NIXPACKS + Staged Installation (Recommended)"
    echo "   - Uses Railway's native builder"
    echo "   - Installs packages in order of stability"
    echo "   - Expected: 4-6 minutes, good caching"
    echo ""
    echo "2. DOCKER + Single-Stage Optimized" 
    echo "   - Simple Dockerfile optimized for Railway"
    echo "   - Layer-based caching (if supported)"
    echo "   - Expected: 3-5 minutes if caching works"
    echo ""
    echo "3. DOCKER + Multi-Stage (Current - Not Working)"
    echo "   - Complex multi-stage build"
    echo "   - Expected: 8-9 minutes (no caching benefit)"
    echo ""
}

# Function to apply strategy
apply_strategy() {
    case $1 in
        1)
            echo "✅ Applying Strategy 1: NIXPACKS + Staged Installation"
            
            # Update railway.toml for nixpacks
            cat > railway.toml << 'EOL'
[build]
builder = "NIXPACKS"
buildCommand = """
pip install --upgrade pip &&
echo "📦 Installing core packages..." &&
pip install fastapi uvicorn pydantic sqlalchemy alembic psycopg2-binary &&
echo "📦 Installing auth & networking..." &&
pip install python-jose python-multipart bcrypt aiohttp requests httpx &&
echo "📦 Installing AI services..." &&
pip install anthropic openai python-dotenv redis &&
echo "📦 Installing data processing..." &&
pip install 'numpy<2.0.0,>=1.26.2' 'pandas>=2.0.0' 'pinecone>=3.0.0' &&
echo "📦 Installing ML packages (this will take a few minutes)..." &&
pip install --index-url https://download.pytorch.org/whl/cpu torch==2.1.0 &&
pip install torch-geometric scikit-learn sentence-transformers matplotlib scipy &&
echo "✅ All packages installed successfully!"
"""

[deploy] 
startCommand = "uvicorn main_deploy:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"

[build.env]
PIP_INDEX_URL = "https://download.pytorch.org/whl/cpu"
PIP_EXTRA_INDEX_URL = "https://pypi.org/simple/"
BUILDKIT_INLINE_CACHE = "1"

[build.cache]
enabled = true
paths = ["/usr/local/lib/python3.11/site-packages"]
EOL
            echo "✅ Railway configured for NIXPACKS optimization"
            ;;
            
        2)
            echo "✅ Applying Strategy 2: DOCKER + Single-Stage"
            
            # Update railway.toml for docker
            cat > railway.toml << 'EOL'
[build]
builder = "DOCKER"
dockerfilePath = "Dockerfile.railway-optimized"

[deploy] 
startCommand = "uvicorn main_deploy:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"

[build.env]
BUILDKIT_INLINE_CACHE = "1"
DOCKER_BUILDKIT = "1"

[build.cache]
enabled = true
EOL
            echo "✅ Railway configured for optimized Docker build"
            ;;
            
        3)
            echo "⚠️  Strategy 3: Reverting to multi-stage Docker (not recommended)"
            
            # Update railway.toml for multi-stage
            cat > railway.toml << 'EOL'
[build]
builder = "DOCKER"
dockerfilePath = "Dockerfile.ultra-optimized"

[deploy] 
startCommand = "uvicorn main_deploy:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
EOL
            echo "⚠️  Using multi-stage Docker (may be slow)"
            ;;
            
        *)
            echo "❌ Invalid option"
            exit 1
            ;;
    esac
}

# Main execution
if [ "$1" = "" ]; then
    show_options
    echo ""
    echo "Usage: ./optimize-railway.sh [strategy_number]"
    echo "Example: ./optimize-railway.sh 1"
    exit 0
fi

apply_strategy $1

echo ""
echo "🎯 Strategy Applied Successfully!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Commit changes: git add railway.toml && git commit -m 'Test optimization strategy $1'"
echo "2. Deploy: git push origin stability"
echo "3. Monitor build time in Railway dashboard"
echo "4. Expected result based on strategy $1:"

case $1 in
    1) echo "   - Build time: 4-6 minutes (first time), 2-3 minutes (cached)" ;;
    2) echo "   - Build time: 3-5 minutes (if Docker caching works)" ;;
    3) echo "   - Build time: 8-9 minutes (no optimization)" ;;
esac

echo ""
echo "💡 Recommendation: Start with Strategy 1 (NIXPACKS)"
echo "   Railway's native builder often performs better than Docker"