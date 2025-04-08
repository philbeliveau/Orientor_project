from dotenv import load_dotenv
import os
from openai import OpenAI
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_openai_api():
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    logger.info(f"API key exists: {bool(api_key)}")
    
    if not api_key:
        logger.error("API key not found in environment variables")
        return
    
    logger.info(f"API key starts with: {api_key[:5]}...")
    
    try:
        client = OpenAI(api_key=api_key)
        
        logger.info("Making API request to OpenAI...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, are you working?"}],
            max_tokens=50
        )
        
        logger.info(f"Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_openai_api()
    print(f"Test completed successfully: {success}") 