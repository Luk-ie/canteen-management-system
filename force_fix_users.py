import json
import os
import hashlib
from datetime import datetime

def force_fix_users():
    """Completely reset and fix the users.json file"""
    data_dir = "data"
    users_file = os.path.join(data_dir, "users.json")
    
    print("=== FORCE FIXING USERS.JSON ===")
    
    # Create fresh admin user
    admin_user = {
        "user_id": 1,
        "username": "admin",
        "password": hashlib.sha256("admin".encode()).hexdigest(),
        "role": "admin",  # Explicitly set role
        "full_name": "System Administrator",
        "email": "admin@canteen.com",
        "is_active": True,
        "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_login": None
    }
    
    users = [admin_user]
    
    # Ensure data directory exists
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print("Created data directory")
    
    # Save fresh users file
    try:
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)
        print("Successfully created fresh users.json")
        print("Admin user created with:")
        print(f"   Username: admin")
        print(f"   Password: admin") 
        print(f"   Role: admin")
        print(f"   File: {users_file}")
        return True
    except Exception as e:
        print(f"❌ Error creating users file: {e}")
        return False

if __name__ == "__main__":
    force_fix_users()