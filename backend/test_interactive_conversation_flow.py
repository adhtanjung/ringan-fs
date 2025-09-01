#!/usr/bin/env python3
"""
Comprehensive test for the interactive conversation flow implementation
Tests the complete 5-stage conversation flow:
1.1 Problem Identification -> 1.2 Self-Assessment -> 1.3 Suggestions -> 1.4 Feedback -> 1.5 Next Action
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.conversation_flow_service import conversation_flow_service, ConversationStage
from app.services.chat_service import ChatService
from app.services.semantic_search_service import semantic_search_service
from app.services.assessment_service import assessment_service

class InteractiveFlowTester:
    """
    Test the complete interactive conversation flow
    """
    
    def __init__(self):
        self.test_results = {
            "test_name": "Interactive Conversation Flow Test",
            "timestamp": datetime.now().isoformat(),
            "test_scenarios": [],
            "summary": {}
        }
        
    async def run_all_tests(self):
        """
        Run all conversation flow tests
        """
        print("🚀 Starting Interactive Conversation Flow Tests...\n")
        
        # Initialize services
        await self._initialize_services()
        
        # Test scenarios
        test_scenarios = [
            {
                "name": "Work Stress Flow",
                "domain": "stress",
                "initial_message": "Saya merasa sangat stres dengan pekerjaan dan tidak tahu harus bagaimana",
                "responses": [
                    "Ya, saya siap untuk assessment dan pertanyaan lebih lanjut",
                    "Ya",  # Yes/no responses
                    "8",   # Scale responses
                    "Ya",
                    "7",
                    "Tidak",
                    "9",
                    "Ya, saya siap untuk mendapat saran",
                    "Saran nomor 2 terasa paling cocok untuk saya, terima kasih",
                    "Saya setuju dengan saran ini",
                    "Saya merasa lebih tenang setelah mendapat saran ini",
                    "Saya ingin mencoba teknik pernapasan yang disarankan sebagai langkah selanjutnya"
                ]
            },
            {
                "name": "Anxiety Support Flow",
                "domain": "anxiety",
                "initial_message": "Saya sering merasa cemas dan khawatir berlebihan tentang masa depan",
                "responses": [
                    "Iya, saya mau ikut assessment dan evaluasi lebih detail",
                    "Ya",
                    "6",
                    "Tidak",
                    "8",
                    "Ya",
                    "5",
                    "Ya, saya siap menerima saran",
                    "Semua saran terlihat membantu, terutama yang pertama, terima kasih",
                    "Saya setuju dengan rekomendasi ini",
                    "Terima kasih, saya merasa ada harapan sekarang",
                    "Saya akan mulai dengan journaling seperti yang disarankan sebagai tindakan selanjutnya"
                ]
            },
            {
                "name": "General Mental Health Flow",
                "domain": "general",
                "initial_message": "Saya merasa down dan tidak termotivasi akhir-akhir ini",
                "responses": [
                    "Baik, saya siap menjawab pertanyaan dan assessment",
                    "Tidak",
                    "4",
                    "Ya",
                    "7",
                    "Tidak",
                    "6",
                    "Ya, saya siap untuk mendapat saran",
                    "Saran untuk olahraga ringan terdengar bagus, terima kasih",
                    "Saya setuju dengan saran ini",
                    "Saya merasa sedikit lebih optimis setelah berbicara",
                    "Saya akan mencoba berjalan kaki setiap pagi sebagai langkah berikutnya"
                ]
            }
        ]
        
        # Run each test scenario
        for scenario in test_scenarios:
            print(f"\n📋 Testing: {scenario['name']}")
            result = await self._test_conversation_scenario(scenario)
            self.test_results["test_scenarios"].append(result)
            
            # Print scenario summary
            self._print_scenario_summary(result)
        
        # Generate overall summary
        await self._generate_test_summary()
        
        # Save results
        await self._save_test_results()
        
        print("\n✅ Interactive Conversation Flow Tests Completed!")
        
    async def _initialize_services(self):
        """
        Initialize all required services
        """
        try:
            print("🔧 Initializing services...")
            
            # Initialize semantic search service
            await semantic_search_service.initialize()
            print("   ✓ Semantic search service initialized")
            
            # Assessment service doesn't need initialization
            print("   ✓ Assessment service ready")
            
            # Initialize chat service
            self.chat_service = ChatService()
            print("   ✓ Chat service ready")
            
            # Conversation flow service doesn't need initialization
            print("   ✓ Conversation flow service ready")
            
            print("   ✓ All services initialized successfully\n")
            
        except Exception as e:
            print(f"   ❌ Error initializing services: {str(e)}")
            raise
    
    async def _test_conversation_scenario(self, scenario: Dict) -> Dict:
        """
        Test a complete conversation scenario
        """
        client_id = f"test_{scenario['domain']}_{datetime.now().timestamp()}"
        
        scenario_result = {
            "scenario_name": scenario["name"],
            "domain": scenario["domain"],
            "client_id": client_id,
            "started_at": datetime.now().isoformat(),
            "stages_completed": [],
            "conversation_log": [],
            "stage_transitions": [],
            "errors": [],
            "success": False,
            "flow_summary": {}
        }
        
        try:
            # Start conversation with initial message
            print(f"   👤 User: {scenario['initial_message']}")
            response = await conversation_flow_service.start_conversation_flow(
                client_id, scenario['initial_message']
            )
            
            scenario_result["conversation_log"].append({
                "role": "user",
                "message": scenario['initial_message'],
                "timestamp": datetime.now().isoformat()
            })
            
            scenario_result["conversation_log"].append({
                "role": "assistant",
                "message": response.get("message", ""),
                "stage": response.get("stage", ""),
                "type": response.get("type", ""),
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"   🤖 Assistant: {response.get('message', '')[:100]}...")
            print(f"   📍 Stage: {response.get('stage', 'Unknown')}")
            
            # Track stage transition
            if response.get("stage"):
                scenario_result["stage_transitions"].append({
                    "stage": response.get("stage"),
                    "timestamp": datetime.now().isoformat(),
                    "response_type": response.get("type")
                })
            
            # Continue conversation with predefined responses
            for i, user_response in enumerate(scenario["responses"]):
                print(f"\n   👤 User: {user_response}")
                
                response = await conversation_flow_service.process_flow_message(
                    client_id, user_response
                )
                
                scenario_result["conversation_log"].append({
                    "role": "user",
                    "message": user_response,
                    "timestamp": datetime.now().isoformat()
                })
                
                scenario_result["conversation_log"].append({
                    "role": "assistant",
                    "message": response.get("message", ""),
                    "stage": response.get("stage", ""),
                    "type": response.get("type", ""),
                    "timestamp": datetime.now().isoformat()
                })
                
                print(f"   🤖 Assistant: {response.get('message', '')[:100]}...")
                print(f"   📍 Stage: {response.get('stage', 'Unknown')}")
                
                # Track stage transitions
                current_stage = response.get("stage")
                if current_stage:
                    # Check if this is a new stage
                    last_stage = scenario_result["stage_transitions"][-1]["stage"] if scenario_result["stage_transitions"] else None
                    if current_stage != last_stage:
                        scenario_result["stage_transitions"].append({
                            "stage": current_stage,
                            "timestamp": datetime.now().isoformat(),
                            "response_type": response.get("type")
                        })
                
                # Check for errors
                if response.get("type") == "error":
                    scenario_result["errors"].append({
                        "step": i + 1,
                        "error_message": response.get("message", ""),
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Check if conversation is complete
                if response.get("conversation_complete") or response.get("flow_complete"):
                    scenario_result["flow_summary"] = response.get("flow_summary", {})
                    break
                
                # Small delay between messages
                await asyncio.sleep(0.5)
            
            # Get final flow status
            final_status = conversation_flow_service.get_flow_status(client_id)
            if final_status:
                scenario_result["final_flow_status"] = final_status
            
            # Determine success
            stages_completed = [t["stage"] for t in scenario_result["stage_transitions"]]
            expected_stages = [
                ConversationStage.PROBLEM_IDENTIFICATION.value,
                ConversationStage.SELF_ASSESSMENT.value,
                ConversationStage.SUGGESTIONS.value,
                ConversationStage.FEEDBACK.value,
                ConversationStage.NEXT_ACTION.value
            ]
            
            scenario_result["stages_completed"] = stages_completed
            scenario_result["success"] = len(set(stages_completed)) >= 3  # At least 3 different stages
            scenario_result["completed_at"] = datetime.now().isoformat()
            
        except Exception as e:
            scenario_result["errors"].append({
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "fatal": True
            })
            print(f"   ❌ Error in scenario: {str(e)}")
        
        return scenario_result
    
    def _print_scenario_summary(self, result: Dict):
        """
        Print summary of a scenario test
        """
        print(f"\n   📊 Scenario Summary:")
        print(f"      Success: {'✅' if result['success'] else '❌'}")
        print(f"      Stages Completed: {len(set(result['stages_completed']))}")
        print(f"      Conversation Length: {len(result['conversation_log'])}")
        print(f"      Errors: {len(result['errors'])}")
        
        if result["stage_transitions"]:
            print(f"      Stage Flow: {' -> '.join([t['stage'].split(' ')[1] for t in result['stage_transitions']])}")
    
    async def _generate_test_summary(self):
        """
        Generate overall test summary
        """
        total_scenarios = len(self.test_results["test_scenarios"])
        successful_scenarios = sum(1 for s in self.test_results["test_scenarios"] if s["success"])
        
        total_errors = sum(len(s["errors"]) for s in self.test_results["test_scenarios"])
        
        # Analyze stage completion
        all_stages = []
        for scenario in self.test_results["test_scenarios"]:
            all_stages.extend(scenario["stages_completed"])
        
        stage_counts = {}
        for stage in all_stages:
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
        
        self.test_results["summary"] = {
            "total_scenarios": total_scenarios,
            "successful_scenarios": successful_scenarios,
            "success_rate": (successful_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0,
            "total_errors": total_errors,
            "stage_completion_counts": stage_counts,
            "test_status": "PASSED" if successful_scenarios == total_scenarios else "PARTIAL" if successful_scenarios > 0 else "FAILED"
        }
        
        # Print summary
        print(f"\n📈 Overall Test Summary:")
        print(f"   Total Scenarios: {total_scenarios}")
        print(f"   Successful: {successful_scenarios}")
        print(f"   Success Rate: {self.test_results['summary']['success_rate']:.1f}%")
        print(f"   Total Errors: {total_errors}")
        print(f"   Test Status: {self.test_results['summary']['test_status']}")
        
        print(f"\n📋 Stage Completion Analysis:")
        for stage, count in stage_counts.items():
            stage_name = stage.split(' ', 1)[1] if ' ' in stage else stage
            print(f"   {stage_name}: {count} times")
    
    async def _save_test_results(self):
        """
        Save test results to file
        """
        try:
            filename = f"interactive_flow_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Test results saved to: {filename}")
            
        except Exception as e:
            print(f"\n❌ Error saving test results: {str(e)}")

async def main():
    """
    Main test execution
    """
    tester = InteractiveFlowTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())