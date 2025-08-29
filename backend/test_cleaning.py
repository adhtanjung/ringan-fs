#!/usr/bin/env python3
"""
Test script for data cleaning service
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.data_cleaning_service import data_cleaning_service
import pandas as pd
from pathlib import Path

def test_cleaning():
    """Test the data cleaning service"""

    print("🧪 Testing data cleaning service...\n")

    # Test response type cleaning
    print("📝 Testing response type cleaning:")
    test_response_types = [
        'scale (0–4)',
        'scale (1–5)',
        'yes/no',
        'yes_no',
        'text',
        'Open text',
        'unknown_type',
        '',
        None
    ]

    for rt in test_response_types:
        cleaned = data_cleaning_service._clean_response_type(rt)
        print(f"   '{rt}' -> '{cleaned}'")

    print("\n🎭 Testing stage cleaning:")
    test_stages = [
        'post_suggestion',
        'ongoing',
        'post-suggestion',
        'unknown_stage',
        '',
        None
    ]

    for stage in test_stages:
        cleaned = data_cleaning_service._clean_stage(stage)
        print(f"   '{stage}' -> '{cleaned}'")

    print("\n⏭️ Testing next action cleaning:")
    test_actions = [
        'continue_same',
        'show_problem_menu',
        '[yes]A01, [no] Continue coaching within the same problem module',
        '[general] offer resources, [try to do diet] continue coanching',
        'unknown_action',
        '',
        None
    ]

    for action in test_actions:
        cleaned = data_cleaning_service._clean_next_action(action)
        print(f"   '{action}' -> '{cleaned}'")

    print("\n✅ Data cleaning service test completed!")

if __name__ == "__main__":
    test_cleaning()
