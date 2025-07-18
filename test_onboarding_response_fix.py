import requests
import json

# Test the onboarding response fix with existing user
print("Testing onboarding response fix...")

# First reset the existing user's onboarding to test fresh flow
login_url = 'http://localhost:8000/auth/login'
login_data = {
    'email': 'beli5@example.com',
    'password': 'navigo_123'
}

try:
    print("1. Logging in existing user...")
    login_response = requests.post(login_url, json=login_data)
    print(f"   Login Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        print("2. Resetting onboarding to test fresh flow...")
        reset_response = requests.delete('http://localhost:8000/onboarding/reset', headers=headers)
        print(f"   Reset Status: {reset_response.status_code}")
        
        if reset_response.status_code == 200:
            print("3. Checking onboarding status after reset...")
            status_response = requests.get('http://localhost:8000/auth/onboarding-status', headers=headers)
            print(f"   Status: {status_response.json()}")
            
            print("4. Directly saving response without starting session...")
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
                
                print("5. Saving another response...")
                response_data2 = {
                    'questionId': 'test_question_2',
                    'question': 'What are your biggest strengths?',
                    'response': 'My biggest strengths are critical thinking and communication.',
                    'timestamp': '2024-01-01T00:00:00Z'
                }
                
                response_response2 = requests.post('http://localhost:8000/onboarding/response', json=response_data2, headers=headers)
                print(f"   Response2 Status: {response_response2.status_code}")
                if response_response2.status_code != 200:
                    print(f"   Error: {response_response2.text}")
                else:
                    print(f"   Response: {response_response2.json()}")
        else:
            print(f"   Reset Error: {reset_response.text}")
    else:
        print(f"   Login Error: {login_response.text}")
        
except Exception as e:
    print(f"Error: {e}")