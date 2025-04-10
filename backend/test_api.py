import requests
import json
import logging
import sys
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.access_token: Optional[str] = None
        self.test_user = {
            "email": "test_user@example.com",
            "password": "test_password123!"
        }

    def test_root(self) -> bool:
        """Test the root endpoint"""
        try:
            response = requests.get(f"{self.base_url}/")
            logger.info(f"Root endpoint response: {response.text}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error testing root endpoint: {str(e)}")
            return False

    def test_register(self) -> bool:
        """Test user registration"""
        try:
            response = requests.post(
                f"{self.base_url}/users/register",
                json=self.test_user
            )
            logger.info(f"Register response: {response.text}")
            return response.status_code in [200, 201, 400]  # 400 is ok if user exists
        except Exception as e:
            logger.error(f"Error testing registration: {str(e)}")
            return False

    def test_login(self) -> bool:
        """Test user login"""
        try:
            response = requests.post(
                f"{self.base_url}/users/login",
                json=self.test_user
            )
            if response.status_code == 200:
                self.access_token = response.json()["access_token"]
                logger.info("Login successful, token received")
                return True
            logger.error(f"Login failed: {response.text}")
            return False
        except Exception as e:
            logger.error(f"Error testing login: {str(e)}")
            return False

    def test_profile(self) -> bool:
        """Test profile endpoints"""
        if not self.access_token:
            logger.error("No access token available")
            return False

        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            # Get profile
            get_response = requests.get(
                f"{self.base_url}/profiles/me",
                headers=headers
            )
            logger.info(f"Get profile response: {get_response.text}")

            # Update profile
            profile_data = {
                "favorite_movie": "Test Movie",
                "favorite_book": "Test Book",
                "favorite_celebrities": "Test Celebrity",
                "learning_style": "Visual",
                "interests": "Testing"
            }
            update_response = requests.put(
                f"{self.base_url}/profiles/update",
                headers=headers,
                json=profile_data
            )
            logger.info(f"Update profile response: {update_response.text}")

            return get_response.status_code == 200 and update_response.status_code == 200
        except Exception as e:
            logger.error(f"Error testing profile endpoints: {str(e)}")
            return False

    def test_chat(self) -> bool:
        """Test chat endpoints"""
        if not self.access_token:
            logger.error("No access token available")
            return False

        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            # Send a test message
            message_data = {"text": "Hello, this is a test message"}
            send_response = requests.post(
                f"{self.base_url}/chat/send",
                headers=headers,
                json=message_data
            )
            logger.info(f"Send message response: {send_response.text}")

            # Clear chat history
            clear_response = requests.post(
                f"{self.base_url}/chat/clear",
                headers=headers
            )
            logger.info(f"Clear chat response: {clear_response.text}")

            return send_response.status_code == 200 and clear_response.status_code == 200
        except Exception as e:
            logger.error(f"Error testing chat endpoints: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all tests and return overall status"""
        tests = {
            "Root Endpoint": self.test_root,
            "User Registration": self.test_register,
            "User Login": self.test_login,
            "Profile Endpoints": self.test_profile,
            "Chat Endpoints": self.test_chat
        }

        results = {}
        all_passed = True

        for test_name, test_func in tests.items():
            logger.info(f"\nRunning test: {test_name}")
            passed = test_func()
            results[test_name] = "PASSED" if passed else "FAILED"
            all_passed = all_passed and passed
            logger.info(f"{test_name}: {results[test_name]}")

        logger.info("\nTest Summary:")
        for test_name, result in results.items():
            logger.info(f"{test_name}: {result}")

        return all_passed

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_api.py <api_base_url>")
        print("Example: python test_api.py https://your-api.railway.app")
        sys.exit(1)

    api_base_url = sys.argv[1]
    tester = APITester(api_base_url)
    success = tester.run_all_tests()
    sys.exit(0 if success else 1) 