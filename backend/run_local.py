#!/usr/bin/env python3
"""
Local development runner that ensures correct database configuration
"""
import os
import sys

# Clear ALL potentially problematic environment variables
railway_vars = [
    'RAILWAY_ENVIRONMENT', 'RAILWAY_SERVICE_ID', 'RAILWAY_DATABASE_URL',
    'DATABASE_PUBLIC_URL', 'RAILWAY_DEPLOYMENT_ID', 'RAILWAY_REPLICA_ID',
    'RAILWAY_VOLUME_MOUNT_PATH', 'RAILWAY_VOLUME_NAME'
]

for var in railway_vars:
    if var in os.environ:
        del os.environ[var]
        print(f"🗑️  Removed {var}")

# Clear any environment variables containing 'railway'
for key in list(os.environ.keys()):
    if 'RAILWAY' in key.upper() or 'railway' in key:
        del os.environ[key]
        print(f"🗑️  Removed {key}")

# Set correct local database configuration
os.environ['DATABASE_URL'] = 'postgresql://postgres:Mac.phil.007@localhost:5432/navigo_local'
os.environ['LOCAL_DATABASE_URL'] = 'postgresql://postgres:Mac.phil.007@localhost:5432/navigo_local'
os.environ['ENV'] = 'development'

print("🚀 Starting backend with local database configuration...")
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")
print(f"LOCAL_DATABASE_URL: {os.environ.get('LOCAL_DATABASE_URL')}")
print(f"ENV: {os.environ.get('ENV')}")
print(f"RAILWAY_ENVIRONMENT: {os.environ.get('RAILWAY_ENVIRONMENT', 'NOT SET')}")

# Now import and run the app
sys.path.insert(0, '.')
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)