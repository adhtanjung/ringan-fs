from app.core.database import get_mongodb
import asyncio

async def check_stress_problems():
    db = get_mongodb()
    if db is None:
        print("Failed to connect to database")
        return
    
    stress_problems = list(db.problems.find({'domain': 'stress'}, {'category_id': 1, 'sub_category_id': 1, '_id': 0}))
    print(f"Found {len(stress_problems)} stress problems")
    print("\nStress problems with category_id and sub_category_id:")
    for i, p in enumerate(stress_problems):
        print(f"{i+1}. category_id: {p.get('category_id')}, sub_category_id: {p.get('sub_category_id')}")
    
    # Check for the specific problematic IDs
    print("\nChecking for STR_04_08 and STR_04_26:")
    str_04_08 = db.problems.find_one({'sub_category_id': 'STR_04_08'})
    str_04_26 = db.problems.find_one({'sub_category_id': 'STR_04_26'})
    print(f"STR_04_08 found: {str_04_08 is not None}")
    print(f"STR_04_26 found: {str_04_26 is not None}")
    
    # Show all unique sub_category_ids for stress
    all_sub_category_ids = set()
    for p in stress_problems:
        if p.get('sub_category_id'):
            all_sub_category_ids.add(p['sub_category_id'])
    
    print(f"\nAll stress sub_category_ids: {sorted(all_sub_category_ids)}")

if __name__ == "__main__":
    asyncio.run(check_stress_problems())