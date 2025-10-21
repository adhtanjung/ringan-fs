#!/usr/bin/env python3
"""
Comprehensive Assessment Workflow Test
Tests the complete mental health assessment system end-to-end
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List
import aiohttp
import sys

class AssessmentWorkflowTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.test_results = {
            "start_time": datetime.now().isoformat(),
            "tests": [],
            "summary": {}
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_health_check(self) -> bool:
        """Test backend health check"""
        print("🔍 Testing backend health check...")
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"✅ Health check passed: {health_data['status']}")
                    self.test_results["tests"].append({
                        "test": "health_check",
                        "status": "passed",
                        "details": health_data
                    })
                    return True
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

    async def test_semantic_search(self) -> bool:
        """Test semantic search functionality"""
        print("🔍 Testing semantic search...")
        try:
            search_data = {
                "query": "I feel anxious about work",
                "collection": "mental-health-problems",
                "limit": 3,
                "score_threshold": 0.3
            }

            async with self.session.post(
                f"{self.base_url}/api/v1/vector/search",
                json=search_data
            ) as response:
                if response.status == 200:
                    search_results = await response.json()
                    if search_results.get("success") and search_results.get("results"):
                        print(f"✅ Semantic search passed: Found {len(search_results['results'])} results")
                        self.test_results["tests"].append({
                            "test": "semantic_search",
                            "status": "passed",
                            "details": {
                                "results_count": len(search_results["results"]),
                                "query_time": search_results.get("query_time", 0)
                            }
                        })
                        return True
                    else:
                        print("❌ Semantic search failed: No results found")
                        return False
                else:
                    print(f"❌ Semantic search failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Semantic search error: {e}")
            return False

    async def test_assessment_start(self, user_id: str = "test_user_workflow") -> Dict[str, Any]:
        """Test starting an assessment"""
        print("🔍 Testing assessment start...")
        try:
            start_data = {
                "user_id": user_id,
                "problem_category": "stress"
            }

            async with self.session.post(
                f"{self.base_url}/api/v1/assessment/start",
                json=start_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        print("✅ Assessment start passed")
                        self.test_results["tests"].append({
                            "test": "assessment_start",
                            "status": "passed",
                            "details": result["data"]
                        })
                        return result["data"]
                    else:
                        print("❌ Assessment start failed: No success response")
                        return {}
                else:
                    print(f"❌ Assessment start failed: {response.status}")
                    return {}
        except Exception as e:
            print(f"❌ Assessment start error: {e}")
            return {}

    async def test_assessment_submit(self, user_id: str, answer: str) -> Dict[str, Any]:
        """Test submitting an assessment answer"""
        print(f"🔍 Testing assessment submit with answer: '{answer[:50]}...'")
        try:
            submit_data = {
                "user_id": user_id,
                "answer": answer
            }

            async with self.session.post(
                f"{self.base_url}/api/v1/assessment/submit",
                json=submit_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        print("✅ Assessment submit passed")
                        self.test_results["tests"].append({
                            "test": "assessment_submit",
                            "status": "passed",
                            "details": result["data"]
                        })
                        return result["data"]
                    else:
                        print("❌ Assessment submit failed: No success response")
                        return {}
                else:
                    print(f"❌ Assessment submit failed: {response.status}")
                    return {}
        except Exception as e:
            print(f"❌ Assessment submit error: {e}")
            return {}

    async def test_assessment_status(self, user_id: str) -> Dict[str, Any]:
        """Test getting assessment status"""
        print("🔍 Testing assessment status...")
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/assessment/status/{user_id}"
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        print("✅ Assessment status passed")
                        self.test_results["tests"].append({
                            "test": "assessment_status",
                            "status": "passed",
                            "details": result["data"]
                        })
                        return result["data"]
                    else:
                        print("❌ Assessment status failed: No success response")
                        return {}
                else:
                    print(f"❌ Assessment status failed: {response.status}")
                    return {}
        except Exception as e:
            print(f"❌ Assessment status error: {e}")
            return {}

    async def test_chat_with_assessment_context(self, message: str) -> Dict[str, Any]:
        """Test chat with assessment context"""
        print(f"🔍 Testing chat with message: '{message[:50]}...'")
        try:
            chat_data = {
                "message": message,
                "session_data": {
                    "preferredLanguage": "en",
                    "client_id": "test_workflow_client"
                },
                "use_flow": True,
                "flow_mode": "flow"
            }

            async with self.session.post(
                f"{self.base_url}/api/v1/chat/chat",
                json=chat_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Chat test passed")
                    self.test_results["tests"].append({
                        "test": "chat_with_context",
                        "status": "passed",
                        "details": {
                            "message_length": len(result.get("message", "")),
                            "has_semantic_context": len(result.get("semantic_context", [])) > 0,
                            "has_assessment_recommendations": bool(result.get("assessment_recommendations"))
                        }
                    })
                    return result
                else:
                    print(f"❌ Chat test failed: {response.status}")
                    return {}
        except Exception as e:
            print(f"❌ Chat test error: {e}")
            return {}

    async def test_chat_streaming(self, message: str) -> bool:
        """Test chat streaming functionality"""
        print(f"🔍 Testing chat streaming with message: '{message[:50]}...'")
        try:
            chat_data = {
                "message": message,
                "session_data": {
                    "preferredLanguage": "en",
                    "client_id": "test_streaming_client"
                }
            }

            async with self.session.post(
                f"{self.base_url}/api/v1/chat/chat/stream",
                json=chat_data
            ) as response:
                if response.status == 200:
                    chunks_received = 0
                    async for line in response.content:
                        if line:
                            chunks_received += 1
                            if chunks_received >= 3:  # Test with first few chunks
                                break

                    if chunks_received > 0:
                        print(f"✅ Chat streaming passed: Received {chunks_received} chunks")
                        self.test_results["tests"].append({
                            "test": "chat_streaming",
                            "status": "passed",
                            "details": {"chunks_received": chunks_received}
                        })
                        return True
                    else:
                        print("❌ Chat streaming failed: No chunks received")
                        return False
                else:
                    print(f"❌ Chat streaming failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Chat streaming error: {e}")
            return False

    async def run_comprehensive_test(self):
        """Run comprehensive assessment workflow test"""
        print("🚀 Starting Comprehensive Assessment Workflow Test")
        print("=" * 60)

        # Test 1: Health Check
        health_ok = await self.test_health_check()
        if not health_ok:
            print("❌ Backend health check failed. Aborting tests.")
            return

        # Test 2: Semantic Search
        search_ok = await self.test_semantic_search()

        # Test 3: Assessment Workflow
        user_id = f"test_user_{int(time.time())}"

        # Start assessment
        assessment_data = await self.test_assessment_start(user_id)
        if not assessment_data:
            print("❌ Assessment start failed. Skipping assessment tests.")
        else:
            # Submit answer
            answer = "I feel overwhelmed with work deadlines and have trouble sleeping at night"
            submit_result = await self.test_assessment_submit(user_id, answer)

            # Check status
            status_result = await self.test_assessment_status(user_id)

        # Test 4: Chat with Assessment Context
        chat_message = "I need help with anxiety and stress management"
        chat_result = await self.test_chat_with_assessment_context(chat_message)

        # Test 5: Chat Streaming
        streaming_ok = await self.test_chat_streaming(chat_message)

        # Generate summary
        self.test_results["end_time"] = datetime.now().isoformat()
        self.test_results["summary"] = {
            "total_tests": len(self.test_results["tests"]),
            "passed_tests": len([t for t in self.test_results["tests"] if t["status"] == "passed"]),
            "failed_tests": len([t for t in self.test_results["tests"] if t["status"] == "failed"]),
            "success_rate": len([t for t in self.test_results["tests"] if t["status"] == "passed"]) / len(self.test_results["tests"]) * 100 if self.test_results["tests"] else 0
        }

        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.test_results['summary']['total_tests']}")
        print(f"Passed: {self.test_results['summary']['passed_tests']}")
        print(f"Failed: {self.test_results['summary']['failed_tests']}")
        print(f"Success Rate: {self.test_results['summary']['success_rate']:.1f}%")

        # Save results
        results_file = f"assessment_workflow_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n📄 Detailed results saved to: {results_file}")

        return self.test_results

async def main():
    """Main test function"""
    async with AssessmentWorkflowTester() as tester:
        results = await tester.run_comprehensive_test()

        # Exit with appropriate code
        if results["summary"]["success_rate"] >= 80:
            print("\n🎉 Assessment workflow test PASSED!")
            sys.exit(0)
        else:
            print("\n❌ Assessment workflow test FAILED!")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())













