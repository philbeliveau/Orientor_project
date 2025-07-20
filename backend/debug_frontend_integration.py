#!/usr/bin/env python3
"""
Debug frontend integration - Check response formats
"""

import requests
import json

def debug_frontend_integration():
    """Check if our responses match what frontend expects"""
    
    backend_url = 'https://orientor-backend-production-7c13.up.railway.app'
    
    print("🔍 DEBUGGING FRONTEND INTEGRATION")
    print("=" * 50)
    
    # Login and get token
    print("\n1️⃣ Testing login response format...")
    login_response = requests.post(
        f'{backend_url}/auth/login',
        json={'email': 'beli5@example.com', 'password': 'navigo_123'},
        timeout=10
    )
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        print(f"✅ Login successful")
        print(f"📋 Login response format:")
        print(json.dumps(login_data, indent=2))
        
        token = login_data.get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    # Check auth/me response
    print(f"\n2️⃣ Testing /auth/me response format...")
    me_response = requests.get(f'{backend_url}/auth/me', headers=headers)
    
    if me_response.status_code == 200:
        me_data = me_response.json()
        print(f"✅ Profile endpoint working")
        print(f"📋 Profile response format:")
        print(json.dumps(me_data, indent=2))
    else:
        print(f"❌ Profile failed: {me_response.status_code}")
    
    # Check onboarding status
    print(f"\n3️⃣ Testing onboarding status...")
    onboarding_response = requests.get(f'{backend_url}/auth/onboarding-status', headers=headers)
    
    if onboarding_response.status_code == 200:
        onboarding_data = onboarding_response.json()
        print(f"✅ Onboarding endpoint working")
        print(f"📋 Onboarding response format:")
        print(json.dumps(onboarding_data, indent=2))
    else:
        print(f"❌ Onboarding failed: {onboarding_response.status_code}")
    
    # Common frontend issues to check
    print(f"\n🔍 POTENTIAL FRONTEND ISSUES:")
    
    # Check token format
    if 'access_token' in login_data and 'token_type' in login_data:
        print(f"✅ Token format correct: access_token + token_type")
    else:
        print(f"❌ Token format issue - missing access_token or token_type")
    
    # Check user ID
    if 'id' in me_data:
        print(f"✅ User ID present: {me_data['id']}")
    else:
        print(f"❌ User ID missing - frontend might need this for routing")
    
    # Check onboarding completion
    if onboarding_data.get('completed') == True:
        print(f"✅ Onboarding marked complete - should allow dashboard access")
    else:
        print(f"❌ Onboarding not complete - might redirect to onboarding flow")
    
    # Check for specific fields frontend might expect
    critical_fields = {
        'login': ['access_token', 'token_type'],
        'profile': ['id', 'email', 'name'],
        'onboarding': ['completed', 'current_step']
    }
    
    responses = {
        'login': login_data,
        'profile': me_data,
        'onboarding': onboarding_data
    }
    
    print(f"\n📋 FIELD VERIFICATION:")
    for endpoint, fields in critical_fields.items():
        data = responses[endpoint]
        for field in fields:
            if field in data:
                print(f"   ✅ {endpoint}.{field}: {data[field]}")
            else:
                print(f"   ❌ {endpoint}.{field}: MISSING")
    
    print(f"\n💡 NEXT STEPS:")
    print(f"1. Check Vercel environment variables point to: {backend_url}")
    print(f"2. Verify frontend token storage (localStorage/cookies)")
    print(f"3. Check frontend routing logic after successful /auth/me call")
    print(f"4. Look for JavaScript console errors in browser")
    print(f"5. Ensure Vercel deployment is latest version")

if __name__ == "__main__":
    debug_frontend_integration()