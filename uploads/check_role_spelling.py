import json
import os

def check_exact_role_spelling():
    """Check the exact spelling and characters in the role field"""
    users_file = "data/users.json"
    
    print("=== CHECKING EXACT ROLE SPELLING ===")
    
    if not os.path.exists(users_file):
        print("❌ users.json doesn't exist!")
        return
    
    with open(users_file, 'r') as f:
        users = json.load(f)
    
    admin_user = None
    for user in users:
        if user.get('username') == 'admin':
            admin_user = user
            break
    
    if not admin_user:
        print("❌ No admin user found!")
        return
    
    role_value = admin_user.get('role')
    
    print("🔍 ADMIN USER ROLE ANALYSIS:")
    print(f"  Raw role value: '{role_value}'")
    print(f"  Type: {type(role_value)}")
    print(f"  Length: {len(role_value) if role_value else 0}")
    print(f"  Repr: {repr(role_value)}")
    
    if role_value:
        print(f"  Character codes: {[ord(c) for c in role_value]}")
        print(f"  Is 'admin'? {role_value == 'admin'}")
        print(f"  Is 'Admin'? {role_value == 'Admin'}")
        print(f"  Is 'ADMIN'? {role_value == 'ADMIN'}")
        print(f"  Lowercase: '{role_value.lower()}'")
        print(f"  Stripped: '{role_value.strip()}'")
    
    print(f"  All user fields:")
    for key, value in admin_user.items():
        print(f"    {key}: {repr(value)}")

if __name__ == "__main__":
    check_exact_role_spelling()