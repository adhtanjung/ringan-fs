import asyncio
from app.services.semantic_search_service import semantic_search_service

async def test_search():
    await semantic_search_service.initialize()
    
    # Test problem search
    response = await semantic_search_service.search_problems('I feel anxious about exams', limit=3)
    print(f'Search success: {response.success}')
    print(f'Found {len(response.results)} results')
    
    if response.success and response.results:
        print('Search results for anxiety:')
        for r in response.results:
            print(f'ID: {r.id}, Score: {r.score:.3f}, Category: "{r.payload.get("category")}", Problem: {r.payload.get("problem_name")}')
        
        top_result = response.results[0]
        category = top_result.payload.get('category')
        print(f'\nTop result category: "{category}" (type: {type(category)})')
        
        # Test assessment search with this category
        print(f'\nSearching assessments for category: "{category}"')
        assessment_response = await semantic_search_service.search_assessment_questions(category, limit=3)
        print(f'Assessment search success: {assessment_response.success}')
        print(f'Found {len(assessment_response.results)} assessment questions')
        
        if assessment_response.success and assessment_response.results:
            for ar in assessment_response.results:
                question_text = ar.payload.get('question_text', '')
                print(f'  Question: {question_text[:100]}...')
        else:
            print(f'  Assessment search failed: {assessment_response.error}')
    else:
        print(f'Problem search failed: {response.error}')

if __name__ == '__main__':
    asyncio.run(test_search())