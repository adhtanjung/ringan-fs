#!/usr/bin/env python3
"""
Debug feedback validation issues
"""

import asyncio
import sys
import os
import pandas as pd

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.data_import_service import data_import_service
from app.services.dataset_management_service import dataset_management_service
from app.services.dataset_validation_service import dataset_validation_service
from app.core.database import get_mongodb

async def debug_feedback_validation():
    print("🧪 Debugging feedback validation...")
    
    # Initialize services
    await data_import_service.initialize()
    print("✅ Services initialized")
    
    # Get database connection
    db = get_mongodb()
    if db:
        db = db.mental_health_db
    print(f"🔍 Database connection: {db is not None}")
    
    # Check what next_actions exist in the database
    print("\n🔍 Checking next_actions in database...")
    try:
        next_actions_cursor = db.next_actions.find({})
        next_actions = await next_actions_cursor.to_list(None)
        print(f"📊 Found {len(next_actions)} next_actions in database:")
        for action in next_actions:
            print(f"  - action_id: {action.get('action_id')}, label: {action.get('label')}")
    except Exception as e:
        print(f"❌ Error checking next_actions: {e}")
    
    # Load feedback data from Excel
    print("\n🔍 Loading feedback data from Excel...")
    try:
        df_feedback = pd.read_excel('data/anxiety.xlsx', sheet_name='1.4 Feedback Prompts')
        print(f"📊 Loaded {len(df_feedback)} feedback prompts from Excel")
        
        if len(df_feedback) > 0:
            print("\n🔍 Sample feedback data:")
            for idx, row in df_feedback.head(3).iterrows():
                print(f"  Row {idx}: prompt_id={row.get('prompt_id')}, next_action={row.get('next_action')}")
                
            # Test validation with first feedback prompt
            first_feedback = df_feedback.iloc[0]
            feedback_data = {
                "prompt_id": str(first_feedback.get('prompt_id', '')),
                "stage": str(first_feedback.get('stage', 'assessment')),
                "prompt_text": str(first_feedback.get('prompt_text', '')),
                "next_action_id": str(first_feedback.get('next_action', 'continue_same')),
                "context": None
            }
            
            print(f"\n🔄 Testing validation with data: {feedback_data}")
            validation_result = await dataset_validation_service.validate_feedback_prompt(feedback_data)
            print(f"✅ Validation result:")
            print(f"  - is_valid: {validation_result.is_valid}")
            print(f"  - errors: {validation_result.errors}")
            print(f"  - field_errors: {validation_result.field_errors}")
            print(f"  - foreign_key_errors: {validation_result.foreign_key_errors}")
            
    except Exception as e:
        print(f"❌ Error loading feedback data: {e}")
        import traceback
        traceback.print_exc()
    
    # Load training data from Excel
    print("\n🔍 Loading training data from Excel...")
    try:
        df_training = pd.read_excel('data/anxiety.xlsx', sheet_name='1.6 FineTuning Examples')
        print(f"📊 Loaded {len(df_training)} training examples from Excel")
        
        if len(df_training) > 0:
            print("\n🔍 Sample training data:")
            for idx, row in df_training.head(3).iterrows():
                print(f"  Row {idx}: id={row.get('id')}, domain={row.get('domain', 'anxiety')}")
                
            # Test validation with first training example
            first_training = df_training.iloc[0]
            training_data = {
                "example_id": str(first_training.get('id', '')),
                "domain": "anxiety",
                "problem": str(first_training.get('problem', '')),
                "conversation_id": str(first_training.get('ConversationID', '')),
                "user_intent": "problem_identification",
                "prompt": str(first_training.get('prompt', '')),
                "completion": str(first_training.get('completion', '')),
                "context": None,
                "quality_score": 0.8,
                "tags": ["anxiety"]
            }
            
            print(f"\n🔄 Testing training validation with data: {training_data}")
            validation_result = await dataset_validation_service.validate_training_example(training_data)
            print(f"✅ Training validation result:")
            print(f"  - is_valid: {validation_result.is_valid}")
            print(f"  - errors: {validation_result.errors}")
            print(f"  - field_errors: {validation_result.field_errors}")
            
    except Exception as e:
        print(f"❌ Error loading training data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_feedback_validation())