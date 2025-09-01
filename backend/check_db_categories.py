import asyncio
from app.services.vector_service import vector_service

async def check_categories():
    await vector_service.connect()
    results = vector_service.client.scroll('mental-health-problems', limit=20)
    
    print('Sample problem records:')
    categories = set()
    for p in results[0]:
        category = p.payload.get('category')
        categories.add(category)
        print(f'ID: {p.id}, Category: "{category}", Problem: {p.payload.get("problem_name")}')
    
    print(f'\nUnique categories found: {sorted(categories)}')

if __name__ == '__main__':
    asyncio.run(check_categories())