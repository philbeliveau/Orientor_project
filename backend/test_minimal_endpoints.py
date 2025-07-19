#!/usr/bin/env python3
"""
Test minimal app endpoints
"""

import requests
import subprocess
import time
import sys
import os

# Set environment
os.environ["PORT"] = "8080"
os.environ["DATABASE_URL"] = "postgresql://postgres:maywewVkqQnjHsGIuXjhpDRGoMnGcNPg@switchback.proxy.rlwy.net:58065/railway"

def test_minimal_app():
    """Test minimal app endpoints"""
    
    print("🧪 TESTING MINIMAL APP ENDPOINTS")
    print("=" * 50)
    
    # Start server
    print("\n🚀 Starting minimal server...")
    process = subprocess.Popen(
        [sys.executable, "main_phase2_minimal_deploy.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Wait for startup
        time.sleep(5)
        base_url = "http://localhost:8080"
        
        # Test health
        print("\n1️⃣ Testing health...")
        health_response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   Health: {health_response.status_code}")
        
        # Login
        print("\n2️⃣ Testing login...")
        login_response = requests.post(
            f"{base_url}/auth/login",
            json={"email": "beli5@example.com", "password": "navigo_123"},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
        token = login_response.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        print(f"✅ Login: {login_response.status_code}")
        
        # Test all endpoints
        endpoints = [
            "/auth/me",
            "/auth/onboarding-status", 
            "/api/v1/avatar/me",
            "/user-progress/",
            "/api/v1/courses",
            "/api/v1/career-goals/active",
            "/space/notes",
            "/peers/compatible",
            "/api/tests/holland/user-results",
        ]
        
        print(f"\n3️⃣ Testing {len(endpoints)} endpoints...")
        success_count = 0
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ {endpoint}: {response.status_code}")
                    success_count += 1
                else:
                    print(f"   ❌ {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"   💥 {endpoint}: Error - {e}")
        
        print(f"\n📊 RESULTS: {success_count}/{len(endpoints)} endpoints working")
        
        return success_count == len(endpoints)
        
    finally:
        # Cleanup
        print(f"\n🛑 Stopping server...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    success = test_minimal_app()
    print(f"\n{'🎉 SUCCESS!' if success else '❌ FAILED'}")
    sys.exit(0 if success else 1)