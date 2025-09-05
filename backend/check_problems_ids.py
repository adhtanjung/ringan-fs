from app.core.database import get_mongodb

def check_problems():
    db = get_mongodb()
    if db is None:
        print("Failed to connect to database")
        return
    
    problems = list(db.problems.find({}, {'category_id': 1, 'sub_category_id': 1, '_id': 0}))
    print(f"Found {len(problems)} problems")
    print("\nProblems with category_id and sub_category_id:")
    for i, p in enumerate(problems[:15]):
        print(f"{i+1}. category_id: {p.get('category_id', 'N/A')}, sub_category_id: {p.get('sub_category_id', 'N/A')}")
    
    # Check for specific problematic IDs
    print("\nChecking for STR_04_08 and STR_04_26:")
    str_04_08 = db.problems.find_one({'sub_category_id': 'STR_04_08'})
    str_04_26 = db.problems.find_one({'sub_category_id': 'STR_04_26'})
    print(f"STR_04_08 found: {str_04_08 is not None}")
    print(f"STR_04_26 found: {str_04_26 is not None}")
    
    # Show all unique category_ids and sub_category_ids
    all_category_ids = set()
    all_sub_category_ids = set()
    for p in problems:
        if p.get('category_id'):
            all_category_ids.add(p['category_id'])
        if p.get('sub_category_id'):
            all_sub_category_ids.add(p['sub_category_id'])
    
    print(f"\nUnique category_ids: {sorted(all_category_ids)}")
    print(f"\nUnique sub_category_ids: {sorted(all_sub_category_ids)}")

if __name__ == "__main__":
    check_problems()