import asyncio
from app.services.vector_service import vector_service
from app.services.embedding_service import embedding_service

async def check_vector_content():
    await vector_service.connect()
    await embedding_service.initialize()
    
    # Get all assessment questions
    points, _ = vector_service.client.scroll('mental-health-assessments', limit=240)
    print(f'Total assessment questions: {len(points)}')
    
    # Look for work-related questions
    work_related = []
    for p in points:
        text = p.payload.get('text', '').lower()
        if any(keyword in text for keyword in ['work', 'job', 'workplace', 'boss', 'supervisor', 'colleague', 'office']):
            work_related.append(p)
    
    print(f'\nWork-related questions found: {len(work_related)}')
    for p in work_related:
        domain = p.payload.get('domain', 'N/A')
        text = p.payload.get('text', 'N/A')
        sub_category = p.payload.get('sub_category_id', 'N/A')
        print(f'ID: {p.id}, Domain: {domain}, Sub-category: {sub_category}')
        print(f'Text: {text}')
        print('---')
    
    # Test semantic search for work stress
    print('\n=== Testing semantic search for work stress ===')
    query_embedding = await embedding_service.generate_embedding('work stress pressure job workplace')
    if query_embedding:
        search_results = await vector_service.search_similar(
            collection_name='mental-health-assessments',
            vector=query_embedding,
            limit=5,
            score_threshold=0.3
        )
        
        print(f'Search results: {len(search_results)}')
        for result in search_results:
            print(f'Score: {result["score"]:.3f}, Text: {result["payload"].get("text", "N/A")[:100]}...')

if __name__ == '__main__':
    asyncio.run(check_vector_content())