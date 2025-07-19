#!/usr/bin/env python3
"""
Test all the new fallback endpoints locally
"""

import requests
import subprocess
import time
import sys
import os

# Set environment
os.environ["PORT"] = "8080"
os.environ["DATABASE_URL"] = "postgresql://postgres:maywewVkqQnjHsGIuXjhpDRGoMnGcNPg@switchback.proxy.rlwy.net:58065/railway"

def test_all_endpoints():
    """Test all fallback endpoints locally"""
    
    print("🧪 TESTING ALL NEW FALLBACK ENDPOINTS")
    print("=" * 50)
    
    # Start server
    print("\n🚀 Starting local server...")
    process = subprocess.Popen(
        [sys.executable, "main_phase2_deploy.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Wait for startup
        time.sleep(5)
        base_url = "http://localhost:8080"
        
        # Login first
        print("\n1️⃣ Getting auth token...")
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
        print(f"✅ Got token: {token[:20]}...")
        
        # Test all endpoints
        endpoints = [
            ("/auth/me", "User profile"),
            ("/auth/onboarding-status", "Onboarding status"),
            ("/api/v1/avatar/me", "User avatar"),
            ("/user-progress/", "User progress"),
            ("/api/v1/courses", "Courses list"),
            ("/api/v1/career-goals/active", "Active career goals"),
            ("/space/notes", "Space notes"),
            ("/peers/compatible", "Compatible peers"),
            ("/api/tests/holland/user-results", "Holland test results"),
        ]
        
        print(f"\n2️⃣ Testing {len(endpoints)} endpoints...")
        working = 0
        failing = 0
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
                
                if response.status_code == 200:
                    print(f"   ✅ {endpoint} ({description}): {response.status_code}")
                    working += 1
                    
                    # Show sample data for first few
                    if working <= 3:
                        data = response.json()
                        if isinstance(data, dict):
                            keys = list(data.keys())[:3]
                            print(f"      📋 Keys: {keys}")
                else:
                    print(f"   ❌ {endpoint} ({description}): {response.status_code}")
                    failing += 1
                    
            except Exception as e:
                print(f"   💥 {endpoint} ({description}): Error - {e}")
                failing += 1
        
        print(f"\n📊 RESULTS:")
        print(f"   ✅ Working: {working}/{len(endpoints)}")
        print(f"   ❌ Failing: {failing}/{len(endpoints)}")
        
        if working >= 8:  # Allow 1 failure
            print(f"\n🎉 SUCCESS! Fallback endpoints are working")
            print(f"🚀 Ready to deploy to Railway")
            return True
        else:
            print(f"\n❌ Too many failures - need to debug")
            return False
        
    finally:
        # Cleanup
        print(f"\n🛑 Stopping server...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    success = test_all_endpoints()
    sys.exit(0 if success else 1)