#!/usr/bin/env python3
"""
Simple test to check if the backend onboarding endpoint is working
"""

import requests
import json

def test_backend_endpoints():
    """Test the backend onboarding endpoints"""
    
    base_url = "http://localhost:8000"
    
    print("🔧 Testing Backend Onboarding Endpoints")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Server health check: {health_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Server not responding: {e}")
        print("Make sure the backend server is running on port 8001")
        return
    
    # Test 2: Try to access onboarding status without authentication (should fail)
    try:
        status_response = requests.get(f"{base_url}/onboarding/status", timeout=5)
        print(f"📋 Onboarding status (no auth): {status_response.status_code}")
        if status_response.status_code == 401:
            print("   ✅ Correctly returns 401 Unauthorized (expected)")
        else:
            print(f"   ❓ Unexpected response: {status_response.text[:100]}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing onboarding status: {e}")
    
    # Test 3: Check available endpoints
    try:
        docs_response = requests.get(f"{base_url}/docs", timeout=5)
        if docs_response.status_code == 200:
            print("✅ API docs available at /docs")
        
        # Try openapi.json
        openapi_response = requests.get(f"{base_url}/openapi.json", timeout=5)
        if openapi_response.status_code == 200:
            openapi_data = openapi_response.json()
            
            # Check if onboarding endpoints are defined
            paths = openapi_data.get("paths", {})
            onboarding_paths = [path for path in paths.keys() if "onboarding" in path]
            
            print(f"📋 Onboarding endpoints found: {len(onboarding_paths)}")
            for path in onboarding_paths:
                print(f"   - {path}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not check API documentation: {e}")
    
    print("\n🔍 Testing Login Flow")
    print("-" * 30)
    
    # Test 4: Try login (this will likely fail without valid credentials)
    login_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    
    try:
        login_response = requests.post(
            f"{base_url}/auth/login",
            json=login_data,
            timeout=5
        )
        print(f"🔐 Login attempt: {login_response.status_code}")
        
        if login_response.status_code == 200:
            response_data = login_response.json()
            token = response_data.get("access_token")
            print("   ✅ Login successful!")
            
            # Test onboarding status with valid token
            headers = {"Authorization": f"Bearer {token}"}
            status_response = requests.get(
                f"{base_url}/onboarding/status",
                headers=headers,
                timeout=5
            )
            
            print(f"📋 Onboarding status (with auth): {status_response.status_code}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"   Status data: {json.dumps(status_data, indent=2)}")
            else:
                print(f"   Error: {status_response.text}")
                
        elif login_response.status_code == 400:
            print("   ❌ Invalid credentials (expected for test user)")
        else:
            print(f"   ❓ Unexpected login response: {login_response.text[:100]}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Login request failed: {e}")

if __name__ == "__main__":
    test_backend_endpoints()