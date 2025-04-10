#!/usr/bin/env python3
"""
Railway Setup Script

This script helps verify and set up the necessary environment variables
for Railway deployment. It can be run locally to check if everything is
properly configured.
"""

import os
import sys
import json
import subprocess
from dotenv import load_dotenv

# Configure basic logging
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

def check_railway_cli():
    """Check if Railway CLI is installed and the user is logged in."""
    try:
        result = subprocess.run(["railway", "whoami"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
        if result.returncode == 0:
            logger.info("✅ Railway CLI is installed and you are logged in.")
            return True
        else:
            logger.error("❌ You are not logged into Railway CLI.")
            logger.info("Please run 'railway login' and try again.")
            return False
    except FileNotFoundError:
        logger.error("❌ Railway CLI is not installed.")
        logger.info("Please install it by running 'npm i -g @railway/cli'")
        return False

def get_required_env_vars():
    """Get the list of required environment variables for Railway."""
    return {
        # PostgreSQL
        "PGHOST": "postgres.railway.internal",
        "PGDATABASE": os.getenv("POSTGRES_DB", "railway"),
        "PGUSER": os.getenv("POSTGRES_USER", "postgres"),
        "PGPASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
        "PGPORT": "5432",
        
        # Application
        "PORT": "8000",
        "RAILWAY": "true",
        
        # API Keys (from .env)
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "HUGGINGFACE_API_KEY": os.getenv("HUGGINGFACE_API_KEY", ""),
        
        # JWT
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", ""),
        "ALGORITHM": os.getenv("ALGORITHM", "HS256"),
        "ACCESS_TOKEN_EXPIRE_MINUTES": os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"),
    }

def verify_railway_env_vars():
    """Check if all required environment variables are set on Railway."""
    logger.info("Checking Railway environment variables...")
    
    try:
        # Get current environment variables from Railway
        result = subprocess.run(["railway", "variables", "get"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True)
        
        if result.returncode != 0:
            logger.error(f"❌ Failed to get Railway variables: {result.stderr}")
            return False
        
        # Parse the variables
        railway_vars = {}
        for line in result.stdout.splitlines():
            if '=' in line:
                key, value = line.strip().split('=', 1)
                railway_vars[key] = value
        
        # Check required variables
        required_vars = get_required_env_vars()
        missing_vars = []
        
        for var, default_value in required_vars.items():
            if var not in railway_vars and not default_value:
                missing_vars.append(var)
        
        if missing_vars:
            logger.warning("⚠️ The following variables are missing from Railway:")
            for var in missing_vars:
                logger.warning(f"  - {var}")
            
            return False
        else:
            logger.info("✅ All required environment variables are set on Railway.")
            return True
    
    except Exception as e:
        logger.error(f"❌ Error verifying Railway variables: {str(e)}")
        return False

def set_railway_env_vars():
    """Set required environment variables on Railway."""
    logger.info("Setting up Railway environment variables...")
    
    required_vars = get_required_env_vars()
    
    # Confirm with user
    print("\nThe following variables will be set on Railway:")
    for key, value in required_vars.items():
        # Mask sensitive values
        masked_value = "****" if any(x in key.lower() for x in ["password", "secret", "key"]) else value
        print(f"  {key}={masked_value}")
    
    confirm = input("\nDo you want to continue? (y/n): ")
    if confirm.lower() != 'y':
        logger.info("Operation cancelled by user.")
        return False
    
    # Set variables
    success = True
    for key, value in required_vars.items():
        if not value:
            logger.warning(f"⚠️ Skipping {key} as it has no value.")
            continue
            
        try:
            # Set the variable
            cmd = ["railway", "variables", "--set", f"{key}={value}"]
            result = subprocess.run(cmd, 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE,
                                  text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Set {key}.")
            else:
                logger.error(f"❌ Failed to set {key}: {result.stderr}")
                success = False
        
        except Exception as e:
            logger.error(f"❌ Error setting {key}: {str(e)}")
            success = False
    
    if success:
        logger.info("✅ All environment variables have been set on Railway.")
    
    return success

def main():
    """Main function."""
    print("\n=== Railway Deployment Setup ===\n")
    
    # Check Railway CLI
    if not check_railway_cli():
        return 1
    
    # Verify environment variables
    if verify_railway_env_vars():
        print("\nYour Railway environment is already set up correctly!")
        return 0
    
    # Ask user if they want to set up environment variables
    print("\nSome required environment variables are missing from your Railway project.")
    confirm = input("Do you want to set them up now? (y/n): ")
    
    if confirm.lower() == 'y':
        if set_railway_env_vars():
            print("\nRailway environment variables have been set up successfully!")
            print("You can now deploy your application with 'railway up'")
            return 0
        else:
            print("\nFailed to set up all Railway environment variables.")
            return 1
    else:
        print("\nOperation cancelled by user.")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 