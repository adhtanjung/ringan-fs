#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import init_db, get_mongodb

async def main():
    # Initialize database connection
    await init_db()
    db = get_mongodb()
    if db:
        db = db.mental_health_db
    
    if db is None:
        print("❌ Failed to connect to database")
        return
    
    print("🔍 Checking next_actions collection...")
    
    # Get all next_actions
    next_actions = await db.next_actions.find({}, {'action_id': 1, 'action_type': 1, 'label': 1, '_id': 0}).to_list(length=None)
    print(f"📊 Found {len(next_actions)} next_actions:")
    
    for action in next_actions:
        print(f"  - action_id: {action.get('action_id')}, action_type: {action.get('action_type')}, label: {action.get('label')}")
    
    print("\n🔍 Checking feedback_prompts collection...")
    feedback_sample = await db.feedback_prompts.find({}, {'next_action_id': 1, '_id': 0}).limit(5).to_list(length=5)
    print(f"📊 Sample feedback next_action_ids:")
    for feedback in feedback_sample:
        print(f"  - next_action_id: {feedback.get('next_action_id')}")

if __name__ == "__main__":
    asyncio.run(main())