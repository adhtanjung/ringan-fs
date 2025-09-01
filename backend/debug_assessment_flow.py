import asyncio
from app.services.assessment_service import AssessmentService
from app.services.semantic_search_service import semantic_search_service
from app.services.vector_service import vector_service
from app.services.embedding_service import embedding_service

async def debug_assessment_flow():
    # Initialize services
    await vector_service.connect()
    await embedding_service.initialize()
    
    assessment_service = AssessmentService()
    
    print("=== Debugging Work Stress Assessment Flow ===")
    
    # Simulate starting assessment for work stress
    client_id = "debug_client"
    problem_category = "work stress"
    
    print(f"Starting assessment for: {problem_category}")
    
    # Test the search query that assessment service uses
    search_query = f"{problem_category} stress anxiety mental health"
    print(f"Search query: '{search_query}'")
    
    search_response = await semantic_search_service.search_assessment_questions(
        problem_description=search_query,
        sub_category_id=None,
        limit=50,
        score_threshold=0.3
    )
    
    print(f"Search success: {search_response.success}")
    print(f"Results found: {len(search_response.results) if search_response.success else 0}")
    
    if search_response.success and search_response.results:
        print("\nTop 10 questions found:")
        for i, result in enumerate(search_response.results[:10]):
            payload = result.payload
            print(f"{i+1}. Score: {result.score:.3f}")
            print(f"   Text: {payload.get('text', 'N/A')}")
            print(f"   Question ID: {payload.get('question_id', 'N/A')}")
            print(f"   Domain: {payload.get('domain', 'N/A')}")
            print(f"   Next step: {payload.get('next_step', 'N/A')}")
            print()
    
    # Now test the actual assessment start
    print("\n=== Testing actual assessment start ===")
    result = await assessment_service.start_assessment(client_id, problem_category)
    
    print(f"Assessment result type: {result.get('type')}")
    if result.get('type') == 'assessment_question':
        print(f"First question: {result.get('question')}")
        print(f"Question ID: {result.get('question_id')}")
        print(f"Progress: {result.get('progress')}")
    else:
        print(f"Error: {result.get('message')}")
    
    # Check session data
    if client_id in assessment_service.active_sessions:
        session = assessment_service.active_sessions[client_id]
        print(f"\nSession created with {len(session['all_questions'])} questions")
        print(f"Current question ID: {session['current_question']['question_id']}")
        print(f"Current question text: {session['current_question']['question_text']}")

if __name__ == '__main__':
    asyncio.run(debug_assessment_flow())