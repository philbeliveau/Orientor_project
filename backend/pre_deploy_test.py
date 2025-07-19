#!/usr/bin/env python3
"""
Pre-deployment test - Run before every Railway deployment
"""

import os
import sys
import subprocess
import time

def quick_deployment_test():
    """Quick test to verify deployment readiness"""
    
    print("🚀 PRE-DEPLOYMENT VERIFICATION")
    print("=" * 40)
    
    # Set Railway environment
    os.environ["PORT"] = "8080"
    os.environ["DATABASE_URL"] = "postgresql://postgres:maywewVkqQnjHsGIuXjhpDRGoMnGcNPg@switchback.proxy.rlwy.net:58065/railway"
    
    # Test 1: Import Check
    print("1️⃣ Testing imports...")
    try:
        from main_phase2_deploy import main
        from main_phase2_real import app
        print("   ✅ All imports successful")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Test 2: Database Connection
    print("2️⃣ Testing database...")
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT email FROM users WHERE email = 'beli5@example.com'"))
            user = result.fetchone()
            if user:
                print(f"   ✅ Database and target user ready")
            else:
                print(f"   ❌ Target user missing")
                return False
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False
    
    # Test 3: Routes Check
    print("3️⃣ Testing routes...")
    auth_login_exists = False
    health_exists = False
    
    for route in app.routes:
        if hasattr(route, 'path'):
            if route.path == "/auth/login":
                auth_login_exists = True
            elif route.path == "/health":
                health_exists = True
    
    if auth_login_exists and health_exists:
        print("   ✅ Critical routes available")
    else:
        print(f"   ❌ Missing routes - login: {auth_login_exists}, health: {health_exists}")
        return False
    
    print("\n🎉 DEPLOYMENT READY!")
    print("✅ All critical components verified")
    return True

if __name__ == "__main__":
    success = quick_deployment_test()
    if success:
        print("\n🚀 Proceeding with Railway deployment...")
    else:
        print("\n❌ Fix issues before deployment!")
    sys.exit(0 if success else 1)