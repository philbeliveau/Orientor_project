import os
import sys
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Fix database URL if needed
database_url = os.getenv("DATABASE_URL")
if database_url and "@db:" in database_url:
    fixed_url = database_url.replace("@db:", "@localhost:")
    os.environ["DATABASE_URL"] = fixed_url
    print(f"Changed DATABASE_URL from {database_url} to {fixed_url}")
else:
    print(f"Using DATABASE_URL: {database_url}")

# Set PostgreSQL host to localhost
os.environ["POSTGRES_HOST"] = "localhost"

# Start the server
if __name__ == "__main__":
    print("Starting server with fixed database configuration...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 