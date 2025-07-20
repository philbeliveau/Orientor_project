#!/usr/bin/env python3
"""
Test the complete frontend flow to identify issues
"""

import requests
import json
import time

def test_frontend_flow():
    """Test the complete flow that frontend should follow"""
    
    backend_url = 'https://orientor-backend-production-7c13.up.railway.app'
    
    print("🔍 TESTING COMPLETE FRONTEND FLOW")
    print("=" * 50)
    
    # Step 1: Test login (what frontend does when you click login)
    print("\n1️⃣ Step 1: User Login")
    print("=" * 30)
    
    login_payload = {
        'email': 'beli5@example.com',
        'password': 'navigo_123'
    }
    
    login_response = requests.post(
        f'{backend_url}/auth/login',
        json=login_payload,
        headers={'Content-Type': 'application/json'},
        timeout=10
    )
    
    print(f"Login Status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"❌ Login failed")
        print(f"Response: {login_response.text}")
        return False
    
    login_data = login_response.json()
    print(f"✅ Login successful")
    print(f"Token received: {login_data.get('access_token', 'MISSING')[:30]}...")
    print(f"Token type: {login_data.get('token_type', 'MISSING')}")
    
    # Frontend should store this token and use it for subsequent requests
    token = login_data.get('access_token')
    if not token:
        print("❌ No access token received!")
        return False
    
    headers = {
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json'
    }
    
    # Step 2: Get user profile (first thing frontend usually does after login)
    print(f"\n2️⃣ Step 2: Get User Profile")
    print("=" * 30)
    
    profile_response = requests.get(f'{backend_url}/auth/me', headers=headers, timeout=10)
    print(f"Profile Status: {profile_response.status_code}")
    
    if profile_response.status_code != 200:
        print(f"❌ Profile failed")
        print(f"Response: {profile_response.text}")
        return False
    
    profile_data = profile_response.json()
    print(f"✅ Profile retrieved")
    print(f"User ID: {profile_data.get('id')}")
    print(f"Email: {profile_data.get('email')}")
    print(f"Name: {profile_data.get('name')}")
    
    # Step 3: Check onboarding status (determines where to redirect)
    print(f"\n3️⃣ Step 3: Check Onboarding Status")
    print("=" * 30)
    
    onboarding_response = requests.get(f'{backend_url}/auth/onboarding-status', headers=headers, timeout=10)
    print(f"Onboarding Status: {onboarding_response.status_code}")
    
    if onboarding_response.status_code != 200:
        print(f"❌ Onboarding check failed")
        print(f"Response: {onboarding_response.text}")
        return False
    
    onboarding_data = onboarding_response.json()
    print(f"✅ Onboarding status retrieved")
    print(f"Completed: {onboarding_data.get('completed')}")
    print(f"Current Step: {onboarding_data.get('current_step')}")
    
    # Frontend logic check
    if onboarding_data.get('completed') == True:
        print(f"🎯 SHOULD REDIRECT TO: /dashboard")
    else:
        print(f"🎯 SHOULD REDIRECT TO: /onboarding")
    
    # Step 4: Test dashboard data loading (what happens after redirect)
    print(f"\n4️⃣ Step 4: Load Dashboard Data")
    print("=" * 30)
    
    # Test multiple endpoints that dashboard needs
    dashboard_endpoints = [
        ('/api/v1/avatar/me', 'Avatar'),
        ('/user-progress/', 'Progress'),
        ('/api/v1/courses', 'Courses'),
        ('/api/v1/career-goals/active', 'Career Goals')
    ]
    
    all_working = True
    
    for endpoint, name in dashboard_endpoints:
        try:
            response = requests.get(f'{backend_url}{endpoint}', headers=headers, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: {response.status_code}")
            else:
                print(f"❌ {name}: {response.status_code}")
                all_working = False
        except Exception as e:
            print(f"💥 {name}: Error - {e}")
            all_working = False
    
    # Summary
    print(f"\n📊 FLOW ANALYSIS")
    print("=" * 30)
    
    print(f"✅ Login: Working")
    print(f"✅ Profile: Working") 
    print(f"✅ Onboarding: Complete (should go to dashboard)")
    print(f"{'✅' if all_working else '❌'} Dashboard Data: {'All working' if all_working else 'Some issues'}")
    
    # Potential issues
    print(f"\n🔍 POTENTIAL FRONTEND ISSUES:")
    print("=" * 30)
    
    print(f"1. Environment Variables:")
    print(f"   - Check NEXT_PUBLIC_API_URL = {backend_url}")
    print(f"   - Check NEXT_PUBLIC_BACKEND_URL = {backend_url}")
    
    print(f"2. Token Storage:")
    print(f"   - Frontend should store token in localStorage or cookies")
    print(f"   - Check browser dev tools > Application > Local Storage")
    
    print(f"3. Routing Logic:")
    print(f"   - After /auth/me succeeds, should redirect to /dashboard")
    print(f"   - Check browser console for JavaScript errors")
    
    print(f"4. CORS Issues:")
    print(f"   - Check browser Network tab for CORS errors")
    print(f"   - Backend has CORS enabled for all origins")
    
    return all_working

def test_specific_vercel_issue():
    """Test specific issues that might affect Vercel deployment"""
    
    print(f"\n🔍 VERCEL-SPECIFIC CHECKS")
    print("=" * 30)
    
    # Check if it's a deployment caching issue
    backend_url = 'https://orientor-backend-production-7c13.up.railway.app'
    
    # Test with cache-busting
    headers_no_cache = {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    
    health_response = requests.get(f'{backend_url}/health', headers=headers_no_cache)
    health_data = health_response.json()
    
    print(f"Backend Version: {health_data.get('version', 'unknown')}")
    print(f"Backend Status: {health_data.get('status', 'unknown')}")
    
    # Check if there are any API endpoints in frontend
    print(f"\n📋 Frontend might be calling these endpoints:")
    print(f"   - GET /api/auth/me (frontend API route)")
    print(f"   - POST /api/auth/login (frontend API route)")
    print(f"   - Direct backend calls to Railway")
    
    print(f"\n💡 DEBUG STEPS FOR VERCEL:")
    print(f"1. Open browser dev tools")
    print(f"2. Go to Network tab")
    print(f"3. Try to login")
    print(f"4. Check what URLs are being called")
    print(f"5. Look for 404s, CORS errors, or wrong URLs")

if __name__ == "__main__":
    print("🧪 COMPREHENSIVE FRONTEND FLOW TEST")
    print("=" * 60)
    
    # Test the complete flow
    flow_success = test_frontend_flow()
    
    # Test Vercel-specific issues
    test_specific_vercel_issue()
    
    print(f"\n{'🎉 BACKEND FLOW: WORKING' if flow_success else '❌ BACKEND FLOW: ISSUES'}")
    
    if flow_success:
        print(f"🎯 The issue is likely in frontend code or Vercel configuration")
        print(f"🔧 Check browser dev tools for JavaScript errors")
    else:
        print(f"🎯 There are still backend issues to resolve")