import requests
import json

def test_comprehensive_onboarding():
    """Test complete onboarding flow with all fixes"""
    print("=== Comprehensive Onboarding Test ===")
    
    # Test with existing user
    login_url = 'http://localhost:8000/auth/login'
    login_data = {
        'email': 'beli5@example.com',
        'password': 'navigo_123'
    }
    
    try:
        # Login
        print("1. Logging in...")
        login_response = requests.post(login_url, json=login_data)
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        print("   ✅ Login successful")
        
        # Reset to test fresh flow
        print("2. Resetting onboarding...")
        reset_response = requests.delete('http://localhost:8000/onboarding/reset', headers=headers)
        assert reset_response.status_code == 200, f"Reset failed: {reset_response.text}"
        print("   ✅ Reset successful")
        
        # Test flow without explicit start (the fix)
        print("3. Saving responses without starting session (should auto-create session)...")
        
        responses = [
            {
                'questionId': 'emotion-1',
                'question': 'What makes you feel most alive?',
                'response': 'I feel most alive when I am solving complex problems and learning new things.',
                'timestamp': '2024-01-01T00:00:00Z'
            },
            {
                'questionId': 'hexaco-1',
                'question': 'When working on a team project, do you prefer to lead the discussion or contribute your ideas quietly?',
                'response': 'I prefer to lead the discussion and guide the team toward solutions.',
                'timestamp': '2024-01-01T00:01:00Z'
            },
            {
                'questionId': 'hexaco-2',
                'question': 'How do you typically handle stressful situations?',
                'response': 'I stay calm and break down the problem into manageable steps.',
                'timestamp': '2024-01-01T00:02:00Z'
            }
        ]
        
        for i, response_data in enumerate(responses):
            print(f"   Saving response {i+1}...")
            response_response = requests.post('http://localhost:8000/onboarding/response', json=response_data, headers=headers)
            assert response_response.status_code == 200, f"Response {i+1} failed: {response_response.text}"
            result = response_response.json()
            print(f"   ✅ Response {i+1} saved. Progress: {result['progress']}/{result['total']}")
        
        # Complete onboarding
        print("4. Completing onboarding...")
        complete_data = {
            'responses': responses,
            'psychProfile': {
                'hexaco': {
                    'extraversion': 85.0,
                    'openness': 90.0,
                    'conscientiousness': 80.0,
                    'emotionality': 40.0,
                    'agreeableness': 75.0,
                    'honesty': 85.0
                },
                'riasec': {
                    'realistic': 60.0,
                    'investigative': 95.0,
                    'artistic': 70.0,
                    'social': 80.0,
                    'enterprising': 85.0,
                    'conventional': 50.0
                },
                'topTraits': ['Analytical', 'Leadership', 'Problem-solving'],
                'description': 'A natural leader with strong analytical and investigative skills.'
            }
        }
        
        complete_response = requests.post('http://localhost:8000/onboarding/complete', json=complete_data, headers=headers)
        assert complete_response.status_code == 200, f"Complete failed: {complete_response.text}"
        print("   ✅ Onboarding completed successfully")
        
        # Check final status
        print("5. Checking final onboarding status...")
        final_status = requests.get('http://localhost:8000/auth/onboarding-status', headers=headers)
        assert final_status.status_code == 200, f"Status check failed: {final_status.text}"
        status_data = final_status.json()
        assert status_data['onboarding_completed'] == True, f"Onboarding not marked complete: {status_data}"
        print("   ✅ Onboarding status: COMPLETED")
        
        # Test that user won't see onboarding again
        print("6. Testing onboarding persistence...")
        status_response = requests.get('http://localhost:8000/auth/onboarding-status', headers=headers)
        status_data = status_response.json()
        assert status_data['onboarding_completed'] == True, "Onboarding should stay completed"
        print("   ✅ Onboarding persistence: WORKING")
        
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("✅ Auto-session creation: WORKING")
        print("✅ Response saving: WORKING")
        print("✅ Onboarding completion: WORKING")
        print("✅ Persistence: WORKING")
        print("✅ No more onboarding loops!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_comprehensive_onboarding()