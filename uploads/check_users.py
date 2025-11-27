import json
import os

def check_users_file():
    """Check the current users.json file"""
    users_file = "data/users.json"
    
    print("=== CHECKING USERS.JSON ===")
    
    if not os.path.exists(users_file):
        print("❌ users.json file does not exist!")
        return
    
    try:
        with open(users_file, 'r') as f:
            users = json.load(f)
        
        print(f"✅ Found {len(users)} users:")
        for i, user in enumerate(users):
            print(f"\nUser {i+1}:")
            print(f"  Username: {user.get('username', 'MISSING')}")
            print(f"  Role: {user.get('role', 'MISSING')}")
            print(f"  Full Name: {user.get('full_name', 'MISSING')}")
            print(f"  Is Active: {user.get('is_active', 'MISSING')}")
            print(f"  All fields: {list(user.keys())}")
            
    except Exception as e:
        print(f"❌ Error reading users.json: {e}")

if __name__ == "__main__":
    check_users_file()