import requests
import json

# Test creating a new user and onboarding flow
print("Testing new user onboarding flow...")

# First, let's create a new user
register_url = 'http://localhost:8000/auth/register'
register_data = {
    'email': 'newuser@example.com',
    'password': 'test123',
    'first_name': 'New',
    'last_name': 'User'
}

try:
    print("1. Registering new user...")
    register_response = requests.post(register_url, json=register_data)
    print(f"   Register Status: {register_response.status_code}")
    
    if register_response.status_code == 201:
        print("   Registration successful!")
        
        # Login with the new user
        login_url = 'http://localhost:8000/auth/login'
        login_data = {
            'email': 'newuser@example.com',
            'password': 'test123'
        }
        
        print("2. Logging in new user...")
        login_response = requests.post(login_url, json=login_data)
        print(f"   Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token = login_response.json()['access_token']
            headers = {'Authorization': f'Bearer {token}'}
            
            print("3. Checking onboarding status...")
            status_response = requests.get('http://localhost:8000/auth/onboarding-status', headers=headers)
            print(f"   Status: {status_response.json()}")
            
            print("4. Starting onboarding...")
            start_response = requests.post('http://localhost:8000/onboarding/start', headers=headers)
            print(f"   Start Status: {start_response.status_code}")
            if start_response.status_code == 200:
                print(f"   Start Response: {start_response.json()}")
                
                print("5. Saving onboarding response...")
                response_data = {
                    'questionId': 'test_question_1',
                    'question': 'What motivates you the most?',
                    'response': 'I am motivated by solving challenging problems and helping others.',
                    'timestamp': '2024-01-01T00:00:00Z'
                }
                
                response_response = requests.post('http://localhost:8000/onboarding/response', json=response_data, headers=headers)
                print(f"   Response Status: {response_response.status_code}")
                if response_response.status_code != 200:
                    print(f"   Error: {response_response.text}")
                else:
                    print(f"   Response: {response_response.json()}")
            else:
                print(f"   Start Error: {start_response.text}")
        else:
            print(f"   Login Error: {login_response.text}")
    else:
        print(f"   Register Error: {register_response.text}")
        
except Exception as e:
    print(f"Error: {e}")