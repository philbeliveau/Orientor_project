#!/usr/bin/env python3
"""
Comprehensive test suite for Railway deployment
Tests all Phase 2 + Phase 3B Batch 1 + Batch 2 endpoints
"""

import requests
import json
import time
import sys
from datetime import datetime

# Test configuration
LOCAL_URL = "http://localhost:8003"

# Use local for comprehensive testing
BASE_URL = LOCAL_URL

class OrientorTester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   📝 {details}")
        if response_data and not success:
            print(f"   📊 Response: {response_data}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_health_check(self):
        """Test basic health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            success = response.status_code == 200
            self.log_test("Health Check", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            success = response.status_code == 200
            if success:
                data = response.json()
                version = data.get("version", "unknown")
                self.log_test("Root Endpoint", True, f"Version: {version}")
            else:
                self.log_test("Root Endpoint", False, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_register_user(self):
        """Test user registration"""
        try:
            test_email = f"test_{int(time.time())}@orientor.test"
            register_data = {
                "email": test_email,
                "password": "testpassword123",
                "name": "Test User"
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=register_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.log_test("User Registration", True, f"User ID: {self.user_id}")
                return True
            else:
                self.log_test("User Registration", False, f"Status: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("User Registration", False, f"Exception: {str(e)}")
            return False
    
    def test_login_user(self):
        """Test user login with existing test user"""
        try:
            # Try to login with a known test user first
            login_data = {
                "email": "test@orientor.com",
                "password": "testpassword"
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.log_test("User Login", True, f"Token received for user {self.user_id}")
                return True
            else:
                self.log_test("User Login", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("User Login", False, f"Exception: {str(e)}")
            return False
    
    def get_auth_headers(self):
        """Get authentication headers"""
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}
    
    def test_authenticated_endpoint(self, endpoint, method="GET", data=None, test_name=None):
        """Test any authenticated endpoint"""
        if not test_name:
            test_name = f"Auth Test: {method} {endpoint}"
        
        try:
            headers = self.get_auth_headers()
            if not headers:
                self.log_test(test_name, False, "No authentication token available")
                return False
            
            if method == "GET":
                response = self.session.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
            elif method == "POST":
                response = self.session.post(f"{self.base_url}{endpoint}", json=data, headers=headers, timeout=10)
            else:
                self.log_test(test_name, False, f"Unsupported method: {method}")
                return False
            
            success = response.status_code == 200
            if success:
                try:
                    response_data = response.json()
                    self.log_test(test_name, True, f"Status: {response.status_code}")
                    return response_data
                except:
                    self.log_test(test_name, True, f"Status: {response.status_code} (non-JSON response)")
                    return True
            else:
                self.log_test(test_name, False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test(test_name, False, f"Exception: {str(e)}")
            return False
    
    def test_phase2_endpoints(self):
        """Test all Phase 2 endpoints"""
        print("\n📋 Testing Phase 2 Endpoints...")
        
        endpoints = [
            "/auth/me",
            "/auth/onboarding-status", 
            "/api/v1/avatar/me",
            "/user-progress/",
            "/api/v1/courses",
            "/api/v1/career-goals/active",
            "/space/notes",
            "/peers/compatible",
            "/api/tests/holland/user-results",
            "/api/v1/jobs/recommendations/me"
        ]
        
        results = []
        for endpoint in endpoints:
            result = self.test_authenticated_endpoint(endpoint, test_name=f"Phase 2: {endpoint}")
            results.append(result is not False)
        
        success_rate = sum(results) / len(results) * 100
        self.log_test("Phase 2 Endpoints Overall", success_rate >= 80, f"Success rate: {success_rate:.1f}%")
        return success_rate >= 80
    
    def test_batch1_endpoints(self):
        """Test Phase 3B Batch 1 (Enhanced Assessment) endpoints"""
        print("\n🧠 Testing Phase 3B Batch 1 - Enhanced Assessment Endpoints...")
        
        # Test HEXACO endpoints
        hexaco_results = []
        
        # Test HEXACO questions
        result = self.test_authenticated_endpoint("/api/tests/hexaco/questions", test_name="HEXACO: Questions")
        hexaco_results.append(result is not False)
        
        # Test HEXACO versions
        result = self.test_authenticated_endpoint("/api/tests/hexaco/versions", test_name="HEXACO: Versions")
        hexaco_results.append(result is not False)
        
        # Test HEXACO start
        start_data = {"version_id": "hexaco-pi-r-60"}
        result = self.test_authenticated_endpoint("/api/tests/hexaco/start", "POST", start_data, "HEXACO: Start Test")
        hexaco_results.append(result is not False)
        
        # Test Holland endpoints
        holland_results = []
        
        # Test Holland metadata
        result = self.test_authenticated_endpoint("/api/tests/holland", test_name="Holland: Metadata")
        holland_results.append(result is not False)
        
        # Test Holland questions
        result = self.test_authenticated_endpoint("/api/tests/holland/questions", test_name="Holland: Questions")
        holland_results.append(result is not False)
        
        hexaco_rate = sum(hexaco_results) / len(hexaco_results) * 100
        holland_rate = sum(holland_results) / len(holland_results) * 100
        overall_rate = (sum(hexaco_results) + sum(holland_results)) / (len(hexaco_results) + len(holland_results)) * 100
        
        self.log_test("HEXACO Endpoints", hexaco_rate >= 80, f"Success rate: {hexaco_rate:.1f}%")
        self.log_test("Holland Endpoints", holland_rate >= 80, f"Success rate: {holland_rate:.1f}%")
        self.log_test("Batch 1 Endpoints Overall", overall_rate >= 80, f"Success rate: {overall_rate:.1f}%")
        
        return overall_rate >= 80
    
    def test_batch2_endpoints(self):
        """Test Phase 3B Batch 2 (AI-Powered Career Guidance) endpoints"""
        print("\n🤖 Testing Phase 3B Batch 2 - AI-Powered Career Guidance Endpoints...")
        
        results = []
        
        # Test enhanced chat
        chat_data = {
            "message": "I want to learn about data science careers",
            "conversation_history": [],
            "user_context": {}
        }
        result = self.test_authenticated_endpoint("/enhanced-chat/send", "POST", chat_data, "AI Chat: Send Message")
        results.append(result is not False)
        
        # Test skill explanation
        result = self.test_authenticated_endpoint("/enhanced-chat/skill-explanation/python", test_name="AI Chat: Skill Explanation")
        results.append(result is not False)
        
        # Test learning recommendations
        result = self.test_authenticated_endpoint("/enhanced-chat/learning-recommendations", test_name="AI Chat: Learning Recommendations")
        results.append(result is not False)
        
        # Test competence tree
        result = self.test_authenticated_endpoint("/competence-tree/generate", test_name="AI: Competence Tree")
        results.append(result is not False)
        
        # Test career progression
        result = self.test_authenticated_endpoint("/career-progression/data_scientist/personalized", test_name="AI: Career Progression")
        results.append(result is not False)
        
        success_rate = sum(results) / len(results) * 100
        self.log_test("Batch 2 AI Endpoints Overall", success_rate >= 80, f"Success rate: {success_rate:.1f}%")
        return success_rate >= 80
    
    def test_complete_hexaco_flow(self):
        """Test complete HEXACO assessment flow"""
        print("\n🧪 Testing Complete HEXACO Assessment Flow...")
        
        try:
            # Start test
            start_data = {"version_id": "hexaco-pi-r-60"}
            start_result = self.test_authenticated_endpoint("/api/tests/hexaco/start", "POST", start_data, "HEXACO Flow: Start")
            
            if not start_result:
                return False
            
            session_id = start_result.get("session_id")
            if not session_id:
                self.log_test("HEXACO Flow: Session ID", False, "No session ID returned")
                return False
            
            # Submit a few test answers
            for i in range(1, 4):  # Submit 3 test answers
                answer_data = {
                    "session_id": session_id,
                    "question_id": i,
                    "answer": 3,  # Neutral answer
                    "factor": "Honesty-Humility" if i <= 2 else "Emotionality"
                }
                result = self.test_authenticated_endpoint("/api/tests/hexaco/answer", "POST", answer_data, f"HEXACO Flow: Answer {i}")
                if not result:
                    return False
            
            self.log_test("HEXACO Complete Flow", True, "Successfully submitted test answers")
            return True
            
        except Exception as e:
            self.log_test("HEXACO Complete Flow", False, f"Exception: {str(e)}")
            return False
    
    def test_complete_holland_flow(self):
        """Test complete Holland assessment flow"""
        print("\n🎯 Testing Complete Holland Assessment Flow...")
        
        try:
            # Get questions first
            questions_result = self.test_authenticated_endpoint("/api/tests/holland/questions", test_name="Holland Flow: Get Questions")
            
            if not questions_result:
                return False
            
            session_id = questions_result.get("session_id")
            if not session_id:
                self.log_test("Holland Flow: Session ID", False, "No session ID in questions response")
                return False
            
            # Prepare sample responses (normally would be from user input)
            sample_responses = []
            factors = ["Realistic", "Investigative", "Artistic", "Social", "Enterprising", "Conventional"]
            
            for i in range(30):  # 30 questions total
                factor = factors[i % 6]  # Cycle through factors
                sample_responses.append({
                    "question_id": i + 1,
                    "factor": factor,
                    "answer": 3 + (i % 3)  # Vary answers between 3-5
                })
            
            # Submit complete assessment
            submit_data = {
                "session_id": session_id,
                "responses": sample_responses
            }
            
            result = self.test_authenticated_endpoint("/api/tests/holland/submit", "POST", submit_data, "Holland Flow: Submit Assessment")
            
            if result:
                holland_code = result.get("holland_code")
                self.log_test("Holland Complete Flow", True, f"Holland Code: {holland_code}")
                return True
            else:
                return False
                
        except Exception as e:
            self.log_test("Holland Complete Flow", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting Comprehensive Orientor Platform Test Suite")
        print(f"🌍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Basic connectivity tests
        print("\n🔧 Basic Connectivity Tests...")
        health_ok = self.test_health_check()
        root_ok = self.test_root_endpoint()
        
        if not (health_ok and root_ok):
            print("❌ Basic connectivity failed. Stopping tests.")
            return False
        
        # Authentication tests
        print("\n🔐 Authentication Tests...")
        auth_ok = self.test_login_user()
        if not auth_ok:
            print("⚠️ Login failed, trying registration...")
            auth_ok = self.test_register_user()
        
        if not auth_ok:
            print("❌ Authentication failed. Stopping tests.")
            return False
        
        # Test all endpoint groups
        phase2_ok = self.test_phase2_endpoints()
        batch1_ok = self.test_batch1_endpoints()  
        batch2_ok = self.test_batch2_endpoints()
        
        # Test complete workflows
        hexaco_flow_ok = self.test_complete_hexaco_flow()
        holland_flow_ok = self.test_complete_holland_flow()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = passed_tests / total_tests * 100 if total_tests > 0 else 0
        
        print(f"✅ Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"🔧 Basic Connectivity: {'✅' if health_ok and root_ok else '❌'}")
        print(f"🔐 Authentication: {'✅' if auth_ok else '❌'}")
        print(f"📋 Phase 2 Endpoints: {'✅' if phase2_ok else '❌'}")
        print(f"🧠 Batch 1 (Assessment): {'✅' if batch1_ok else '❌'}")
        print(f"🤖 Batch 2 (AI Guidance): {'✅' if batch2_ok else '❌'}")
        print(f"🧪 HEXACO Flow: {'✅' if hexaco_flow_ok else '❌'}")
        print(f"🎯 Holland Flow: {'✅' if holland_flow_ok else '❌'}")
        
        overall_success = success_rate >= 85
        print(f"\n🎯 Overall Status: {'✅ READY FOR PRODUCTION' if overall_success else '⚠️ NEEDS ATTENTION'}")
        
        return overall_success

def main():
    """Main test execution"""
    print("🧪 Orientor Platform - Comprehensive Deployment Test")
    print("=" * 60)
    
    # Test Local deployment
    print("🏠 Testing Local Deployment...")
    local_tester = OrientorTester(LOCAL_URL)
    local_success = local_tester.run_all_tests()
    
    print("\n" + "=" * 60)
    print(f"🎯 FINAL RESULT: {'✅ DEPLOYMENT READY' if local_success else '❌ DEPLOYMENT ISSUES'}")
    print("=" * 60)
    
    return local_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)