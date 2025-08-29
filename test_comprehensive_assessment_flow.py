#!/usr/bin/env python3
"""
Comprehensive Assessment Flow Test Suite

This test suite evaluates the assessment flow within the chat interface with focus on:
1. Semantic relevance of dataset-based responses
2. Accuracy and appropriateness of responses
3. Seamless integration of assessment flow within chat interaction
4. Functional correctness and semantic accuracy
"""

import asyncio
import websockets
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import os
from difflib import SequenceMatcher
import re

class ComprehensiveAssessmentFlowTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.ws_url = "ws://localhost:8000/api/v1/chat/ws/chat/stream"
        self.ws_url_fallback = "ws://localhost:8000/api/v1/chat/ws/test_client"
        self.test_results = []
        self.session_data = {}
        self.datasets = {}
        self.semantic_test_cases = []
        
    def load_datasets(self):
        """Load and prepare datasets for testing"""
        dataset_files = {
            'anxiety': 'd:/AITek/ringan-landing/backend/data/anxiety.xlsx',
            'stress': 'd:/AITek/ringan-landing/backend/data/stress.xlsx', 
            'trauma': 'd:/AITek/ringan-landing/backend/data/trauma.xlsx'
        }
        
        for category, file_path in dataset_files.items():
            try:
                df = pd.read_excel(file_path)
                self.datasets[category] = df.to_dict('records')
                self.log_test_result(f"Dataset Load - {category}", "PASS", 
                                   f"Loaded {len(df)} records")
            except Exception as e:
                self.log_test_result(f"Dataset Load - {category}", "FAIL", 
                                   f"Failed to load: {e}")
                
    def prepare_semantic_test_cases(self):
        """Prepare comprehensive test cases for semantic evaluation"""
        self.semantic_test_cases = [
            # Anxiety-related test cases
            {
                "category": "anxiety",
                "user_message": "I can't stop worrying about my upcoming presentation. My heart races and I feel like I can't breathe.",
                "expected_keywords": ["anxiety", "worry", "presentation", "panic", "breathing"],
                "expected_problem_types": ["Social Anxiety", "Performance Anxiety"],
                "assessment_trigger": True,
                "severity_level": "moderate"
            },
            {
                "category": "anxiety", 
                "user_message": "Every time I have to take a test, I freeze up completely. I study hard but then blank out during exams.",
                "expected_keywords": ["test", "exam", "freeze", "blank", "study"],
                "expected_problem_types": ["Exam/ test anxiety"],
                "assessment_trigger": True,
                "severity_level": "high"
            },
            {
                "category": "anxiety",
                "user_message": "I'm starting college next month and I'm terrified about leaving home and making new friends.",
                "expected_keywords": ["college", "leaving home", "new friends", "terrified"],
                "expected_problem_types": ["Transition/ adjustment anxiety"],
                "assessment_trigger": True,
                "severity_level": "moderate"
            },
            
            # Stress-related test cases
            {
                "category": "stress",
                "user_message": "My relationship is falling apart and I don't know how to fix it. We fight constantly.",
                "expected_keywords": ["relationship", "falling apart", "fight", "constantly"],
                "expected_problem_types": ["Stress from Relationships"],
                "assessment_trigger": True,
                "severity_level": "high"
            },
            {
                "category": "stress",
                "user_message": "My parents are always criticizing me and nothing I do is ever good enough for them.",
                "expected_keywords": ["parents", "criticizing", "not good enough"],
                "expected_problem_types": ["Stress from Family Relations"],
                "assessment_trigger": True,
                "severity_level": "moderate"
            },
            {
                "category": "stress",
                "user_message": "There's this group at school that keeps picking on me and making my life miserable.",
                "expected_keywords": ["school", "picking on", "miserable", "group"],
                "expected_problem_types": ["Stress from Bullying"],
                "assessment_trigger": True,
                "severity_level": "high"
            },
            
            # Trauma-related test cases
            {
                "category": "trauma",
                "user_message": "I keep having nightmares about the car accident. I can't drive anymore without panicking.",
                "expected_keywords": ["nightmares", "car accident", "drive", "panicking"],
                "expected_problem_types": ["Acute Trauma", "PTSD"],
                "assessment_trigger": True,
                "severity_level": "high"
            },
            {
                "category": "trauma",
                "user_message": "Since moving to this new city, I feel completely lost and can't adjust to anything.",
                "expected_keywords": ["moving", "new city", "lost", "adjust"],
                "expected_problem_types": ["Adjustment Disorder"],
                "assessment_trigger": True,
                "severity_level": "moderate"
            },
            
            # Edge cases and mixed scenarios
            {
                "category": "mixed",
                "user_message": "I'm stressed about work, anxious about my relationship, and still dealing with trauma from my childhood.",
                "expected_keywords": ["stressed", "work", "anxious", "relationship", "trauma", "childhood"],
                "expected_problem_types": ["Stress", "Anxiety", "Trauma"],
                "assessment_trigger": True,
                "severity_level": "high",
                "multiple_categories": True
            },
            {
                "category": "general",
                "user_message": "I just want to chat about my day. Nothing serious, just had a good time with friends.",
                "expected_keywords": ["chat", "day", "good time", "friends"],
                "expected_problem_types": [],
                "assessment_trigger": False,
                "severity_level": "none"
            }
        ]
        
    def log_test_result(self, test_name: str, status: str, details: str = "", data: Any = None):
        """Log test results with timestamp"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "test_name": test_name,
            "status": status,
            "details": details,
            "data": data
        }
        self.test_results.append(result)
        
        # Print with emoji indicators
        emoji = "✓" if status == "PASS" else "✗" if status == "FAIL" else "⚠" if status == "WARN" else "ℹ"
        print(f"{emoji} {test_name}: {status} - {details}")
        
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        
    def extract_keywords_from_response(self, response: str) -> List[str]:
        """Extract meaningful keywords from response"""
        # Remove common words and extract meaningful terms
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        words = re.findall(r'\b\w+\b', response.lower())
        return [word for word in words if word not in common_words and len(word) > 2]
        
    async def test_backend_health(self):
        """Test backend health and readiness"""
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
            
    async def test_websocket_connection(self):
        """Test WebSocket connection with fallback"""
        # Try streaming endpoint first
        try:
            async with websockets.connect(self.ws_url) as websocket:
                self.log_test_result("WebSocket Connection", "PASS", "Connected to streaming endpoint")
                return True
        except Exception as e:
            self.log_test_result("WebSocket Connection (Streaming)", "WARN", f"Streaming failed: {e}")
            
        # Try fallback endpoint
        try:
            async with websockets.connect(self.ws_url_fallback) as websocket:
                self.log_test_result("WebSocket Connection", "PASS", "Connected to basic endpoint")
                self.ws_url = self.ws_url_fallback
                return True
        except Exception as e:
            self.log_test_result("WebSocket Connection", "FAIL", f"Both endpoints failed: {e}")
            return False
            
    async def test_semantic_relevance_and_accuracy(self):
        """Test semantic relevance and accuracy of responses"""
        for i, test_case in enumerate(self.semantic_test_cases):
            test_name = f"Semantic Test {i+1} ({test_case['category']})"
            
            try:
                async with websockets.connect(self.ws_url) as websocket:
                    # Send message
                    message_data = {
                        "message": test_case["user_message"],
                        "session_data": {},
                        "semantic_context": [],
                        "problem_category": None,
                        "assessment_progress": None
                    }
                    
                    await websocket.send(json.dumps(message_data))
                    
                    # Collect streaming response
                    full_response = ""
                    context_analysis = None
                    assessment_data = None
                    chunks_received = 0
                    
                    timeout_start = time.time()
                    while time.time() - timeout_start < 45.0:
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                            data = json.loads(response)
                            chunks_received += 1
                            
                            if data.get('type') == 'chunk':
                                full_response += data.get('content', '')
                            elif data.get('type') == 'complete':
                                full_response += data.get('content', '')
                                context_analysis = data.get('context_analysis')
                                assessment_data = data.get('assessment_data')
                                break
                            elif 'context_analysis' in data:
                                context_analysis = data['context_analysis']
                                
                        except asyncio.TimeoutError:
                            continue
                        except json.JSONDecodeError:
                            continue
                    
                    # Evaluate semantic relevance
                    await self.evaluate_semantic_relevance(test_case, full_response, context_analysis, test_name)
                    
                    # Evaluate response accuracy
                    await self.evaluate_response_accuracy(test_case, full_response, context_analysis, test_name)
                    
                    # Evaluate assessment integration
                    await self.evaluate_assessment_integration(test_case, assessment_data, context_analysis, test_name)
                    
            except Exception as e:
                self.log_test_result(f"{test_name} - Error", "FAIL", f"Exception: {e}")
                
    async def evaluate_semantic_relevance(self, test_case: Dict, response: str, context_analysis: Dict, test_name: str):
        """Evaluate semantic relevance of the response"""
        if not response:
            self.log_test_result(f"{test_name} - Semantic Relevance", "FAIL", "No response received")
            return
            
        # Check keyword presence
        response_keywords = self.extract_keywords_from_response(response)
        expected_keywords = test_case.get('expected_keywords', [])
        
        keyword_matches = 0
        for keyword in expected_keywords:
            if any(keyword.lower() in resp_keyword.lower() or resp_keyword.lower() in keyword.lower() 
                  for resp_keyword in response_keywords):
                keyword_matches += 1
                
        keyword_relevance = keyword_matches / len(expected_keywords) if expected_keywords else 0
        
        # Check context analysis relevance
        context_relevance = 0
        if context_analysis:
            detected_category = (context_analysis.get('primary_category') or '').lower()
            expected_category = test_case.get('category', '').lower()
            
            if expected_category in detected_category or detected_category in expected_category:
                context_relevance = 1.0
            elif test_case.get('multiple_categories', False):
                # For mixed cases, check if any category is detected
                context_relevance = 0.7 if detected_category else 0
                
        # Overall semantic relevance score
        semantic_score = (keyword_relevance * 0.6) + (context_relevance * 0.4)
        
        if semantic_score >= 0.7:
            self.log_test_result(f"{test_name} - Semantic Relevance", "PASS", 
                               f"Score: {semantic_score:.2f}, Keywords: {keyword_matches}/{len(expected_keywords)}")
        elif semantic_score >= 0.4:
            self.log_test_result(f"{test_name} - Semantic Relevance", "WARN", 
                               f"Score: {semantic_score:.2f}, Keywords: {keyword_matches}/{len(expected_keywords)}")
        else:
            self.log_test_result(f"{test_name} - Semantic Relevance", "FAIL", 
                               f"Score: {semantic_score:.2f}, Keywords: {keyword_matches}/{len(expected_keywords)}")
                               
    async def evaluate_response_accuracy(self, test_case: Dict, response: str, context_analysis: Dict, test_name: str):
        """Evaluate accuracy and appropriateness of responses"""
        if not response:
            self.log_test_result(f"{test_name} - Response Accuracy", "FAIL", "No response to evaluate")
            return
            
        # Check response length and structure
        response_length = len(response.strip())
        if response_length < 50:
            self.log_test_result(f"{test_name} - Response Accuracy", "WARN", 
                               f"Response too short: {response_length} chars")
            return
            
        # Check for appropriate tone and content
        inappropriate_indicators = ['ignore', 'dismiss', 'not important', 'don\'t worry about it']
        supportive_indicators = ['understand', 'support', 'help', 'care', 'listen', 'here for you']
        
        inappropriate_count = sum(1 for indicator in inappropriate_indicators 
                                if indicator in response.lower())
        supportive_count = sum(1 for indicator in supportive_indicators 
                             if indicator in response.lower())
        
        # Check for problem-specific accuracy
        problem_accuracy = 0
        expected_problems = test_case.get('expected_problem_types', [])
        if expected_problems and context_analysis:
            detected_problems = context_analysis.get('detected_problems', [])
            if isinstance(detected_problems, list):
                for expected in expected_problems:
                    if any(expected.lower() in detected.lower() for detected in detected_problems):
                        problem_accuracy += 1
                problem_accuracy = problem_accuracy / len(expected_problems)
                
        # Calculate accuracy score
        accuracy_score = 0
        if inappropriate_count == 0:  # No inappropriate content
            accuracy_score += 0.3
        if supportive_count > 0:  # Contains supportive language
            accuracy_score += 0.4
        accuracy_score += problem_accuracy * 0.3  # Problem identification accuracy
        
        if accuracy_score >= 0.7:
            self.log_test_result(f"{test_name} - Response Accuracy", "PASS", 
                               f"Score: {accuracy_score:.2f}, Supportive: {supportive_count > 0}")
        elif accuracy_score >= 0.4:
            self.log_test_result(f"{test_name} - Response Accuracy", "WARN", 
                               f"Score: {accuracy_score:.2f}, Supportive: {supportive_count > 0}")
        else:
            self.log_test_result(f"{test_name} - Response Accuracy", "FAIL", 
                               f"Score: {accuracy_score:.2f}, Issues detected")
                               
    async def evaluate_assessment_integration(self, test_case: Dict, assessment_data: Dict, context_analysis: Dict, test_name: str):
        """Evaluate seamless integration of assessment flow"""
        should_trigger_assessment = test_case.get('assessment_trigger', False)
        
        if should_trigger_assessment:
            # Check if assessment was suggested or context analysis detected problems
            assessment_suggested = bool(
                assessment_data or 
                (context_analysis and context_analysis.get('assessment_recommended')) or
                (context_analysis and context_analysis.get('should_suggest_assessment')) or
                (context_analysis and context_analysis.get('detected_problems'))
            )
            
            if assessment_suggested:
                self.log_test_result(f"{test_name} - Assessment Integration", "PASS", 
                                   "Assessment appropriately suggested")
                
                # Check assessment data quality if available
                if assessment_data:
                    await self.evaluate_assessment_data_quality(test_case, assessment_data, test_name)
            else:
                # For single message tests, assessment might not be triggered immediately
                # This is expected behavior based on backend logic
                self.log_test_result(f"{test_name} - Assessment Integration", "WARN", 
                                   "Assessment not triggered (may require conversation history)")
        else:
            # Check that assessment wasn't inappropriately triggered
            assessment_triggered = bool(assessment_data)
            
            if not assessment_triggered:
                self.log_test_result(f"{test_name} - Assessment Integration", "PASS", 
                                   "Assessment correctly not triggered")
            else:
                self.log_test_result(f"{test_name} - Assessment Integration", "WARN", 
                                   "Assessment triggered when it shouldn't have been")
                                   
    async def evaluate_assessment_data_quality(self, test_case: Dict, assessment_data: Dict, test_name: str):
        """Evaluate quality of assessment data"""
        required_fields = ['session_id', 'problem_category', 'current_question']
        missing_fields = [field for field in required_fields if not assessment_data.get(field)]
        
        if not missing_fields:
            self.log_test_result(f"{test_name} - Assessment Data Quality", "PASS", 
                               "All required fields present")
        else:
            self.log_test_result(f"{test_name} - Assessment Data Quality", "WARN", 
                               f"Missing fields: {missing_fields}")
                               
    async def test_dataset_response_integration(self):
        """Test integration with actual dataset responses"""
        for category, dataset in self.datasets.items():
            if not dataset:
                continue
                
            # Test with first few problems from each dataset
            for i, problem in enumerate(dataset[:3]):
                test_name = f"Dataset Integration - {category} Problem {i+1}"
                
                try:
                    # Start assessment for this category
                    response = requests.post(f"{self.base_url}/api/v1/chat/assessment/start", 
                                           json={"problem_category": category})
                    
                    if response.status_code == 200:
                        assessment_data = response.json()
                        session_id = assessment_data.get('session_id')
                        question = assessment_data.get('question')
                        
                        if session_id and question:
                            # Verify question matches dataset
                            problem_name = problem.get('problem_name', '')
                            description = problem.get('description', '')
                            
                            # Handle question - it might be a dict or string
                            if isinstance(question, dict):
                                question_text = question.get('question_text', '') or question.get('question', '') or question.get('text', '') or str(question)
                            else:
                                question_text = str(question)
                            
                            # Safely convert to string and handle None values
                            problem_name_str = str(problem_name) if problem_name is not None else ''
                            description_str = str(description) if description is not None else ''
                            
                            # Check if question relates to the problem
                            problem_words = problem_name_str.lower().split() if problem_name_str else []
                            description_words = description_str.lower().split()[:5] if description_str else []
                            
                            question_relevance = (
                                any(word in question_text.lower() for word in problem_words) or
                                any(word in question_text.lower() for word in description_words)
                            )
                            
                            if question_relevance:
                                self.log_test_result(test_name, "PASS", 
                                                   f"Question relevant to {problem_name_str}")
                            else:
                                self.log_test_result(test_name, "WARN", 
                                                   f"Question may not be relevant to {problem_name_str}")
                        else:
                            self.log_test_result(test_name, "FAIL", "Missing session_id or question")
                    else:
                        self.log_test_result(test_name, "FAIL", f"API error: {response.status_code}")
                        
                except Exception as e:
                    self.log_test_result(test_name, "FAIL", f"Error: {e}")
                    
    async def test_end_to_end_assessment_flow(self):
        """Test complete end-to-end assessment flow"""
        test_scenario = {
            "user_message": "I've been having panic attacks before every exam. My heart races and I can't think straight.",
            "expected_category": "anxiety",
            "expected_flow": ["context_analysis", "assessment_start", "question_progression", "completion"]
        }
        
        # First test multi-conversation flow to trigger assessment
        await self.test_multi_conversation_assessment_trigger()
        
        # Then test direct assessment start
        
        try:
            async with websockets.connect(self.ws_url) as websocket:
                # Step 1: Send initial message
                message_data = {
                    "message": test_scenario["user_message"],
                    "session_data": {},
                    "semantic_context": [],
                    "problem_category": None,
                    "assessment_progress": None
                }
                
                await websocket.send(json.dumps(message_data))
                
                # Collect response and check for assessment trigger
                context_analysis = None
                assessment_recommended = False
                
                timeout_start = time.time()
                while time.time() - timeout_start < 30.0:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        data = json.loads(response)
                        
                        if 'context_analysis' in data:
                            context_analysis = data['context_analysis']
                        if data.get('type') == 'complete':
                            context_analysis = data.get('context_analysis', context_analysis)
                            assessment_recommended = data.get('assessment_recommended', False)
                            break
                            
                    except (asyncio.TimeoutError, json.JSONDecodeError):
                        continue
                
                # Verify context analysis
                if context_analysis:
                    detected_category = (context_analysis.get('primary_category') or '').lower()
                    expected_category = test_scenario['expected_category'].lower()
                    
                    if expected_category in detected_category:
                        self.log_test_result("E2E Flow - Context Analysis", "PASS", 
                                           f"Correctly identified {detected_category}")
                    else:
                        self.log_test_result("E2E Flow - Context Analysis", "WARN", 
                                           f"Expected {expected_category}, got {detected_category}")
                else:
                    self.log_test_result("E2E Flow - Context Analysis", "FAIL", "No context analysis")
                
                # Step 2: Start formal assessment if context analysis detected problems
                if context_analysis and context_analysis.get('detected_problems'):
                    # Use detected category or default to anxiety for testing
                    category = context_analysis.get('primary_category', 'anxiety')
                    
                    try:
                        response = requests.post(f"{self.base_url}/api/v1/chat/assessment/start", 
                                               json={"problem_category": category},
                                               timeout=10)
                        
                        if response.status_code == 200:
                            assessment_data = response.json()
                            session_id = assessment_data.get('session_id')
                            
                            if session_id:
                                self.log_test_result("E2E Flow - Assessment Start", "PASS", 
                                                   f"Started session {session_id}")
                                
                                # Step 3: Test question progression
                                await self.test_question_progression(session_id)
                            else:
                                self.log_test_result("E2E Flow - Assessment Start", "FAIL", "No session ID")
                        else:
                            self.log_test_result("E2E Flow - Assessment Start", "FAIL", 
                                               f"API error: {response.status_code} - {response.text}")
                    except requests.RequestException as e:
                        self.log_test_result("E2E Flow - Assessment Start", "FAIL", f"Request error: {e}")
                else:
                    self.log_test_result("E2E Flow - Assessment Start", "WARN", 
                                       "No context analysis or detected problems to start assessment")
                        
        except Exception as e:
            self.log_test_result("E2E Flow - Error", "FAIL", f"Exception: {e}")
            
    async def test_multi_conversation_assessment_trigger(self):
        """Test assessment triggering through multiple conversation exchanges"""
        conversation_messages = [
            "Hi, I've been feeling really stressed lately.",
            "I can't sleep well and I'm constantly worried about everything.",
            "It's affecting my work and relationships. I feel overwhelmed.",
            "I think I need help but I don't know where to start."
        ]
        
        try:
            async with websockets.connect(self.ws_url) as websocket:
                context_analysis = None
                assessment_suggested = False
                
                for i, message in enumerate(conversation_messages):
                    message_data = {
                        "message": message,
                        "session_data": {},
                        "semantic_context": [],
                        "problem_category": None,
                        "assessment_progress": None
                    }
                    
                    await websocket.send(json.dumps(message_data))
                    
                    # Collect response
                    timeout_start = time.time()
                    while time.time() - timeout_start < 20.0:
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                            data = json.loads(response)
                            
                            if 'context_analysis' in data:
                                context_analysis = data['context_analysis']
                            if data.get('should_suggest_assessment') or data.get('is_assessment_suggestion'):
                                assessment_suggested = True
                            if data.get('type') == 'complete':
                                break
                                
                        except (asyncio.TimeoutError, json.JSONDecodeError):
                            continue
                    
                    # Check if assessment was suggested after multiple exchanges
                    if i >= 2 and (assessment_suggested or 
                                 (context_analysis and context_analysis.get('should_suggest_assessment'))):
                        self.log_test_result("Multi-Conversation Assessment Trigger", "PASS", 
                                           f"Assessment suggested after {i+1} messages")
                        return True
                        
                if not assessment_suggested:
                    self.log_test_result("Multi-Conversation Assessment Trigger", "WARN", 
                                       "Assessment not suggested after full conversation")
                return False
                
        except Exception as e:
            self.log_test_result("Multi-Conversation Assessment Trigger", "FAIL", f"Error: {e}")
            return False
            
    async def test_question_progression(self, session_id: str):
        """Test question progression within assessment"""
        try:
            # Simulate answering a few questions
            for i in range(3):
                response = requests.post(f"{self.base_url}/api/v1/chat/assessment/respond", 
                                       json={
                                           "session_id": session_id,
                                           "answer": f"Test answer {i+1}",
                                           "question_id": f"q_{i+1}"
                                       })
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('next_question'):
                        self.log_test_result(f"E2E Flow - Question {i+1}", "PASS", 
                                           "Question progression working")
                    elif data.get('assessment_complete'):
                        self.log_test_result("E2E Flow - Assessment Complete", "PASS", 
                                           "Assessment completed successfully")
                        break
                    else:
                        self.log_test_result(f"E2E Flow - Question {i+1}", "WARN", 
                                           "Unexpected response format")
                else:
                    self.log_test_result(f"E2E Flow - Question {i+1}", "FAIL", 
                                       f"API error: {response.status_code}")
                    break
                    
        except Exception as e:
            self.log_test_result("E2E Flow - Question Progression", "FAIL", f"Error: {e}")
            
    async def run_comprehensive_tests(self):
        """Run all comprehensive assessment flow tests"""
        print("\n" + "="*80)
        print("COMPREHENSIVE ASSESSMENT FLOW TEST SUITE")
        print("="*80)
        
        # Load datasets and prepare test cases
        print("\n📊 Loading Datasets and Preparing Test Cases...")
        self.load_datasets()
        self.prepare_semantic_test_cases()
        
        # Test backend health
        print("\n🏥 Testing Backend Health...")
        if not await self.test_backend_health():
            print("❌ Backend not healthy. Stopping tests.")
            return
            
        # Test WebSocket connection
        print("\n🔌 Testing WebSocket Connection...")
        if not await self.test_websocket_connection():
            print("❌ WebSocket connection failed. Stopping tests.")
            return
            
        # Run comprehensive semantic and accuracy tests
        print("\n🧠 Testing Semantic Relevance and Response Accuracy...")
        await self.test_semantic_relevance_and_accuracy()
        
        # Test dataset integration
        print("\n📋 Testing Dataset Response Integration...")
        await self.test_dataset_response_integration()
        
        # Test end-to-end assessment flow
        print("\n🔄 Testing End-to-End Assessment Flow...")
        await self.test_end_to_end_assessment_flow()
        
        # Generate comprehensive report
        self.generate_comprehensive_report()
        
    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("COMPREHENSIVE TEST REPORT")
        print("="*80)
        
        # Calculate statistics
        total_tests = len(self.test_results)
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.test_results if r['status'] == 'WARN'])
        
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 Overall Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✓ Passed: {passed}")
        print(f"   ✗ Failed: {failed}")
        print(f"   ⚠ Warnings: {warnings}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if r['status'] == 'FAIL']
        if failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"   • {test['test_name']}: {test['details']}")
                
        # Show warnings
        warning_tests = [r for r in self.test_results if r['status'] == 'WARN']
        if warning_tests:
            print(f"\n⚠️ Warnings:")
            for test in warning_tests:
                print(f"   • {test['test_name']}: {test['details']}")
                
        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"comprehensive_assessment_test_report_{timestamp}.json"
        
        report_data = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "success_rate": success_rate,
                "test_timestamp": datetime.now().isoformat()
            },
            "detailed_results": self.test_results,
            "test_cases": self.semantic_test_cases,
            "datasets_info": {k: len(v) for k, v in self.datasets.items()}
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Final assessment
        if success_rate >= 80:
            print("\n🎉 Excellent! Assessment flow is working very well.")
        elif success_rate >= 60:
            print("\n✅ Good! Assessment flow is working with minor issues.")
        elif success_rate >= 40:
            print("\n⚠️ Moderate issues detected. Review failed tests.")
        else:
            print("\n❌ Significant issues detected. Major fixes needed.")

if __name__ == "__main__":
    tester = ComprehensiveAssessmentFlowTester()
    asyncio.run(tester.run_comprehensive_tests())