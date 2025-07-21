#!/bin/bash
# Create a pre-built base image with ML dependencies
# Run this once, then use the cached image for fast deployments

echo "🏗️ Building ML base image for fast deployments..."

# Create minimal ML requirements for profiles
cat > requirements-ml-minimal.txt << EOF
# Minimal ML for profiles router only
torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu
scikit-learn==1.3.0
sentence-transformers==2.2.2
EOF

# Build base image
docker build -f - -t orientor-ml-base:latest . << 'EOF'
FROM python:3.11-slim
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*
COPY requirements-ml-minimal.txt .
RUN pip install --no-cache-dir -r requirements-ml-minimal.txt
EOF

echo "✅ ML base image created: orientor-ml-base:latest"
echo "💡 Now use this in your main Dockerfile:"
echo "FROM orientor-ml-base:latest as base"