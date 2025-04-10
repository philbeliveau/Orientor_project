import os
import sys
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Check if running on Railway
is_railway = os.getenv("RAILWAY_ENVIRONMENT") is not None or os.getenv("RAILWAY") is not None

# Handle database configuration
if is_railway:
    print("Running on Railway environment, using Railway PostgreSQL configuration")
else:
    print("Running in local development environment")
    
    # Fix database URL if needed - this is likely causing the "db" host error
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Make sure we're not using a "db" hostname (Docker-like setup)
        if "@db:" in database_url:
            fixed_url = database_url.replace("@db:", "@localhost:")
            os.environ["DATABASE_URL"] = fixed_url
            print(f"Changed DATABASE_URL from {database_url} to {fixed_url}")
        
        # Make sure we're not using Railway's internal hostnames when developing locally
        elif "railway.internal" in database_url or "monorail.proxy.rlwy.net" in database_url:
            # Parse and rebuild the URL with localhost
            print("Found Railway URL in local environment, using local database instead")
            # Extract the database name from the URL if possible
            db_name = database_url.split("/")[-1] if "/" in database_url else "orientor_db"
            local_url = f"postgresql://postgres:{os.getenv('POSTGRES_PASSWORD', 'Mac.phil.007')}@localhost:5432/{db_name}"
            os.environ["DATABASE_URL"] = local_url
            print(f"Using local DATABASE_URL: {local_url}")
        else:
            print(f"Using DATABASE_URL: {database_url}")
    else:
        print("No DATABASE_URL found, will try to construct from individual variables")
    
    # Always set PostgreSQL host to localhost for local development
    os.environ["POSTGRES_HOST"] = "localhost"

# Start the server with appropriate host/port
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"  # Bind to all interfaces
    
    print(f"Starting server on {host}:{port}...")
    uvicorn.run("main:app", host=host, port=port, reload=not is_railway)  # Only use reload in development 