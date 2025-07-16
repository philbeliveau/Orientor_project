#!/usr/bin/env python3
"""
Test the onboarding skip functionality
"""
import requests
import json

# Test user data
import time
test_user = {
    "email": f"skip_test_{int(time.time())}@example.com",
    "password": "testpass123"
}

def test_onboarding_skip():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing onboarding skip functionality...")
    
    # 1. Register a new user
    print("1. Registering new user...")
    response = requests.post(f"{base_url}/auth/register", json=test_user)
    print(f"   Registration: {response.status_code}")
    
    if response.status_code not in [200, 201]:
        print(f"   Registration failed: {response.text}")
        return False
    
    # 2. Login to get token
    print("2. Logging in...")
    response = requests.post(f"{base_url}/auth/login", json=test_user)
    print(f"   Login: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Login failed: {response.text}")
        return False
    
    token = response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Check initial onboarding status
    print("3. Checking initial onboarding status...")
    response = requests.get(f"{base_url}/onboarding/status", headers=headers)
    print(f"   Status check: {response.status_code}")
    
    if response.status_code == 200:
        status = response.json()
        print(f"   Initial status: isComplete={status.get('isComplete')}, hasStarted={status.get('hasStarted')}")
    
    # 4. Skip onboarding
    print("4. Skipping onboarding...")
    response = requests.post(f"{base_url}/onboarding/skip", headers=headers)
    print(f"   Skip onboarding: {response.status_code}")
    
    if response.status_code == 200:
        skip_result = response.json()
        print(f"   Skip result: {skip_result}")
    else:
        print(f"   Skip failed: {response.text}")
        return False
    
    # 5. Check onboarding status after skip
    print("5. Checking onboarding status after skip...")
    response = requests.get(f"{base_url}/onboarding/status", headers=headers)
    print(f"   Status check: {response.status_code}")
    
    if response.status_code == 200:
        status = response.json()
        print(f"   Final status: isComplete={status.get('isComplete')}, hasStarted={status.get('hasStarted')}")
        
        if status.get('isComplete'):
            print("   ✅ SUCCESS: User now has completed onboarding!")
        else:
            print("   ❌ FAILED: User still needs onboarding")
            return False
    else:
        print(f"   Status check failed: {response.text}")
        return False
    
    print("\n🎉 Onboarding skip test completed successfully!")
    print(f"📧 Test user email: {test_user['email']}")
    print(f"🔑 Test user password: {test_user['password']}")
    print("This user should now be able to login and go directly to dashboard.")
    
    return True

if __name__ == "__main__":
    success = test_onboarding_skip()
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed!")