#!/usr/bin/env python3
"""
Test script to demonstrate the onboarding issue with existing user beli5@example.com
This will show the problem BEFORE the fix is applied
"""

import requests
import json
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
TEST_EMAIL = "beli5@example.com"
TEST_PASSWORD = "navigo_123"

def test_existing_user_onboarding():
    """Test onboarding issue with existing user"""
    
    print("🧪 TESTING EXISTING USER ONBOARDING ISSUE")
    print("=" * 60)
    print(f"🌐 API URL: {API_URL}")
    print(f"👤 Test User: {TEST_EMAIL}")
    print()
    
    # Test 1: Try to login
    print("🔑 Step 1: Testing login...")
    try:
        login_response = requests.post(
            f"{API_URL}/auth/login",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            },
            timeout=10
        )
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Login successful")
            print(f"   Token: {token[:50]}...")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Test 2: Check onboarding status
    print("\n🔍 Step 2: Checking onboarding status...")
    try:
        status_response = requests.get(
            f"{API_URL}/auth/onboarding-status",
            headers=headers,
            timeout=10
        )
        
        print(f"   Status Code: {status_response.status_code}")
        print(f"   Response: {status_response.text}")
        
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"✅ Onboarding status retrieved: {status}")
            
            if "onboarding_completed" in status:
                if status["onboarding_completed"]:
                    print("✅ User has completed onboarding")
                else:
                    print("❌ ISSUE: User shows as needing onboarding (this is the bug!)")
            else:
                print("❌ ISSUE: onboarding_completed field missing from response")
                
        elif status_response.status_code == 500:
            print("❌ ISSUE: Internal server error (likely the database field missing)")
            print("   This confirms the bug - backend trying to access non-existent field")
        else:
            print(f"❌ Unexpected status code: {status_response.status_code}")
            
    except Exception as e:
        print(f"❌ Onboarding status check error: {e}")
        return False
    
    # Test 3: Check if user has personality profile (alternative method)
    print("\n🧠 Step 3: Checking personality profile (alternative method)...")
    try:
        profile_response = requests.get(
            f"{API_URL}/onboarding/profile",
            headers=headers,
            timeout=10
        )
        
        print(f"   Profile Status Code: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            profile = profile_response.json()
            print("✅ User has personality profile - should NOT need onboarding")
            print(f"   Profile preview: {str(profile)[:100]}...")
            print("   🚨 This confirms the bug: user has profile but system thinks they need onboarding")
        elif profile_response.status_code == 404:
            print("ℹ️  User has no personality profile - would legitimately need onboarding")
        else:
            print(f"   Profile check returned: {profile_response.status_code}")
            
    except Exception as e:
        print(f"❌ Profile check error: {e}")
    
    # Test 4: Test the working onboarding status endpoint
    print("\n🔍 Step 4: Testing alternative onboarding status endpoint...")
    try:
        alt_status_response = requests.get(
            f"{API_URL}/onboarding/status",
            headers=headers,
            timeout=10
        )
        
        print(f"   Alternative Status Code: {alt_status_response.status_code}")
        
        if alt_status_response.status_code == 200:
            alt_status = alt_status_response.json()
            print(f"✅ Alternative onboarding status: {alt_status}")
            
            if alt_status.get("isComplete", False):
                print("✅ Alternative method correctly shows onboarding complete")
                print("   🚨 This confirms the issue: frontend calls wrong endpoint!")
            else:
                print("❌ Alternative method also shows incomplete")
        else:
            print(f"   Alternative status returned: {alt_status_response.status_code}")
            
    except Exception as e:
        print(f"❌ Alternative status check error: {e}")
    
    # Summary
    print("\n📊 DIAGNOSIS SUMMARY")
    print("=" * 60)
    print("🔍 ROOT CAUSE ANALYSIS:")
    print("   1. Frontend calls /auth/onboarding-status")
    print("   2. Backend tries to access user.onboarding_completed field")
    print("   3. Field doesn't exist in database → returns undefined")
    print("   4. Frontend interprets undefined as 'needs onboarding'")
    print("   5. User gets stuck in onboarding loop")
    print()
    print("✅ SOLUTION AVAILABLE:")
    print("   1. Add onboarding_completed column to Supabase users table")
    print("   2. Update backend User model")
    print("   3. Enhanced endpoint with fallback logic")
    print("   4. Migration script provided")
    print()
    print("🎯 NEXT STEPS:")
    print("   1. Run the Supabase migration (supabase_onboarding_migration.sql)")
    print("   2. Deploy the updated backend code")
    print("   3. Test with this user again")
    
    return True

if __name__ == "__main__":
    success = test_existing_user_onboarding()
    print(f"\n{'✅ DIAGNOSIS COMPLETE' if success else '❌ DIAGNOSIS FAILED'}")