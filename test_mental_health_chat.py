#!/usr/bin/env python3
"""
Comprehensive Test Script for AI-Powered Mental Health Chat App
Based on PRD_Chat.md requirements

This script tests:
1. Chat Consultation Flow
2. AI-Powered Assessment
3. Structured Assessment Flow
4. Suggestion and Intervention Delivery
5. WebSocket Streaming
6. Knowledge Base Integration
"""

import asyncio
import websockets
import json
import requests
import time
from typing import Dict, List, Any
from datetime import datetime

class MentalHealthChatTester:
    def __init__(self, base_url="http://localhost:8000", ws_url="ws://localhost:8000/ws"):
        self.base_url = base_url
        self.ws_url = ws_url
        self.session_id = None
        self.test_results = []
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"[{status}] {test_name}: {details}")
    
    def test_backend_health(self):
        """Test if backend is running and healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.log_test("Backend Health Check", "PASS", "Backend is running")
                return True
            else:
                self.log_test("Backend Health Check", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health Check", "FAIL", str(e))
            return False
    
    def test_chat_initialization(self):
        """Test chat functionality by sending a simple message"""
        try:
            # Test basic chat endpoint
            response = requests.post(f"{self.base_url}/api/v1/chat/chat", 
                                   json={"message": "Hello, I need help with stress"}, 
                                   timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Chat Initialization", "PASS", "Chat endpoint responding")
                return True
            else:
                self.log_test("Chat Initialization", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Chat Initialization", "FAIL", str(e))
            return False
    
    def test_natural_language_understanding(self):
        """Test AI's ability to understand and categorize mental health concerns"""
        test_messages = [
            "I've been feeling really stressed at work lately",
            "I can't sleep and feel anxious all the time",
            "I experienced something traumatic and can't stop thinking about it"
        ]
        
        for message in test_messages:
            try:
                response = requests.post(f"{self.base_url}/api/v1/chat/chat",
                                       json={"message": message},
                                       timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    self.log_test("Natural Language Understanding", "PASS", 
                                f"Message: '{message[:30]}...' -> Response received")
                else:
                    self.log_test("Natural Language Understanding", "FAIL", 
                                f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test("Natural Language Understanding", "FAIL", str(e))
    
    def test_assessment_flow(self):
        """Test structured assessment functionality"""
        categories = ["stress", "anxiety", "trauma"]
        
        for category in categories:
            try:
                # Start assessment
                response = requests.post(f"{self.base_url}/api/v1/chat/assessment/start",
                                       json={"problem_category": category},
                                       timeout=10)
                if response.status_code == 200:
                    assessment_data = response.json()
                    
                    # Try to respond to assessment
                    answer_response = requests.post(f"{self.base_url}/api/v1/chat/assessment/respond",
                                                  json={
                                                      "answer": "Test answer",
                                                      "category": category
                                                  },
                                                  timeout=10)
                    
                    self.log_test("Assessment Flow", "PASS", f"Category: {category}")
                else:
                    self.log_test("Assessment Flow", "FAIL", 
                                f"Category: {category}, Status: {response.status_code}")
            except Exception as e:
                self.log_test("Assessment Flow", "FAIL", f"Category: {category}, Error: {str(e)}")
    
    def test_suggestion_delivery(self):
        """Test assessment recommendations delivery"""
        test_cases = [
            {"category": "stress", "responses": ["7", "8", "6"]},
            {"category": "anxiety", "responses": ["9", "7", "8"]},
            {"category": "trauma", "responses": ["6", "8", "7"]}
        ]
        
        for case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/chat/assessment/recommendations",
                    json=case,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    recommendations = data.get('recommendations', [])
                    
                    if recommendations:
                        self.log_test(
                            "Assessment Recommendations", 
                            "PASS", 
                            f"Category: {case['category']}, Received {len(recommendations)} recommendations"
                        )
                    else:
                        self.log_test(
                            "Assessment Recommendations", 
                            "FAIL", 
                            f"Category: {case['category']}, No recommendations received"
                        )
                else:
                    self.log_test(
                        "Assessment Recommendations", 
                        "FAIL", 
                        f"Category: {case['category']}, Status: {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_test(
                    "Assessment Recommendations", 
                    "FAIL", 
                    f"Category: {case['category']}, Error: {str(e)}"
                )
    
    async def test_websocket_streaming(self):
        """Test WebSocket streaming functionality"""
        try:
            # Use the correct WebSocket endpoint
            ws_url = "ws://localhost:8000/api/v1/chat/ws/chat/stream"
            async with websockets.connect(ws_url) as websocket:
                # Send a test message
                test_message = {
                    "message": "I'm feeling anxious about my upcoming presentation",
                    "session_data": {
                        "user_name": "Test User"
                    }
                }
                
                await websocket.send(json.dumps(test_message))
                self.log_test("WebSocket - Send Message", "PASS", "Message sent successfully")
                
                # Receive streaming response
                response_chunks = []
                timeout_counter = 0
                max_timeout = 30  # 30 seconds timeout
                
                while timeout_counter < max_timeout:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(response)
                        response_chunks.append(data)
                        
                        if data.get('type') == 'complete':
                            break
                        elif data.get('type') == 'chunk':
                            continue
                            
                    except asyncio.TimeoutError:
                        timeout_counter += 1
                        continue
                
                if response_chunks:
                    self.log_test(
                        "WebSocket - Streaming Response", 
                        "PASS", 
                        f"Received {len(response_chunks)} chunks"
                    )
                else:
                    self.log_test("WebSocket - Streaming Response", "FAIL", "No response received")
                    
        except Exception as e:
            self.log_test("WebSocket Streaming", "FAIL", str(e))
    
    def test_model_status(self):
        """Test AI model status and availability"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/chat/model/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                model_name = data.get('model', 'Unknown')
                status = data.get('status', 'Unknown')
                self.log_test(
                    "Model Status", 
                    "PASS", 
                    f"Model: {model_name}, Status: {status}"
                )
            else:
                self.log_test("Model Status", "FAIL", f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Model Status", "FAIL", str(e))
    
    def test_conversation_history(self):
        """Test conversation history functionality"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/chat/conversation/history", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                conversations = data.get('conversations', [])
                self.log_test(
                    "Conversation History", 
                    "PASS", 
                    f"Retrieved {len(conversations)} conversations"
                )
            else:
                self.log_test("Conversation History", "FAIL", f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Conversation History", "FAIL", str(e))
    
    def test_crisis_detection(self):
        """Test crisis detection in chat responses"""
        crisis_messages = [
            "I want to hurt myself",
            "I'm thinking about ending it all",
            "I don't want to live anymore",
            "I'm planning to kill myself"
        ]
        
        for message in crisis_messages:
            try:
                response = requests.post(f"{self.base_url}/api/v1/chat/chat",
                                       json={"message": message},
                                       timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    is_crisis = data.get('is_crisis', False)
                    
                    if is_crisis:
                        self.log_test(
                            "Crisis Detection", 
                            "PASS", 
                            f"Crisis detected for: '{message[:30]}...'"
                        )
                    else:
                        self.log_test(
                            "Crisis Detection", 
                            "WARN", 
                            f"Crisis not detected for: '{message[:30]}...'"
                        )
                else:
                    self.log_test("Crisis Detection", "FAIL", f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test("Crisis Detection", "FAIL", str(e))
    
    def generate_report(self):
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed_tests = total_tests - passed_tests
        
        report = f"""
=== MENTAL HEALTH CHAT APP TEST REPORT ===
Generated: {datetime.now().isoformat()}

SUMMARY:
- Total Tests: {total_tests}
- Passed: {passed_tests}
- Failed: {failed_tests}
- Success Rate: {(passed_tests/total_tests*100):.1f}%

DETAILED RESULTS:
"""
        
        for result in self.test_results:
            report += f"\n[{result['status']}] {result['test_name']}"
            if result['details']:
                report += f": {result['details']}"
        
        report += "\n\n=== END REPORT ==="
        
        # Save report to file
        with open('test_report.txt', 'w') as f:
            f.write(report)
        
        print(report)
        return report
    
    async def run_all_tests(self):
        """Run all tests in sequence"""
        print("Starting Mental Health Chat App Tests...\n")
        
        # Basic connectivity tests
        if not self.test_backend_health():
            print("Backend is not running. Please start the backend server first.")
            return
        
        if not self.test_chat_initialization():
            print("Chat initialization failed. Cannot proceed with other tests.")
            return
        
        # Core functionality tests
        self.test_natural_language_understanding()
        self.test_assessment_flow()
        self.test_suggestion_delivery()
        self.test_model_status()
        self.test_conversation_history()
        self.test_crisis_detection()
        
        # WebSocket streaming test
        await self.test_websocket_streaming()
        
        # Generate final report
        self.generate_report()

async def main():
    """Main test execution function"""
    tester = MentalHealthChatTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())