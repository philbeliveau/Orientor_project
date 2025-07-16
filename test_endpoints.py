#!/usr/bin/env python3
"""
Test all fixed endpoints
"""
import requests
import json

# Test data
test_user = {
    "email": "test_endpoints@example.com",
    "password": "testpass123"
}

def test_endpoints():
    # Register user
    print("🧪 Testing registration...")
    response = requests.post("http://localhost:8000/auth/register", json=test_user)
    print(f"Registration: {response.status_code}")
    
    # Login user
    print("🧪 Testing login...")
    response = requests.post("http://localhost:8000/auth/login", json=test_user)
    print(f"Login: {response.status_code}")
    
    if response.status_code == 200:
        token = response.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test onboarding endpoints
        print("🧪 Testing onboarding endpoints...")
        
        # Start onboarding
        response = requests.post("http://localhost:8000/onboarding/start", headers=headers)
        print(f"Start onboarding: {response.status_code}")
        
        # Get onboarding status
        response = requests.get("http://localhost:8000/onboarding/status", headers=headers)
        print(f"Onboarding status: {response.status_code}")
        
        # Save onboarding response
        onboarding_data = {
            "questionId": "q1",
            "question": "Test question",
            "response": "Test response"
        }
        response = requests.post("http://localhost:8000/onboarding/response", json=onboarding_data, headers=headers)
        print(f"Save onboarding response: {response.status_code}")
        
        # Test job recommendations
        print("🧪 Testing job recommendations...")
        response = requests.get("http://localhost:8000/api/v1/jobs/recommendations/me?top_k=5", headers=headers)
        print(f"Job recommendations: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  - Received {len(data.get('recommendations', []))} recommendations")
            
        print("🎉 All tests completed!")

if __name__ == "__main__":
    test_endpoints()