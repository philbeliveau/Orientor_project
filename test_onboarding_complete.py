import requests
import json

# Test the onboarding completion endpoint
url = 'http://localhost:8000/auth/login'
data = {
    'email': 'beli5@example.com',
    'password': 'navigo_123'
}

print('Testing complete onboarding flow...')
try:
    # Login first
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        token = response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        print('1. Checking initial onboarding status...')
        status_response = requests.get('http://localhost:8000/auth/onboarding-status', headers=headers)
        print(f'   Initial status: {status_response.json()}')
        
        # Test completing onboarding
        print('2. Completing onboarding...')
        complete_data = {
            'responses': [
                {
                    'questionId': 'test1',
                    'question': 'Test question 1',
                    'response': 'Test response 1',
                    'timestamp': '2024-01-01T00:00:00Z'
                }
            ],
            'psychProfile': {
                'hexaco': {
                    'extraversion': 75.0,
                    'openness': 80.0,
                    'conscientiousness': 70.0,
                    'emotionality': 60.0,
                    'agreeableness': 85.0,
                    'honesty': 90.0
                },
                'riasec': {
                    'realistic': 50.0,
                    'investigative': 80.0,
                    'artistic': 70.0,
                    'social': 85.0,
                    'enterprising': 65.0,
                    'conventional': 45.0
                },
                'topTraits': ['Creative', 'Analytical', 'Collaborative'],
                'description': 'Test profile description'
            }
        }
        
        complete_response = requests.post('http://localhost:8000/onboarding/complete', json=complete_data, headers=headers)
        print(f'   Complete status: {complete_response.status_code}')
        if complete_response.status_code != 200:
            print(f'   Error: {complete_response.text}')
        else:
            print(f'   Response: {complete_response.json()}')
        
        # Check status after completion
        print('3. Checking final onboarding status...')
        final_status = requests.get('http://localhost:8000/auth/onboarding-status', headers=headers)
        print(f'   Final status: {final_status.json()}')
        
    else:
        print('Login failed:', response.text)
        
except Exception as e:
    print(f'Error: {e}')