#!/usr/bin/env python3
"""
WebSocket Assessment Chat Workflow Test

This script tests the complete assessment workflow via WebSocket including:
- Message transmission and real-time streaming
- Assessment question progression
- Data synchronization with dataset
- Error handling and recovery
- Context analysis and problem categorization
"""

import asyncio
import websockets
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd
import os

class WebSocketAssessmentTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.ws_url = "ws://localhost:8000/api/v1/chat/ws/chat/stream"  # Try streaming endpoint first
        self.ws_url_fallback = "ws://localhost:8000/api/v1/chat/ws/test_client"  # Fallback to basic endpoint
        self.test_results = []
        self.session_data = {}
        self.assessment_progress = {}
        self.datasets = {}
        
    def load_datasets(self):
        """Load mental health datasets for testing"""
        dataset_files = {
            'anxiety': 'backend/data/anxiety.xlsx',
            'stress': 'backend/data/stress.xlsx', 
            'trauma': 'backend/data/trauma.xlsx'
        }
        
        for category, file_path in dataset_files.items():
            try:
                if os.path.exists(file_path):
                    df = pd.read_excel(file_path)
                    self.datasets[category] = df
                    print(f"✓ Loaded {category} dataset: {len(df)} records")
                else:
                    print(f"⚠ Dataset file not found: {file_path}")
            except Exception as e:
                print(f"✗ Error loading {category} dataset: {e}")
    
    def log_test_result(self, test_name: str, status: str, details: str = "", data: Any = None):
        """Log test results with timestamp"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'test_name': test_name,
            'status': status,
            'details': details,
            'data': data
        }
        self.test_results.append(result)
        
        status_emoji = {
            'PASS': '✓',
            'FAIL': '✗', 
            'WARN': '⚠',
            'INFO': 'ℹ'
        }
        
        print(f"{status_emoji.get(status, '•')} {test_name}: {status} - {details}")
    
    async def test_websocket_connection(self):
        """Test basic WebSocket connection"""
        # Try streaming endpoint first
        try:
            async with websockets.connect(self.ws_url) as websocket:
                self.log_test_result("WebSocket Connection", "PASS", "Successfully connected to streaming WebSocket")
                return True
        except Exception as e:
            self.log_test_result("WebSocket Connection (Streaming)", "WARN", f"Streaming endpoint failed: {e}")
            
        # Try fallback endpoint
        try:
            async with websockets.connect(self.ws_url_fallback) as websocket:
                self.log_test_result("WebSocket Connection", "PASS", "Successfully connected to basic WebSocket")
                # Update URL for subsequent tests
                self.ws_url = self.ws_url_fallback
                return True
        except Exception as e:
            self.log_test_result("WebSocket Connection", "FAIL", f"Both endpoints failed. Streaming: {self.ws_url}, Basic: {self.ws_url_fallback}. Error: {e}")
            return False
    
    async def test_message_streaming(self):
        """Test real-time message streaming"""
        try:
            async with websockets.connect(self.ws_url) as websocket:
                # Send test message
                test_message = {
                    "message": "I've been feeling very anxious lately and having trouble sleeping",
                    "session_data": {},
                    "semantic_context": [],
                    "problem_category": "",
                    "assessment_progress": {}
                }
                
                await websocket.send(json.dumps(test_message))
                
                # Collect streaming response
                chunks = []
                complete_response = None
                timeout = 60  # 60 second timeout for AI processing
                start_time = time.time()
                chunk_count = 0
                
                while time.time() - start_time < timeout:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        data = json.loads(response)
                        
                        if data.get('type') == 'chunk':
                            chunk_content = data.get('content', '')
                            chunks.append(chunk_content)
                            chunk_count += 1
                            # Log progress for long responses
                            if chunk_count % 10 == 0:
                                self.log_test_result("Streaming Progress", "INFO", f"Received {chunk_count} chunks")
                        elif data.get('type') == 'complete':
                            complete_response = data
                            break
                        elif data.get('type') == 'error':
                            self.log_test_result("Message Streaming", "FAIL", f"Server error: {data.get('message')}")
                            return False
                        else:
                            # Log other message types for debugging
                            self.log_test_result("Message Type", "INFO", f"Received: {data.get('type')}")
                            
                    except asyncio.TimeoutError:
                        self.log_test_result("Streaming Timeout", "WARN", f"No response for 10s, continuing...")
                        continue
                    except json.JSONDecodeError as e:
                        self.log_test_result("JSON Parse Error", "WARN", f"Invalid JSON: {e}")
                        continue
                
                if complete_response:
                    full_text = ''.join(chunks)
                    self.log_test_result("Message Streaming", "PASS", 
                                       f"Received {len(chunks)} chunks, {len(full_text)} characters")
                    return True, complete_response
                else:
                    self.log_test_result("Message Streaming", "FAIL", "No complete response received")
                    return False, None
                    
        except Exception as e:
            self.log_test_result("Message Streaming", "FAIL", f"Streaming error: {e}")
            return False, None
    
    async def test_context_analysis(self):
        """Test AI context analysis and problem categorization"""
        test_cases = [
            {
                "message": "I can't stop worrying about everything and my heart races",
                "expected_category": "anxiety"
            },
            {
                "message": "I'm overwhelmed with work and can't handle the pressure", 
                "expected_category": "stress"
            },
            {
                "message": "I keep having flashbacks from the accident",
                "expected_category": "trauma"
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            try:
                async with websockets.connect(self.ws_url) as websocket:
                    message = {
                        "message": test_case["message"],
                        "session_data": {},
                        "semantic_context": [],
                        "problem_category": "",
                        "assessment_progress": {}
                    }
                    
                    await websocket.send(json.dumps(message))
                    
                    # Wait for complete response and collect all data
                    complete_data = None
                    context_analysis = None
                    timeout = 45
                    start_time = time.time()
                    
                    while time.time() - start_time < timeout:
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                            data = json.loads(response)
                            
                            # Look for context analysis in any chunk
                            if 'context_analysis' in data:
                                context_analysis = data['context_analysis']
                            
                            if data.get('type') == 'complete':
                                complete_data = data
                                break
                                
                        except asyncio.TimeoutError:
                            continue
                        except json.JSONDecodeError:
                            continue
                    
                    # Check context analysis from any received data
                    if context_analysis or (complete_data and 'context_analysis' in complete_data):
                        analysis_data = context_analysis or complete_data.get('context_analysis', {})
                        detected_category = (analysis_data.get('primary_category') or '').lower()
                        expected = (test_case['expected_category'] or '').lower()
                        
                        if expected in detected_category or detected_category in expected:
                            self.log_test_result(f"Context Analysis {i+1}", "PASS", 
                                               f"Correctly identified {detected_category}")
                        else:
                            self.log_test_result(f"Context Analysis {i+1}", "WARN", 
                                               f"Expected {expected}, got {detected_category}")
                    else:
                        self.log_test_result(f"Context Analysis {i+1}", "FAIL", 
                                           "No context analysis in response")
                        
            except Exception as e:
                self.log_test_result(f"Context Analysis {i+1}", "FAIL", f"Error: {e}")
    
    async def test_assessment_workflow(self):
        """Test complete assessment workflow with dataset questions"""
        try:
            # Start assessment via API
            response = requests.post(f"{self.base_url}/api/v1/chat/assessment/start", 
                                   json={"problem_category": "anxiety"})
            
            if response.status_code != 200:
                self.log_test_result("Assessment Start", "FAIL", f"API error: {response.status_code}")
                return
            
            assessment_data = response.json()
            session_id = assessment_data.get('session_id')
            first_question = assessment_data.get('question')
            
            if not session_id or not first_question:
                self.log_test_result("Assessment Start", "FAIL", "Missing session_id or question")
                return
            
            self.log_test_result("Assessment Start", "PASS", f"Session {session_id} started")
            
            # Test assessment progression via WebSocket
            async with websockets.connect(self.ws_url) as websocket:
                question_count = 0
                max_questions = 5  # Limit for testing
                
                while question_count < max_questions:
                    # Send answer via WebSocket
                    answer_message = {
                        "message": "Yes, this happens to me frequently",
                        "session_data": {
                            "assessment_session_id": session_id,
                            "current_question_id": first_question.get('id') if question_count == 0 else None
                        },
                        "semantic_context": [],
                        "problem_category": "anxiety",
                        "assessment_progress": {
                            "isActive": True,
                            "sessionId": session_id
                        }
                    }
                    
                    await websocket.send(json.dumps(answer_message))
                    
                    # Wait for response
                    while True:
                        response = await websocket.recv()
                        data = json.loads(response)
                        
                        if data.get('type') == 'complete':
                            break
                    
                    # Check for next question or completion
                    if 'assessment_questions' in data and data['assessment_questions']:
                        next_question = data['assessment_questions'][0]
                        question_count += 1
                        self.log_test_result(f"Assessment Question {question_count}", "PASS", 
                                           f"Received next question: {next_question.get('question', '')[:50]}...")
                        first_question = next_question
                    else:
                        # Assessment completed
                        self.log_test_result("Assessment Completion", "PASS", 
                                           f"Assessment completed after {question_count} questions")
                        break
                
        except Exception as e:
            self.log_test_result("Assessment Workflow", "FAIL", f"Error: {e}")
    
    async def test_error_handling(self):
        """Test error handling and recovery"""
        error_test_cases = [
            {
                "name": "Invalid JSON",
                "message": "invalid json message",
                "should_fail": True,
                "timeout": 10.0
            },
            {
                "name": "Empty Message", 
                "message": {"message": ""},
                "should_fail": True,  # Empty messages should be handled gracefully
                "timeout": 15.0
            },
            {
                "name": "Very Long Message",
                "message": {"message": "x" * 10000},
                "should_fail": False,  # Long messages should be processed
                "timeout": 30.0  # Longer timeout for processing
            }
        ]
        
        for test_case in error_test_cases:
            try:
                async with websockets.connect(self.ws_url) as websocket:
                    if test_case["name"] == "Invalid JSON":
                        await websocket.send(test_case["message"])
                    else:
                        await websocket.send(json.dumps(test_case["message"]))
                    
                    # Wait for response with custom timeout
                    timeout = test_case.get("timeout", 10.0)
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                        data = json.loads(response)
                        
                        if data.get('type') == 'error' and test_case["should_fail"]:
                            self.log_test_result(f"Error Handling - {test_case['name']}", "PASS", 
                                               "Correctly handled error")
                        elif data.get('type') != 'error' and not test_case["should_fail"]:
                            self.log_test_result(f"Error Handling - {test_case['name']}", "PASS", 
                                               "Correctly processed message")
                        else:
                            self.log_test_result(f"Error Handling - {test_case['name']}", "WARN", 
                                               f"Unexpected response type: {data.get('type')}")
                    except asyncio.TimeoutError:
                        self.log_test_result(f"Error Handling - {test_case['name']}", "FAIL", 
                                           "No response received")
                        
            except Exception as e:
                if test_case["should_fail"]:
                    self.log_test_result(f"Error Handling - {test_case['name']}", "PASS", 
                                       f"Expected error: {e}")
                else:
                    self.log_test_result(f"Error Handling - {test_case['name']}", "FAIL", 
                                       f"Unexpected error: {e}")
    
    def test_backend_health(self):
        """Test backend health and API availability"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_test_result("Backend Health", "PASS", "Backend is healthy")
                return True
            else:
                self.log_test_result("Backend Health", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Backend Health", "FAIL", f"Error: {e}")
            return False
    
    def validate_dataset_integration(self):
        """Validate that datasets are properly integrated"""
        for category, df in self.datasets.items():
            if df.empty:
                self.log_test_result(f"Dataset Validation - {category}", "FAIL", "Empty dataset")
                continue
            
            required_columns = ['category', 'problem_name', 'description']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                self.log_test_result(f"Dataset Validation - {category}", "WARN", 
                                   f"Missing columns: {missing_columns}")
            else:
                self.log_test_result(f"Dataset Validation - {category}", "PASS", 
                                   f"Valid structure with {len(df)} problems")
                # Show sample data
                sample_problems = df['problem_name'].head(3).tolist()
                self.log_test_result(f"Dataset Sample - {category}", "INFO", 
                                   f"Sample problems: {', '.join(sample_problems)}")
    
    async def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*60)
        print("WebSocket Assessment Chat Workflow Test Suite")
        print("="*60)
        
        # Load datasets
        print("\n📊 Loading Datasets...")
        self.load_datasets()
        self.validate_dataset_integration()
        
        # Test backend health
        print("\n🏥 Testing Backend Health...")
        if not self.test_backend_health():
            print("❌ Backend is not healthy. Stopping tests.")
            return
        
        # WebSocket tests
        print("\n🔌 Testing WebSocket Connection...")
        if not await self.test_websocket_connection():
            print("❌ WebSocket connection failed. Stopping tests.")
            return
        
        print("\n💬 Testing Message Streaming...")
        await self.test_message_streaming()
        
        print("\n🧠 Testing Context Analysis...")
        await self.test_context_analysis()
        
        print("\n📋 Testing Assessment Workflow...")
        await self.test_assessment_workflow()
        
        print("\n⚠️ Testing Error Handling...")
        await self.test_error_handling()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("TEST REPORT SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warned_tests = len([r for r in self.test_results if r['status'] == 'WARN'])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 Overall Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✓ Passed: {passed_tests}")
        print(f"   ✗ Failed: {failed_tests}")
        print(f"   ⚠ Warnings: {warned_tests}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test_name']}: {result['details']}")
        
        if warned_tests > 0:
            print(f"\n⚠️ Warnings:")
            for result in self.test_results:
                if result['status'] == 'WARN':
                    print(f"   • {result['test_name']}: {result['details']}")
        
        # Save detailed report
        report_file = f"websocket_assessment_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'warnings': warned_tests,
                    'success_rate': success_rate
                },
                'detailed_results': self.test_results,
                'datasets_loaded': list(self.datasets.keys()),
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        if success_rate >= 90:
            print("\n🎉 Excellent! WebSocket assessment workflow is working well.")
        elif success_rate >= 75:
            print("\n👍 Good! Minor issues detected but core functionality works.")
        else:
            print("\n⚠️ Attention needed! Multiple issues detected in the workflow.")

if __name__ == "__main__":
    tester = WebSocketAssessmentTester()
    asyncio.run(tester.run_all_tests())