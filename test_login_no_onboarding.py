#!/usr/bin/env python3
"""
Test login flow for users who have completed onboarding
"""
import requests
import json
import time

def test_login_flow():
    base_url = "http://localhost:8000"
    
    # Use the user we created in the previous test
    test_user = {
        "email": "skip_test_1752697727@example.com",
        "password": "testpass123"
    }
    
    print("🧪 Testing login flow for user with completed onboarding...")
    
    # 1. Login to get token
    print("1. Logging in...")
    response = requests.post(f"{base_url}/auth/login", json=test_user)
    print(f"   Login: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Login failed: {response.text}")
        return False
    
    token = response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Check onboarding status
    print("2. Checking onboarding status...")
    response = requests.get(f"{base_url}/onboarding/status", headers=headers)
    print(f"   Status check: {response.status_code}")
    
    if response.status_code == 200:
        status = response.json()
        print(f"   Status: isComplete={status.get('isComplete')}, hasStarted={status.get('hasStarted')}")
        
        if status.get('isComplete'):
            print("   ✅ SUCCESS: User has completed onboarding!")
            print("   Frontend should redirect to dashboard instead of onboarding")
        else:
            print("   ❌ FAILED: User still needs onboarding")
            return False
    else:
        print(f"   Status check failed: {response.text}")
        return False
    
    # 3. Test that we can access the profile endpoint
    print("3. Testing profile access...")
    response = requests.get(f"{base_url}/onboarding/profile", headers=headers)
    print(f"   Profile access: {response.status_code}")
    
    if response.status_code == 200:
        profile = response.json()
        print(f"   Profile has scores: {bool(profile.get('profile'))}")
        print(f"   Profile description: {profile.get('description')[:50]}...")
        print("   ✅ SUCCESS: User can access their profile!")
    else:
        print(f"   Profile access failed: {response.text}")
        return False
    
    print("\n🎉 Login flow test completed successfully!")
    print("The user can now:")
    print("- Login successfully")
    print("- Skip onboarding detection (isComplete=True)")
    print("- Access their personality profile")
    print("- Should be redirected to dashboard by frontend")
    
    return True

if __name__ == "__main__":
    success = test_login_flow()
    if success:
        print("\n✅ All login flow tests passed!")
    else:
        print("\n❌ Login flow tests failed!")