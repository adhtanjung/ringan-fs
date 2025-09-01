#!/usr/bin/env python3
"""
Debug script to test the exact conversation flow scenario from the test results
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.conversation_flow_service import conversation_flow_service, ConversationStage
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_conversation_flow():
    """
    Test the exact scenario from the test results
    """
    client_id = "test_debug_client"
    
    print("=== Testing Conversation Flow Debug ===")
    
    # Step 1: Start conversation with work stress problem
    print("\n1. Starting conversation with work stress problem...")
    message1 = "Saya merasa sangat stres dengan pekerjaan saya akhir-akhir ini"
    response1 = await conversation_flow_service.start_conversation_flow(client_id, message1)
    print(f"Response 1 type: {response1.get('type')}")
    print(f"Response 1 stage: {response1.get('stage')}")
    print(f"Response 1 message: {response1.get('message')[:200]}...")
    print(f"Problems identified in response: {response1.get('identified_problems', [])}")
    
    # Check flow state after first message
    flow_status1 = conversation_flow_service.get_flow_status(client_id)
    print(f"\nFlow status after message 1:")
    print(f"  Current stage: {flow_status1.get('current_stage')}")
    print(f"  Stage progress: {flow_status1.get('stage_progress', {}).get('1.1 Problem Identification', {})}")
    if 'identified_problems' in conversation_flow_service.active_flows.get(client_id, {}):
        identified_problems = conversation_flow_service.active_flows[client_id]['identified_problems']
        print(f"  Identified problems in flow state: {len(identified_problems)} problems")
        for i, problem in enumerate(identified_problems[:2]):
            print(f"    Problem {i+1}: {problem.get('category')} - {problem.get('problem_text', '')[:50]}... (score: {problem.get('score', 0):.3f})")
    
    # Step 2: User indicates readiness for assessment
    print("\n2. User indicates readiness for assessment...")
    message2 = "Ya, saya siap untuk assessment dan pertanyaan lebih lanjut"
    response2 = await conversation_flow_service.process_flow_message(client_id, message2)
    print(f"Response 2 type: {response2.get('type')}")
    print(f"Response 2 stage: {response2.get('stage')}")
    print(f"Response 2 message: {response2.get('message')[:200]}...")
    
    # Check if assessment was started
    if response2.get('type') == 'assessment_started':
        print("✅ Assessment was started successfully!")
        assessment_data = response2.get('assessment_data', {})
        question = assessment_data.get('question', {})
        print(f"First question: {question.get('text', 'No question found')}")
    else:
        print("❌ Assessment was NOT started")
        print(f"Instead got response type: {response2.get('type')}")
    
    # Check flow state after second message
    flow_status2 = conversation_flow_service.get_flow_status(client_id)
    print(f"\nFlow status after message 2:")
    print(f"  Current stage: {flow_status2.get('current_stage')}")
    print(f"  Stage progress: {flow_status2.get('stage_progress', {})}")
    
    return response1, response2

if __name__ == "__main__":
    asyncio.run(test_conversation_flow())