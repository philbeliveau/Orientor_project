import requests
import json
import logging
import time
import os
import random
import string
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load any environment variables
load_dotenv()

def generate_random_user():
    """Generate random user credentials for testing."""
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return {
        "username": f"testuser_{random_string}",
        "email": f"test_{random_string}@example.com",
        "password": f"Password123_{random_string}"
    }

def register_user():
    """Register a new user for testing."""
    logger.info("Registering a new test user...")
    
    # Generate random user data to avoid conflicts
    user_data = generate_random_user()
    
    try:
        response = requests.post(
            'http://localhost:8000/users/register',
            json=user_data
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully registered user: {user_data['email']}")
            # Save credentials for future use
            return user_data
        else:
            logger.error(f"Registration failed with status code {response.status_code}: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return None

def get_auth_token(user_data=None):
    """Get authentication token by logging in."""
    logger.info("Attempting to log in...")
    
    if not user_data:
        # Try to create a new user
        user_data = register_user()
        if not user_data:
            logger.error("Could not register a new user")
            return None
    
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/users/login',
            json=login_data
        )
        
        if response.status_code == 200:
            token = response.json().get('access_token')
            logger.info("Successfully obtained token")
            return token
        else:
            logger.error(f"Login failed with status code {response.status_code}: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return None

def test_chat_endpoint(token=None, user_data=None):
    logger.info("Testing chat endpoint...")
    
    if not token:
        logger.warning("No token provided, attempting to get one...")
        token = get_auth_token(user_data)
        
    if not token:
        logger.error("Could not obtain a valid token. Aborting test.")
        return False
    
    try:
        logger.info("Sending request to chat endpoint...")
        response = requests.post(
            'http://localhost:8000/chat/send',
            json={'text': 'Tell me about career options in technology'},
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            timeout=30  # Add timeout to prevent hanging
        )
        
        logger.info(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            logger.info(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            logger.error(f"Error response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("Request timed out. The LLM response may be taking too long.")
        return False
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return False

def check_server_status():
    """Check if the backend server is running."""
    try:
        response = requests.get('http://localhost:8000/')
        if response.status_code == 200:
            logger.info("Backend server is running")
            return True
        else:
            logger.error(f"Backend server returned unexpected status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error("Backend server is not running or not accessible")
        return False

if __name__ == "__main__":
    if not check_server_status():
        print("Backend server is not running. Please start it before running this test.")
        exit(1)
    
    # First register a user
    user_data = register_user()
    if not user_data:
        print("Failed to register a test user. Using existing credentials if available.")
    
    # Then test the chat endpoint
    success = test_chat_endpoint(user_data=user_data)
    print(f"Test completed: {success}") 