#!/usr/bin/env python3
"""
Debug what routes are actually available on Railway
"""

import requests
import json

def debug_railway_routes():
    """Check what routes are available on Railway"""
    
    backend_url = 'https://orientor-backend-production-7c13.up.railway.app'
    
    print("🔍 DEBUGGING RAILWAY ROUTES")
    print("=" * 40)
    
    # Test health first
    print("\n1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f'{backend_url}/health', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data}")
        else:
            print(f"❌ Health failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health error: {e}")
    
    # Test docs to see available routes
    print("\n2️⃣ Testing docs endpoint...")
    try:
        response = requests.get(f'{backend_url}/docs', timeout=10)
        print(f"📋 Docs status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Docs are available - check in browser")
    except Exception as e:
        print(f"❌ Docs error: {e}")
    
    # Test openapi.json to see all routes
    print("\n3️⃣ Testing OpenAPI spec...")
    try:
        response = requests.get(f'{backend_url}/openapi.json', timeout=10)
        if response.status_code == 200:
            data = response.json()
            paths = data.get('paths', {})
            print(f"📋 Available routes ({len(paths)}):")
            
            auth_routes = []
            api_routes = []
            other_routes = []
            
            for path in sorted(paths.keys()):
                if '/auth/' in path:
                    auth_routes.append(path)
                elif '/api/' in path:
                    api_routes.append(path)
                else:
                    other_routes.append(path)
            
            print(f"\n🔐 Auth routes ({len(auth_routes)}):")
            for route in auth_routes:
                print(f"   {route}")
            
            print(f"\n📚 API routes ({len(api_routes)}):")
            for route in api_routes[:10]:  # Show first 10
                print(f"   {route}")
            if len(api_routes) > 10:
                print(f"   ... and {len(api_routes) - 10} more")
            
            print(f"\n🏠 Other routes ({len(other_routes)}):")
            for route in other_routes:
                print(f"   {route}")
                
        else:
            print(f"❌ OpenAPI failed: {response.status_code}")
    except Exception as e:
        print(f"❌ OpenAPI error: {e}")
    
    # Check if fallback endpoints are there
    print("\n4️⃣ Testing specific fallback endpoints...")
    
    # Login first
    try:
        login_response = requests.post(
            f'{backend_url}/auth/login',
            json={'email': 'beli5@example.com', 'password': 'navigo_123'},
            timeout=10
        )
        
        if login_response.status_code == 200:
            token = login_response.json()['access_token']
            headers = {'Authorization': f'Bearer {token}'}
            
            # Test a few key endpoints
            test_endpoints = ['/auth/me', '/api/v1/avatar/me', '/health']
            
            for endpoint in test_endpoints:
                try:
                    response = requests.get(f'{backend_url}{endpoint}', headers=headers, timeout=5)
                    print(f"   {endpoint}: {response.status_code}")
                except Exception as e:
                    print(f"   {endpoint}: Error - {e}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Login error: {e}")

if __name__ == "__main__":
    debug_railway_routes()