#!/usr/bin/env python3
"""
Fix user password with proper bcrypt hash
"""

import os
import bcrypt
from sqlalchemy import create_engine, text

def fix_user_password():
    """Fix beli5@example.com password with fresh bcrypt hash"""
    
    railway_url = "postgresql://postgres:maywewVkqQnjHsGIuXjhpDRGoMnGcNPg@switchback.proxy.rlwy.net:58065/railway"
    
    try:
        engine = create_engine(railway_url)
        
        # Generate fresh bcrypt hash for 'navigo_123'
        password = 'navigo_123'
        fresh_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        print(f"🔐 Generated fresh hash for password '{password}': {fresh_hash}")
        
        with engine.connect() as conn:
            # Update the user with fresh hash
            result = conn.execute(text("""
                UPDATE users 
                SET encrypted_password = :new_hash 
                WHERE email = :email
            """), {
                "new_hash": fresh_hash,
                "email": "beli5@example.com"
            })
            
            print(f"✅ Updated {result.rowcount} user(s)")
            
            # Test the new hash
            test_result = bcrypt.checkpw(password.encode('utf-8'), fresh_hash.encode('utf-8'))
            print(f"🧪 Hash verification test: {test_result}")
            
            # Verify in database
            result = conn.execute(text("""
                SELECT email, encrypted_password 
                FROM users 
                WHERE email = :email
            """), {"email": "beli5@example.com"})
            
            user = result.fetchone()
            if user:
                print(f"📧 User: {user[0]}")
                print(f"🔑 Hash: {user[1][:20]}...{user[1][-10:]}")
                
                # Final verification
                final_test = bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8'))
                print(f"✅ Final verification: {final_test}")
            
            conn.commit()
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_user_password()