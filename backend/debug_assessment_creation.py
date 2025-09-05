#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.vector_models import AssessmentQuestion, ResponseType
from app.models.dataset_models import AssessmentQuestionModel

async def test_assessment_creation():
    print("🧪 Testing AssessmentQuestion creation...")
    
    # Create an AssessmentQuestion with scale_min and scale_max
    question = AssessmentQuestion(
        question_id="Q001",
        sub_category_id="s001_01",
        batch_id="b001",
        question_text="Test question",
        response_type=ResponseType.SCALE,
        domain="anxiety",
        scale_min=0,
        scale_max=4
    )
    
    print(f"✅ AssessmentQuestion created: {question.dict()}")
    print(f"Scale min: {question.scale_min}, Scale max: {question.scale_max}")
    
    # Now try to create AssessmentQuestionModel
    try:
        assessment_data = {
            "question_id": question.question_id,
            "sub_category_id": question.sub_category_id,
            "question_text": question.question_text,
            "response_type": question.response_type,
            "batch_id": question.batch_id,
            "scale_min": question.scale_min,
            "scale_max": question.scale_max
        }
        
        print(f"Assessment data: {assessment_data}")
        
        model = AssessmentQuestionModel(**assessment_data)
        print(f"✅ AssessmentQuestionModel created successfully: {model.dict()}")
        
    except Exception as e:
        print(f"❌ Failed to create AssessmentQuestionModel: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_assessment_creation())