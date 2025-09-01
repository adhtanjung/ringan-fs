#!/usr/bin/env python3
"""
Stress Assessment Flow Test

This script tests the assessment flow functionality for the stress domain,
simulating a dialog-based interaction using questions from the vector database.
It verifies that the assessment runs smoothly and accurately reflects the
intended conversational flow.
"""

import asyncio
import json
import requests
import websockets
import time
from typing import Dict, List, Any
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/api/v1/chat/ws/test_client"
API_KEY = "your-api-key-here"  # Replace with actual API key if needed

class StressAssessmentTester:
    def __init__(self):
        self.session_id = f"test_session_{int(time.time())}"
        self.conversation_id = f"test_conv_{int(time.time())}"
        self.assessment_responses = []
        self.test_results = []
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = {
            "timestamp": timestamp,
            "test": test_name,
            "status": status,
            "details": details
        }
        self.test_results.append(result)
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏳"
        print(f"[{timestamp}] {status_emoji} {test_name}: {status}")
        if details:
            print(f"    Details: {details}")
    
    async def test_vector_search_stress_questions(self):
        """Test vector search for stress-related assessment questions"""
        self.log_test("Vector Search - Stress Questions", "RUNNING")
        
        try:
            # Search for stress-related assessment questions
            search_payload = {
                "query": "stress anxiety work pressure",
                "collection": "mental-health-assessments",
                "limit": 5,
                "score_threshold": 0.6
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/vector/search",
                json=search_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                results = response.json()
                questions = results.get("results", [])
                
                if len(questions) >= 1:  # At least 1 question is sufficient
                    self.log_test(
                        "Vector Search - Stress Questions", 
                        "PASS", 
                        f"Found {len(questions)} stress assessment questions"
                    )
                    return questions  # Return all found questions
                else:
                    self.log_test(
                        "Vector Search - Stress Questions", 
                        "FAIL", 
                        f"No questions found in the vector database"
                    )
                    return []
            else:
                self.log_test(
                    "Vector Search - Stress Questions", 
                    "FAIL", 
                    f"API returned status {response.status_code}: {response.text}"
                )
                return []
                
        except Exception as e:
            self.log_test(
                "Vector Search - Stress Questions", 
                "FAIL", 
                f"Exception: {str(e)}"
            )
            return []
    
    async def test_assessment_initialization(self):
        """Test assessment initialization via API"""
        self.log_test("Assessment Initialization", "RUNNING")
        
        try:
            # Start stress assessment
            start_payload = {
                "problem_category": "stress"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/chat/assessment/start",
                json=start_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("type") == "assessment_question" and "question" in result:
                    self.log_test(
                        "Assessment Initialization", 
                        "PASS", 
                        f"Assessment started with session ID: {result.get('session_id', 'unknown')}"
                    )
                    return result
                else:
                    self.log_test(
                        "Assessment Initialization", 
                        "FAIL", 
                        f"Unexpected response format: {result}"
                    )
                    return None
            else:
                self.log_test(
                    "Assessment Initialization", 
                    "FAIL", 
                    f"API returned status {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Assessment Initialization", 
                "FAIL", 
                f"Exception: {str(e)}"
            )
            return None
    
    async def test_websocket_assessment_flow(self):
        """Test assessment flow via WebSocket"""
        self.log_test("WebSocket Assessment Flow", "RUNNING")
        
        try:
            # Simulate stress-related conversation that should trigger assessment
            stress_messages = [
                "I've been feeling really overwhelmed at work lately",
                "The pressure from my boss is getting to me and I can't sleep",
                "I feel like I'm constantly stressed and can't relax",
                "My workload is too much and I'm having panic attacks"
            ]
            
            # Use the correct WebSocket URL with session_id as client_id
            ws_url = f"ws://localhost:8000/api/v1/chat/ws/{self.session_id}"
            async with websockets.connect(ws_url) as websocket:
                assessment_triggered = False
                question_count = 0
                
                for i, message in enumerate(stress_messages):
                    # Send message with simplified format
                    message_data = {
                        "message": message,
                        "session_data": {
                            "sessionId": self.session_id,
                            "conversationId": self.conversation_id,
                            "preferredLanguage": "en",
                            "mode": "help",
                            "problem_category": "stress"
                        }
                    }
                    
                    await websocket.send(json.dumps(message_data))
                    
                    # Collect response chunks
                    response_chunks = []
                    while True:
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                            data = json.loads(response)
                            
                            if data.get("type") == "chunk":
                                response_chunks.append(data.get("content", ""))
                            elif data.get("type") == "complete":
                                response_chunks.append(data.get("content", ""))
                                
                                # Check if assessment was suggested
                                if data.get("should_show_assessment"):
                                    assessment_triggered = True
                                    self.log_test(
                                        "Assessment Trigger Detection", 
                                        "PASS", 
                                        f"Assessment triggered after message {i+1}"
                                    )
                                
                                # Check for assessment questions
                                if "assessment_questions" in data:
                                    question_count += len(data["assessment_questions"])
                                
                                break
                            elif data.get("type") == "error":
                                self.log_test(
                                    "WebSocket Assessment Flow", 
                                    "FAIL", 
                                    f"WebSocket error: {data.get('message')}"
                                )
                                return False
                                
                        except asyncio.TimeoutError:
                            self.log_test(
                                "WebSocket Assessment Flow", 
                                "FAIL", 
                                "Timeout waiting for response"
                            )
                            return False
                    
                    # Small delay between messages
                    await asyncio.sleep(1)
                
                if assessment_triggered:
                    self.log_test(
                        "WebSocket Assessment Flow", 
                        "PASS", 
                        f"Assessment flow completed successfully with {question_count} questions"
                    )
                    return True
                else:
                    self.log_test(
                        "WebSocket Assessment Flow", 
                        "FAIL", 
                        "Assessment was not triggered despite stress-related messages"
                    )
                    return False
                    
        except Exception as e:
            self.log_test(
                "WebSocket Assessment Flow", 
                "FAIL", 
                f"Exception: {str(e)}"
            )
            return False
    
    async def test_assessment_response_handling(self, assessment_data):
        """Test assessment response handling"""
        if not assessment_data:
            self.log_test("Assessment Response Handling", "SKIP", "No assessment data available")
            return False
            
        self.log_test("Assessment Response Handling", "RUNNING")
        
        try:
            session_id = assessment_data.get("session_id", "test_assessment")
            first_question = assessment_data.get("question", {})
            
            # Simulate responses to assessment questions
            test_responses = [
                {"question_id": first_question.get("question_id", "q1"), "value": "I feel stressed about work deadlines", "type": "text"},
                {"question_id": "stress_q2", "value": "7", "type": "scale"},
                {"question_id": "stress_q3", "value": "Sometimes I feel overwhelmed", "type": "text"}
            ]
            
            for i, response_data in enumerate(test_responses):
                response_payload = {
                    "response": response_data["value"],
                    "question_id": response_data["question_id"]
                }
                
                response = requests.post(
                f"{BASE_URL}/api/v1/chat/assessment/respond",
                json=response_payload,
                headers={"Content-Type": "application/json"}
            )
                
                if response.status_code == 200:
                    result = response.json()
                    self.assessment_responses.append(result)
                    
                    if result.get("is_complete"):
                        self.log_test(
                            "Assessment Response Handling", 
                            "PASS", 
                            f"Assessment completed after {i+1} responses"
                        )
                        return True
                else:
                    self.log_test(
                        "Assessment Response Handling", 
                        "FAIL", 
                        f"Response {i+1} failed with status {response.status_code}"
                    )
                    return False
            
            self.log_test(
                "Assessment Response Handling", 
                "PASS", 
                f"Processed {len(test_responses)} responses successfully"
            )
            return True
            
        except Exception as e:
            self.log_test(
                "Assessment Response Handling", 
                "FAIL", 
                f"Exception: {str(e)}"
            )
            return False
    
    async def test_assessment_recommendations(self):
        """Test assessment recommendations generation"""
        self.log_test("Assessment Recommendations", "RUNNING")
        
        try:
            # Get recommendations based on stress assessment
            recommendations_payload = {
                "message": "I feel stressed about work deadlines and have trouble sleeping. I need help managing my stress levels."
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/chat/assessment/recommendations",
                json=recommendations_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                recommendations = result.get("recommendations", [])
                
                if len(recommendations) > 0:
                    self.log_test(
                        "Assessment Recommendations", 
                        "PASS", 
                        f"Generated {len(recommendations)} recommendations"
                    )
                    return recommendations
                else:
                    self.log_test(
                        "Assessment Recommendations", 
                        "FAIL", 
                        "No recommendations generated"
                    )
                    return []
            else:
                self.log_test(
                    "Assessment Recommendations", 
                    "FAIL", 
                    f"API returned status {response.status_code}: {response.text}"
                )
                return []
                
        except Exception as e:
            self.log_test(
                "Assessment Recommendations", 
                "FAIL", 
                f"Exception: {str(e)}"
            )
            return []
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*60)
        print("STRESS ASSESSMENT FLOW TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        skipped_tests = len([r for r in self.test_results if r["status"] == "SKIP"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Skipped: {skipped_tests} ⏭️")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDetailed Results:")
        print("-" * 60)
        for result in self.test_results:
            status_emoji = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⏭️"
            print(f"[{result['timestamp']}] {status_emoji} {result['test']}: {result['status']}")
            if result["details"]:
                print(f"    {result['details']}")
        
        print("\n" + "="*60)
        
        if failed_tests == 0:
            print("🎉 ALL TESTS PASSED! The stress assessment flow is working correctly.")
        else:
            print(f"⚠️ {failed_tests} test(s) failed. Please review the issues above.")
        
        print("="*60)

async def main():
    """Main test execution function"""
    print("🧪 Starting Stress Assessment Flow Test")
    print("=" * 50)
    
    tester = StressAssessmentTester()
    
    # Test 1: Vector search for stress questions
    stress_questions = await tester.test_vector_search_stress_questions()
    
    # Test 2: Assessment initialization
    assessment_data = await tester.test_assessment_initialization()
    
    # Test 3: WebSocket assessment flow
    await tester.test_websocket_assessment_flow()
    
    # Test 4: Assessment response handling
    await tester.test_assessment_response_handling(assessment_data)
    
    # Test 5: Assessment recommendations
    await tester.test_assessment_recommendations()
    
    # Print summary
    tester.print_test_summary()

if __name__ == "__main__":
    asyncio.run(main())