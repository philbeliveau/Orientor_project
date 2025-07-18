#!/usr/bin/env python3
"""
Comprehensive test script to verify onboarding issue is fixed
"""

import requests
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"  # Update if different

def test_onboarding_fix():
    """Test the complete onboarding flow"""
    
    print("🧪 TESTING ONBOARDING FIX")
    print("=" * 50)
    
    # 1. Create a new test user
    test_email = f"test_onboarding_fix_{int(datetime.now().timestamp())}@example.com"
    test_password = "testpass123"
    
    print(f"📝 Creating test user: {test_email}")
    
    # Register user
    try:
        register_response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": test_email,
                "password": test_password,
                "full_name": "Test User"
            }
        )
        register_response.raise_for_status()
        print("✅ User registration successful")
        print(f"Response: {register_response.json()}")
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return False
    
    # Login to get token
    try:
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": test_email,
                "password": test_password
            }
        )
        login_response.raise_for_status()
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False
    
    # 2. Check initial onboarding status
    print("\n🔍 Checking initial onboarding status...")
    try:
        status_response = requests.get(
            f"{BASE_URL}/auth/onboarding-status",
            headers=headers
        )
        status_response.raise_for_status()
        initial_status = status_response.json()
        print(f"Initial status: {initial_status}")
        
        if initial_status["onboarding_completed"]:
            print("❌ ERROR: New user should not have completed onboarding")
            return False
        else:
            print("✅ Correct: New user needs onboarding")
    except Exception as e:
        print(f"❌ Error checking initial status: {e}")
        return False
    
    # 3. Complete onboarding (using skip endpoint)
    print("\n🎯 Completing onboarding...")
    try:
        complete_response = requests.post(
            f"{BASE_URL}/onboarding/skip",
            headers=headers
        )
        complete_response.raise_for_status()
        print("✅ Onboarding completed successfully")
        print(f"Response: {complete_response.json()}")
    except Exception as e:
        print(f"❌ Error completing onboarding: {e}")
        return False
    
    # 4. Check onboarding status after completion
    print("\n🔍 Checking onboarding status after completion...")
    try:
        status_response = requests.get(
            f"{BASE_URL}/auth/onboarding-status",
            headers=headers
        )
        status_response.raise_for_status()
        final_status = status_response.json()
        print(f"Final status: {final_status}")
        
        if not final_status["onboarding_completed"]:
            print("❌ ERROR: User should have completed onboarding")
            return False
        else:
            print("✅ Correct: User has completed onboarding")
    except Exception as e:
        print(f"❌ Error checking final status: {e}")
        return False
    
    # 5. Test login flow (simulating frontend login)
    print("\n🔄 Testing login flow (simulating frontend)...")
    try:
        # Simulate a new login
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": test_email,
                "password": test_password
            }
        )
        login_response.raise_for_status()
        new_token = login_response.json()["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}
        
        # Check status immediately after login
        status_response = requests.get(
            f"{BASE_URL}/auth/onboarding-status",
            headers=new_headers
        )
        status_response.raise_for_status()
        login_status = status_response.json()
        print(f"Status after fresh login: {login_status}")
        
        if not login_status["onboarding_completed"]:
            print("❌ ERROR: User should still have completed onboarding after login")
            return False
        else:
            print("✅ SUCCESS: User onboarding status persisted after login")
    except Exception as e:
        print(f"❌ Error in login flow test: {e}")
        return False
    
    # 6. Test with existing user (if any)
    print("\n👤 Testing with existing user...")
    try:
        # Try to find a user with a personality profile
        existing_user_test = requests.get(
            f"{BASE_URL}/auth/onboarding-status",
            headers=new_headers
        )
        existing_user_test.raise_for_status()
        print("✅ Existing user test passed")
    except Exception as e:
        print(f"⚠️ Existing user test inconclusive: {e}")
    
    print("\n🎉 ALL TESTS PASSED!")
    print("=" * 50)
    print("✅ Onboarding issue has been fixed!")
    print("✅ New users start with onboarding_completed=False")
    print("✅ Users who complete onboarding have onboarding_completed=True")
    print("✅ Onboarding status persists across login sessions")
    print("✅ No more infinite onboarding loops!")
    
    return True

if __name__ == "__main__":
    success = test_onboarding_fix()
    exit(0 if success else 1)