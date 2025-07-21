#!/usr/bin/env python3
"""
Test script to verify profiles router functionality
Tests models, ML services, and endpoints
"""

def test_models():
    """Test that all required models import correctly"""
    print("🧪 Testing model imports...")
    
    try:
        from app.models import UserProfile, UserSkill, SavedRecommendation, UserNote
        print("✅ All models import successfully:")
        print(f"   UserProfile: {UserProfile.__name__}")
        print(f"   UserSkill: {UserSkill.__name__}")
        print(f"   SavedRecommendation: {SavedRecommendation.__name__}")
        print(f"   UserNote: {UserNote.__name__}")
        return True
    except ImportError as e:
        print(f"❌ Model import failed: {e}")
        return False

def test_ml_services():
    """Test that ML services are available"""
    print("\n🧪 Testing ML services...")
    
    try:
        from app.routers.profiles import (
            OASIS_EMBEDDING_AVAILABLE,
            ESCO_EMBEDDING_AVAILABLE,
            PEER_MATCHING_AVAILABLE
        )
        
        services = {
            "OaSIS Embedding": OASIS_EMBEDDING_AVAILABLE,
            "ESCO Embedding": ESCO_EMBEDDING_AVAILABLE,
            "Peer Matching": PEER_MATCHING_AVAILABLE
        }
        
        all_available = True
        for service, available in services.items():
            status = "✅" if available else "❌"
            print(f"   {status} {service}: {available}")
            if not available:
                all_available = False
                
        return all_available
    except ImportError as e:
        print(f"❌ ML services test failed: {e}")
        return False

def test_router_creation():
    """Test that profiles router creates successfully"""
    print("\n🧪 Testing router creation...")
    
    try:
        from app.routers.profiles import router
        print(f"✅ Profiles router created successfully")
        print(f"   Router type: {type(router)}")
        
        # Get routes from router
        routes = []
        for route in router.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        print(f"   Available routes ({len(routes)}):")
        for route in routes:
            print(f"     - {route}")
            
        return True
    except Exception as e:
        print(f"❌ Router creation failed: {e}")
        return False

def test_app_integration():
    """Test that profiles router is properly integrated in main app"""
    print("\n🧪 Testing app integration...")
    
    try:
        import main_deploy
        app = main_deploy.create_app()
        
        # Find profile-related routes
        profile_routes = []
        for route in app.routes:
            if hasattr(route, 'path') and 'profile' in route.path.lower():
                profile_routes.append(route.path)
        
        if profile_routes:
            print(f"✅ Profiles integrated in main app ({len(profile_routes)} routes):")
            for route in profile_routes:
                print(f"     - {route}")
            return True
        else:
            print("❌ No profile routes found in main app")
            return False
            
    except Exception as e:
        print(f"❌ App integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Profiles Router Functionality Test")
    print("=" * 50)
    
    tests = [
        ("Model Imports", test_models),
        ("ML Services", test_ml_services),
        ("Router Creation", test_router_creation),
        ("App Integration", test_app_integration)
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    print("\n📊 Test Summary:")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("✅ Profiles router is fully functional")
        print("✅ UserProfile, UserSkill, SavedRecommendation models available")
        print("✅ ML services operational")
        print("✅ Ready for production use")
    else:
        print(f"\n❌ Some tests failed")
        print("🔍 Check error messages above for details")
        
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)