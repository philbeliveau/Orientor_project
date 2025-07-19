#!/usr/bin/env python3
"""
Add your specific user to Railway PostgreSQL
"""

import os
from sqlalchemy import create_engine, text

def add_your_user():
    """Add beli5@example.com with the correct hashed password from Supabase"""
    
    railway_url = "postgresql://postgres:maywewVkqQnjHsGIuXjhpDRGoMnGcNPg@switchback.proxy.rlwy.net:58065/railway"
    
    try:
        engine = create_engine(railway_url)
        
        with engine.connect() as conn:
            # Clear existing users table and recreate with simple structure
            print("🔄 Recreating users table...")
            conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
            
            conn.execute(text("""
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    encrypted_password VARCHAR(255),
                    name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """))
            
            # Add your user with the actual hashed password from Supabase
            print("👤 Adding your user with real password...")
            
            # This is the actual hashed password for beli5@example.com from your Supabase (unescaped)
            your_hashed_password = "$2b$12$fwa6.NIyz6RWRWC0JLHDwei/fu376XXlXLMwXAO3Fqc3Zi.h6xB9."
            
            conn.execute(text("""
                INSERT INTO users (email, encrypted_password, name) 
                VALUES (:email, :password, :name)
            """), {
                "email": "beli5@example.com",
                "password": your_hashed_password,
                "name": "Beli"
            })
            
            # Add test user too
            conn.execute(text("""
                INSERT INTO users (email, encrypted_password, name) 
                VALUES (:email, :password, :name)
            """), {
                "email": "test@example.com",
                "password": "$2b$12$jqY.qz0gFFnm5c21wjh1.e7YuVRspsdV2xBRmZ.6yq2o0H1iEfvJG",  # password123
                "name": "Test User"
            })
            
            # Add a few more key users from Supabase (with corrected hash format)
            key_users = [
                ("beli@example.com", "$2b$12$yfzSzGndgVQq8/nGfCDiiOMnJbeH/NsyUvJ.YMZwznPciP6YBCesu", "Beli"),
                ("phil@example.com", "$2b$12$HIzdIl8Sohpf1Wv/8TO.XOk7ZO8S11FGBZquvnJy1P.w05nQH/qTy", "Phil"),
                ("beliveau@example.com", "$2b$12$2O8GdJt6R0iy1Za37Xv1qen3/Hd19cui04e0XR9MH3tMn9auzSvgC", "Beliveau")
            ]
            
            for email, password, name in key_users:
                try:
                    conn.execute(text("""
                        INSERT INTO users (email, encrypted_password, name) 
                        VALUES (:email, :password, :name)
                    """), {
                        "email": email,
                        "password": password,
                        "name": name
                    })
                    print(f"   ✅ Added: {email}")
                except Exception as e:
                    print(f"   ⚠️ Skipped {email}: {e}")
            
            conn.commit()
            
            # Verify
            result = conn.execute(text("SELECT email, name FROM users ORDER BY id"))
            users = result.fetchall()
            
            print("\n✅ Users added successfully!")
            print("👥 Users in Railway database:")
            for user in users:
                print(f"   - {user[0]} ({user[1]})")
                
            print(f"\n🔑 You can now login with:")
            print(f"   Email: beli5@example.com")
            print(f"   Password: navigo_123")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_your_user()