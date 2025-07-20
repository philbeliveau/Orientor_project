#!/usr/bin/env python3
"""
Test minimal app exactly as Railway would deploy it
"""

import os
import sys
import requests
import subprocess
import time

# Set exact Railway environment
os.environ["PORT"] = "8080"
os.environ["DATABASE_URL"] = "postgresql://postgres:maywewVkqQnjHsGIuXjhpDRGoMnGcNPg@switchback.proxy.rlwy.net:58065/railway"

def test_railway_minimal():
    """Test minimal app with Railway environment"""
    
    print("🚁 TESTING RAILWAY MINIMAL DEPLOYMENT")
    print("=" * 50)
    
    # Test 1: Import Check
    print("\n1️⃣ Testing imports...")
    try:
        from main_phase2_minimal_deploy import main
        from main_phase2_minimal import app
        print("   ✅ Imports successful")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Test 2: Route Count
    print("\n2️⃣ Checking routes...")
    route_count = 0
    endpoint_list = []
    
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            for method in route.methods:
                if method not in ['HEAD', 'OPTIONS']:
                    route_str = f"{method} {route.path}"
                    endpoint_list.append(route_str)
                    route_count += 1
    
    print(f"   📋 Total routes: {route_count}")
    
    # Check for critical endpoints
    critical_endpoints = [
        "POST /auth/login",
        "GET /auth/me", 
        "GET /auth/onboarding-status",
        "GET /api/v1/avatar/me",
        "GET /user-progress/",
        "GET /api/v1/courses",
        "GET /api/v1/career-goals/active",
        "GET /space/notes",
        "GET /peers/compatible",
        "GET /api/tests/holland/user-results",
        "GET /health"
    ]
    
    missing = []
    for endpoint in critical_endpoints:
        if not any(endpoint in route for route in endpoint_list):
            missing.append(endpoint)
    
    if missing:
        print(f"   ❌ Missing endpoints: {missing}")
        return False
    else:
        print(f"   ✅ All critical endpoints present")
    
    # Test 3: Live Server
    print("\n3️⃣ Testing live server...")
    process = subprocess.Popen(
        [sys.executable, "main_phase2_minimal_deploy.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        time.sleep(5)
        base_url = "http://localhost:8080"
        
        # Health check
        health_response = requests.get(f"{base_url}/health", timeout=5)
        health_data = health_response.json()
        
        print(f"   Health: {health_response.status_code}")
        print(f"   Version: {health_data.get('version', 'unknown')}")
        
        if health_data.get('version') != '2.1.0-minimal':
            print(f"   ❌ Wrong version: expected 2.1.0-minimal")
            return False
        
        # Login test
        login_response = requests.post(
            f"{base_url}/auth/login",
            json={"email": "beli5@example.com", "password": "navigo_123"},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed: {login_response.status_code}")
            return False
        
        token = login_response.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test critical endpoints
        test_endpoints = [
            "/auth/me",
            "/api/v1/avatar/me", 
            "/auth/onboarding-status"
        ]
        
        working = 0
        for endpoint in test_endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
                if response.status_code == 200:
                    working += 1
                    print(f"   ✅ {endpoint}: {response.status_code}")
                else:
                    print(f"   ❌ {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"   💥 {endpoint}: {e}")
        
        print(f"   📊 Working endpoints: {working}/{len(test_endpoints)}")
        return working == len(test_endpoints)
        
    finally:
        print(f"\n🛑 Stopping server...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    success = test_railway_minimal()
    
    print(f"\n{'🎉 RAILWAY MINIMAL TEST PASSED!' if success else '❌ RAILWAY MINIMAL TEST FAILED'}")
    
    if success:
        print("✅ Ready for Railway deployment!")
        print("🚀 This should resolve the dashboard access issue")
    
    sys.exit(0 if success else 1)