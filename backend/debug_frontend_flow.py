#!/usr/bin/env python3
"""
Debug frontend login flow - Test what happens after login
"""

import requests
import json

def test_post_login_flow():
    """Test the complete login flow and post-login endpoints"""
    
    backend_url = 'https://orientor-backend-production-7c13.up.railway.app'
    
    print("🔍 DEBUGGING FRONTEND LOGIN FLOW")
    print("=" * 50)
    
    # Step 1: Login
    print("1️⃣ Testing login...")
    login_data = {
        'email': 'beli5@example.com',
        'password': 'navigo_123'
    }
    
    try:
        response = requests.post(
            f'{backend_url}/auth/login',
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return
            
        token_data = response.json()
        token = token_data['access_token']
        print(f"✅ Login successful, token: {token[:20]}...")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 2: Test endpoints frontend likely calls after login
    headers = {'Authorization': f'Bearer {token}'}
    
    endpoints_to_test = [
        ('/auth/me', 'User profile'),
        ('/auth/onboarding-status', 'Onboarding status'),
        ('/api/v1/avatar/me', 'User avatar'),
        ('/user-progress/', 'User progress'),
        ('/api/v1/courses', 'Courses list'),
        ('/api/v1/career-goals/active', 'Active career goals'),
        ('/space/notes', 'Space notes'),
        ('/peers/compatible', 'Compatible peers'),
        ('/api/tests/holland/user-results', 'Holland test results'),
    ]
    
    print(f"\n2️⃣ Testing post-login endpoints...")
    
    working_endpoints = []
    failing_endpoints = []
    
    for endpoint, description in endpoints_to_test:
        try:
            response = requests.get(
                f'{backend_url}{endpoint}',
                headers=headers,
                timeout=5
            )
            
            status = response.status_code
            if status == 200:
                print(f"   ✅ {endpoint} ({description}): {status}")
                working_endpoints.append(endpoint)
            elif status == 401:
                print(f"   🔑 {endpoint} ({description}): {status} - Auth issue")
                failing_endpoints.append((endpoint, 'auth'))
            elif status == 404:
                print(f"   ❌ {endpoint} ({description}): {status} - Not found")
                failing_endpoints.append((endpoint, 'missing'))
            else:
                print(f"   ⚠️ {endpoint} ({description}): {status}")
                failing_endpoints.append((endpoint, 'other'))
                
        except Exception as e:
            print(f"   💥 {endpoint} ({description}): Error - {e}")
            failing_endpoints.append((endpoint, 'error'))
    
    # Summary
    print(f"\n📊 ENDPOINT ANALYSIS:")
    print(f"   ✅ Working: {len(working_endpoints)}")
    print(f"   ❌ Failing: {len(failing_endpoints)}")
    
    if failing_endpoints:
        print(f"\n🔧 MISSING ENDPOINTS (likely causing dashboard issues):")
        for endpoint, reason in failing_endpoints:
            print(f"   - {endpoint} ({reason})")
    
    print(f"\n💡 DIAGNOSIS:")
    if len(working_endpoints) == 0:
        print("   🚨 NO endpoints working - frontend can't load any data")
        print("   🎯 Need to add basic profile/auth endpoints")
    elif len(working_endpoints) < 3:
        print("   ⚠️ Very few endpoints working - limited dashboard functionality")
        print("   🎯 Need to add core dashboard endpoints")
    else:
        print("   ✅ Some endpoints working - may be specific missing data")
        print("   🎯 May need specific endpoint implementations")

if __name__ == "__main__":
    test_post_login_flow()