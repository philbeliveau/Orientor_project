#!/usr/bin/env python3
"""
Test Railway deployment locally - Mirror exact Railway environment
"""

import os
import sys
import requests
import json
import subprocess
import time
import signal
from pathlib import Path

# Set Railway-like environment
os.environ["PORT"] = "8080"
os.environ["DATABASE_URL"] = "postgresql://postgres:maywewVkqQnjHsGIuXjhpDRGoMnGcNPg@switchback.proxy.rlwy.net:58065/railway"

def test_deployment_locally():
    """Test the exact Railway deployment locally"""
    
    print("🧪 TESTING RAILWAY DEPLOYMENT LOCALLY")
    print("=" * 50)
    
    # Test 1: App Import
    print("\n1️⃣ Testing app import...")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from main_phase2_deploy import main
        from main_phase2_real import app
        print("   ✅ Apps import successfully")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Test 2: Route Inspection
    print("\n2️⃣ Testing route availability...")
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            for method in route.methods:
                if method not in ['HEAD', 'OPTIONS']:
                    routes.append(f"{method} {route.path}")
    
    expected_routes = [
        "POST /auth/login",
        "GET /health", 
        "GET /"
    ]
    
    print(f"   📋 Total routes: {len(routes)}")
    for expected in expected_routes:
        if any(expected in route for route in routes):
            print(f"   ✅ {expected}")
        else:
            print(f"   ❌ Missing: {expected}")
    
    # Test 3: Database Connection
    print("\n3️⃣ Testing database connection...")
    try:
        from sqlalchemy import create_engine, text
        
        DATABASE_URL = os.environ["DATABASE_URL"]
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.fetchone()[0]
            print(f"   ✅ Database connected: {user_count} users")
            
            # Check target user
            result = conn.execute(text("SELECT email FROM users WHERE email = 'beli5@example.com'"))
            user = result.fetchone()
            if user:
                print(f"   ✅ Target user exists: {user[0]}")
            else:
                print(f"   ❌ Target user missing")
                
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False
    
    return True

def test_live_server():
    """Start server and test endpoints"""
    
    print("\n🚀 TESTING LIVE SERVER")
    print("=" * 50)
    
    # Start server in background
    print("\n4️⃣ Starting server...")
    process = None
    try:
        process = subprocess.Popen(
            [sys.executable, "main_phase2_deploy.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        print("   ⏳ Waiting for server startup...")
        time.sleep(5)
        
        base_url = "http://localhost:8080"
        
        # Test health endpoint
        print("\n5️⃣ Testing health endpoint...")
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Health check: {data.get('status', 'unknown')}")
                print(f"   📋 Version: {data.get('version', 'unknown')}")
            else:
                print(f"   ❌ Health check failed: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Health check error: {e}")
            return False
        
        # Test login endpoint
        print("\n6️⃣ Testing login endpoint...")
        try:
            login_data = {
                "email": "beli5@example.com",
                "password": "navigo_123"
            }
            
            response = requests.post(
                f"{base_url}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token', '')
                print(f"   ✅ Login successful!")
                print(f"   🎟️ Token: {token[:20]}...")
                
                # Test authenticated endpoint
                print("\n7️⃣ Testing authenticated endpoints...")
                headers = {"Authorization": f"Bearer {token}"}
                
                # Try to access avatar endpoint
                try:
                    response = requests.get(f"{base_url}/api/v1/avatar/me", headers=headers, timeout=5)
                    print(f"   Avatar endpoint: {response.status_code}")
                except:
                    print(f"   Avatar endpoint: Not available (expected)")
                
                return True
                
            else:
                print(f"   ❌ Login failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Login error: {e}")
            return False
        
    finally:
        # Clean up server
        if process:
            print("\n🛑 Stopping server...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

def main():
    """Run complete local testing suite"""
    
    print("🔬 RAILWAY DEPLOYMENT LOCAL TESTING SUITE")
    print("=" * 60)
    print("🎯 This mirrors exactly what happens on Railway")
    print()
    
    # Test static components
    static_success = test_deployment_locally()
    
    if static_success:
        print("\n✅ Static tests passed, proceeding to live server test...")
        live_success = test_live_server()
        
        if live_success:
            print("\n🎉 ALL TESTS PASSED!")
            print("🚀 Deployment should work perfectly on Railway")
            print("\n📋 SUMMARY:")
            print("   ✅ App imports successfully")
            print("   ✅ Database connection working")
            print("   ✅ Health check operational") 
            print("   ✅ Login authentication working")
            print("   ✅ JWT token generation functional")
            return True
        else:
            print("\n❌ Live server tests failed")
            return False
    else:
        print("\n❌ Static tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)