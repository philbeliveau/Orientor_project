#!/usr/bin/env python3
"""
Test script to verify onboarding fix works with Supabase
"""

import requests
import json
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API URL from environment or use default
API_URL = os.getenv("API_URL", "https://your-backend-url.railway.app")  # Update with your actual URL
if API_URL == "https://your-backend-url.railway.app":
    print("⚠️  Please set API_URL environment variable or update the URL in this script")
    print("   Example: export API_URL=https://your-backend-url.railway.app")
    exit(1)

def test_supabase_onboarding():
    """Test onboarding with Supabase database"""
    
    print("🧪 TESTING SUPABASE ONBOARDING FIX")
    print("=" * 60)
    print(f"🌐 API URL: {API_URL}")
    
    # Test connection first
    try:
        health_response = requests.get(f"{API_URL}/health", timeout=10)
        print(f"✅ API Health Check: {health_response.status_code}")
    except Exception as e:
        print(f"❌ API Connection failed: {e}")
        print("   Make sure your backend is running and accessible")
        return False
    
    # 1. Test with existing user (if any)
    print("\n👤 Testing existing user...")
    
    # You can add credentials of an existing user here for testing
    existing_email = "test@example.com"  # Update with real test user
    existing_password = "testpass123"
    
    try:
        login_response = requests.post(
            f"{API_URL}/auth/login",
            json={"email": existing_email, "password": existing_password},
            timeout=10
        )
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Check onboarding status
            status_response = requests.get(
                f"{API_URL}/auth/onboarding-status",
                headers=headers,
                timeout=10
            )
            
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"✅ Existing user onboarding status: {status}")
                
                if "onboarding_completed" in status:
                    print("✅ onboarding_completed field is present")
                    if status["onboarding_completed"]:
                        print("✅ User has completed onboarding")
                    else:
                        print("ℹ️  User needs to complete onboarding")
                else:
                    print("❌ onboarding_completed field missing from response")
            else:
                print(f"❌ Status check failed: {status_response.status_code}")
                print(f"   Response: {status_response.text}")
        else:
            print(f"ℹ️  Existing user login failed (expected if no test user): {login_response.status_code}")
            
    except Exception as e:
        print(f"ℹ️  Existing user test inconclusive: {e}")
    
    # 2. Create new user and test complete flow
    print("\n📝 Testing new user registration and onboarding...")
    
    test_email = f"test_supabase_{int(datetime.now().timestamp())}@example.com"
    test_password = "testpass123"
    
    try:
        # Register new user
        register_response = requests.post(
            f"{API_URL}/auth/register",
            json={
                "email": test_email,
                "password": test_password,
                "full_name": "Test User Supabase"
            },
            timeout=10
        )
        
        if register_response.status_code == 201:
            print("✅ New user registration successful")
            
            # Login with new user
            login_response = requests.post(
                f"{API_URL}/auth/login",
                json={"email": test_email, "password": test_password},
                timeout=10
            )
            
            if login_response.status_code == 200:
                token = login_response.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
                print("✅ New user login successful")
                
                # Check initial onboarding status
                status_response = requests.get(
                    f"{API_URL}/auth/onboarding-status",
                    headers=headers,
                    timeout=10
                )
                
                if status_response.status_code == 200:
                    initial_status = status_response.json()
                    print(f"✅ Initial onboarding status: {initial_status}")
                    
                    if not initial_status.get("onboarding_completed", True):
                        print("✅ Correct: New user needs onboarding")
                        
                        # Complete onboarding using skip
                        skip_response = requests.post(
                            f"{API_URL}/onboarding/skip",
                            headers=headers,
                            timeout=10
                        )
                        
                        if skip_response.status_code == 200:
                            print("✅ Onboarding skip successful")
                            
                            # Check final status
                            final_status_response = requests.get(
                                f"{API_URL}/auth/onboarding-status",
                                headers=headers,
                                timeout=10
                            )
                            
                            if final_status_response.status_code == 200:
                                final_status = final_status_response.json()
                                print(f"✅ Final onboarding status: {final_status}")
                                
                                if final_status.get("onboarding_completed", False):
                                    print("✅ SUCCESS: User onboarding completed and persisted!")
                                    return True
                                else:
                                    print("❌ ERROR: Onboarding not marked as completed")
                                    return False
                            else:
                                print(f"❌ Final status check failed: {final_status_response.status_code}")
                                return False
                        else:
                            print(f"❌ Onboarding skip failed: {skip_response.status_code}")
                            print(f"   Response: {skip_response.text}")
                            return False
                    else:
                        print("❌ ERROR: New user should need onboarding")
                        return False
                else:
                    print(f"❌ Initial status check failed: {status_response.status_code}")
                    print(f"   Response: {status_response.text}")
                    return False
            else:
                print(f"❌ New user login failed: {login_response.status_code}")
                return False
        else:
            print(f"❌ Registration failed: {register_response.status_code}")
            print(f"   Response: {register_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ New user test failed: {e}")
        return False
    
    print("\n🎉 SUPABASE ONBOARDING TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_supabase_onboarding()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")
    exit(0 if success else 1)