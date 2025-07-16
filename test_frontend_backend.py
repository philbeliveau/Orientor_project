#!/usr/bin/env python3
"""
Test script to verify frontend-backend connectivity
"""
import requests
import json
import time

# Test registration
def test_registration():
    print("🧪 Testing Registration...")
    
    url = "http://localhost:8000/auth/register"
    data = {
        "email": "test_frontend@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Registration Status: {response.status_code}")
        print(f"Registration Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            return True
        else:
            print("❌ Registration failed")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

# Test login
def test_login():
    print("\n🧪 Testing Login...")
    
    url = "http://localhost:8000/auth/login"
    data = {
        "email": "test_frontend@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Login Status: {response.status_code}")
        print(f"Login Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return response.json().get('access_token')
        else:
            print("❌ Login failed")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

# Test authenticated endpoint
def test_authenticated_endpoint(token):
    print("\n🧪 Testing Authenticated Endpoint...")
    
    url = "http://localhost:8000/profiles/me"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Profiles Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Authenticated endpoint accessible!")
            return True
        else:
            print("❌ Authenticated endpoint failed")
            return False
    except Exception as e:
        print(f"❌ Authenticated endpoint error: {e}")
        return False

def main():
    print("🚀 Testing Frontend-Backend Integration\n")
    
    # Test registration
    registration_success = test_registration()
    
    if registration_success:
        # Test login
        token = test_login()
        
        if token:
            # Test authenticated endpoint
            test_authenticated_endpoint(token)
        
    print("\n🎉 Tests completed!")

if __name__ == "__main__":
    main()