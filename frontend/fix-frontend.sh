#!/bin/bash
echo "Fixing frontend environment..."

# Remove old build artifacts
rm -rf .next
rm -rf node_modules
rm -f package-lock.json

# Install dependencies
npm install

# Build the project
npm run build

# Start the development server
npm run dev 