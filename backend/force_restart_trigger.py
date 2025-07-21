#!/usr/bin/env python3
"""
Force Railway deployment restart by updating a timestamp file
This will clear SQLAlchemy metadata cache and connection pools
"""

import os
from datetime import datetime

def create_restart_trigger():
    """Create a file that will trigger Railway restart when deployed"""
    
    # Create a timestamp file that Railway will see as a change
    timestamp = datetime.utcnow().isoformat()
    
    trigger_content = f"""# Railway Restart Trigger
# Generated: {timestamp}
# Purpose: Force deployment restart to clear SQLAlchemy metadata cache
# 
# This file triggers a restart when committed and pushed to Railway
# The sequence fix is complete but SQLAlchemy needs to refresh its metadata cache
"""
    
    with open('.railway_restart_trigger', 'w') as f:
        f.write(trigger_content)
    
    print(f"[SUCCESS] Restart trigger created with timestamp: {timestamp}")
    print("[INFO] Commit and push this file to force Railway deployment restart")
    
    return True

if __name__ == "__main__":
    create_restart_trigger()