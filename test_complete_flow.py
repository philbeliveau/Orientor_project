#!/usr/bin/env python3
"""
Complete test of the onboarding fix
"""
import requests
import json
import time
import sys

def test_complete_flow():
    base_url = "http://localhost:8000"
    
    print("🧪 COMPLETE ONBOARDING FIX TEST")
    print("="*50)
    
    # Test 1: Create a user without onboarding
    print("\n1. Testing user creation and onboarding bypass...")
    
    # Create a unique user
    timestamp = int(time.time())
    test_user = {
        "email": f"test_complete_{timestamp}@example.com",
        "password": "testpass123"
    }
    
    # Register user
    print("   - Registering new user...")
    response = requests.post(f"{base_url}/auth/register", json=test_user)
    if response.status_code not in [200, 201]:
        print(f"   ❌ Registration failed: {response.text}")
        return False
    print(f"   ✅ Registration successful")
    
    # Login
    print("   - Logging in...")
    response = requests.post(f"{base_url}/auth/login", json=test_user)
    if response.status_code != 200:
        print(f"   ❌ Login failed: {response.text}")
        return False
    
    token = response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    print(f"   ✅ Login successful")
    
    # Check initial onboarding status
    print("   - Checking initial onboarding status...")
    response = requests.get(f"{base_url}/onboarding/status", headers=headers)
    if response.status_code != 200:
        print(f"   ❌ Status check failed: {response.text}")
        return False
    
    status = response.json()
    print(f"   Initial status: isComplete={status.get('isComplete')}, hasStarted={status.get('hasStarted')}")
    
    if status.get('isComplete'):
        print("   ❌ User should need onboarding initially")
        return False
    
    # Skip onboarding
    print("   - Skipping onboarding...")
    response = requests.post(f"{base_url}/onboarding/skip", headers=headers)
    if response.status_code != 200:
        print(f"   ❌ Skip failed: {response.text}")
        return False
    
    skip_result = response.json()
    print(f"   ✅ Skip successful: {skip_result.get('message')}")
    
    # Check final onboarding status
    print("   - Checking final onboarding status...")
    response = requests.get(f"{base_url}/onboarding/status", headers=headers)
    if response.status_code != 200:
        print(f"   ❌ Status check failed: {response.text}")
        return False
    
    status = response.json()
    print(f"   Final status: isComplete={status.get('isComplete')}, hasStarted={status.get('hasStarted')}")
    
    if not status.get('isComplete'):
        print("   ❌ User should have completed onboarding after skip")
        return False
    
    print("   ✅ User now has completed onboarding!")
    
    # Test 2: Login flow simulation
    print("\n2. Testing login flow (simulating frontend behavior)...")
    
    # Login again (simulating fresh login)
    print("   - Fresh login...")
    response = requests.post(f"{base_url}/auth/login", json=test_user)
    if response.status_code != 200:
        print(f"   ❌ Login failed: {response.text}")
        return False
    
    token = response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check onboarding status (this is what frontend does)
    print("   - Frontend checking onboarding status...")
    response = requests.get(f"{base_url}/onboarding/status", headers=headers)
    if response.status_code != 200:
        print(f"   ❌ Status check failed: {response.text}")
        return False
    
    status = response.json()
    needs_onboarding = not status.get('isComplete')
    
    if needs_onboarding:
        print("   ❌ Frontend would redirect to onboarding (BAD)")
        return False
    else:
        print("   ✅ Frontend would redirect to dashboard (GOOD)")
    
    # Test 3: Profile access
    print("\n3. Testing profile access...")
    
    response = requests.get(f"{base_url}/onboarding/profile", headers=headers)
    if response.status_code != 200:
        print(f"   ❌ Profile access failed: {response.text}")
        return False
    
    profile = response.json()
    print(f"   ✅ Profile accessible with scores: {bool(profile.get('profile'))}")
    
    # Test 4: Summary
    print("\n4. SUMMARY")
    print("   ✅ User registration works")
    print("   ✅ Initial onboarding status correctly shows incomplete")
    print("   ✅ Onboarding skip functionality works")
    print("   ✅ Final onboarding status correctly shows complete")
    print("   ✅ Login flow redirects to dashboard (not onboarding)")
    print("   ✅ User can access their personality profile")
    
    print(f"\n🎉 ALL TESTS PASSED!")
    print(f"📧 Test user: {test_user['email']}")
    print(f"🔑 Password: {test_user['password']}")
    print(f"👤 This user can now login and go directly to dashboard")
    
    return True

if __name__ == "__main__":
    success = test_complete_flow()
    if success:
        print("\n✅ Complete flow test PASSED!")
        print("\nThe onboarding issues have been resolved:")
        print("1. ✅ Users can skip onboarding and get a default profile")
        print("2. ✅ Users with completed onboarding go directly to dashboard")
        print("3. ✅ No more forced onboarding for all users")
        print("4. ✅ Backend /onboarding/skip endpoint works")
        print("5. ✅ Frontend onboarding detection works correctly")
    else:
        print("\n❌ Complete flow test FAILED!")
    
    sys.exit(0 if success else 1)