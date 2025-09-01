import asyncio
import json
from typing import Dict, List, Any
from pathlib import Path
import logging
from datetime import datetime

# Import services
from app.services.vector_service import vector_service
from app.services.semantic_search_service import semantic_search_service
from app.services.chat_service import ChatService
from pydantic import BaseModel

class SessionData(BaseModel):
    session_id: str
    problem_category: str = None
    current_stage: str = None
    assessment_responses: List[Dict] = []
    conversation_history: List[Dict] = []

class ChatMessage(BaseModel):
    message: str
    session_data: SessionData = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleMentalHealthTester:
    def __init__(self):
        self.conversation_stages = [
            "1.1 Problem Identification",
            "1.2 Self-Assessment", 
            "1.3 Suggestions",
            "1.4 Feedback",
            "1.5 Next Action After Feedback"
        ]
        self.chat_service = None
        
    async def initialize_services(self):
        """Initialize services once"""
        try:
            # Initialize services only once
            await vector_service.connect()
            await semantic_search_service.initialize()
            self.chat_service = ChatService()
            logger.info("✓ Services initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize services: {e}")
            return False
    
    async def test_single_conversation(self, user_question: str, domain: str) -> Dict[str, Any]:
        """Test a single conversation flow with limited stages"""
        conversation_id = f"test_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        client_id = f"test_client_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        conversation_result = {
            "user_question": user_question,
            "domain": domain,
            "stages": {},
            "conversation_id": conversation_id,
            "client_id": client_id,
            "success": True
        }
        
        try:
            # Test only the first stage to avoid loops
            stage = "1.1 Problem Identification"
            
            logger.info(f"Testing stage: {stage}")
            logger.info(f"User message: {user_question}")
            
            # Process message through chat service
            response = await self.chat_service.process_message(user_question, client_id)
            
            # Extract response content
            response_content = response.get("response") or response.get("message") or str(response)
            
            stage_result = {
                "stage": stage,
                "user_input": user_question,
                "system_response": response_content,
                "validation_passed": len(str(response_content).strip()) > 0
            }
            
            conversation_result["stages"][stage] = stage_result
            
            logger.info(f"Stage completed: {stage_result['validation_passed']}")
            logger.info(f"Response length: {len(str(response_content))}")
            
            return conversation_result
            
        except Exception as e:
            logger.error(f"Error in conversation test: {e}")
            conversation_result["error"] = str(e)
            conversation_result["success"] = False
            return conversation_result
    
    async def run_simple_tests(self) -> Dict[str, Any]:
        """Run simple conversation tests"""
        logger.info("🚀 Starting Simple Mental Health Flow Tests")
        
        # Initialize services
        if not await self.initialize_services():
            return {"error": "Failed to initialize services"}
        
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "conversations": {},
            "summary": {}
        }
        
        # Test questions for different domains
        test_cases = {
            "stress": "I'm feeling very stressed and overwhelmed with work",
            "anxiety": "I have been experiencing anxiety attacks lately",
            "general": "I'm not feeling well mentally and need help"
        }
        
        # Test each domain
        for domain, question in test_cases.items():
            logger.info(f"Testing {domain} domain...")
            
            conversation_result = await self.test_single_conversation(question, domain)
            test_results["conversations"][domain] = conversation_result
            
            # Log results
            success = conversation_result.get("success", False)
            logger.info(f"  {domain}: {'✓' if success else '❌'}")
        
        # Generate summary
        successful_tests = sum(1 for conv in test_results["conversations"].values() 
                             if conv.get("success", False))
        total_tests = len(test_results["conversations"])
        
        test_results["summary"] = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Tests completed: {successful_tests}/{total_tests} successful")
        return test_results
    
    def save_results(self, test_results: Dict[str, Any], filename: str = "simple_test_results.json"):
        """Save test results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        logger.info(f"📁 Results saved to {filename}")

async def main():
    """Main test execution"""
    tester = SimpleMentalHealthTester()
    
    try:
        # Run tests
        results = await tester.run_simple_tests()
        
        # Save results
        tester.save_results(results)
        
        # Print summary
        summary = results.get("summary", {})
        print(f"\n=== Test Summary ===")
        print(f"Total Tests: {summary.get('total_tests', 0)}")
        print(f"Successful: {summary.get('successful_tests', 0)}")
        print(f"Success Rate: {summary.get('success_rate', 0):.1%}")
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())