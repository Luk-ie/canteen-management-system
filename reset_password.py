import json
import os
import hashlib
from datetime import datetime

def reset_admin_password():
    """Reset the admin password to 'admin'"""
    data_dir = "data"
    users_file = os.path.join(data_dir, "users.json")
    
    print("=== ADMIN PASSWORD RESET TOOL ===")
    
    # Check if users file exists
    if not os.path.exists(users_file):
        print("❌ Users file not found!")
        return False
    
    # Load users
    try:
        with open(users_file, 'r') as f:
            users = json.load(f)
        print(f"✅ Loaded {len(users)} users")
    except Exception as e:
        print(f"❌ Error loading users: {e}")
        return False
    
    # Find and update admin user
    admin_found = False
    for user in users:
        if user['username'] == 'admin':
            # Reset password to 'admin'
            new_hash = hashlib.sha256("admin".encode()).hexdigest()
            print(f"🔑 Old password hash: {user['password']}")
            print(f"🔑 New password hash: {new_hash}")
            
            user['password'] = new_hash
            user['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            admin_found = True
            break
    
    if not admin_found:
        print("❌ Admin user not found!")
        return False
    
    # Save updated users
    try:
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)
        print("✅ Admin password reset to 'admin'")
        print("✅ You can now login with:")
        print("   Username: admin")
        print("   Password: admin")
        return True
    except Exception as e:
        print(f"❌ Error saving users: {e}")
        return False

def create_fresh_system():
    """Create a completely fresh system"""
    data_dir = "data"
    users_file = os.path.join(data_dir, "users.json")
    
    print("=== CREATING FRESH SYSTEM ===")
    
    # Create data directory
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print("✅ Created data directory")
    
    # Create fresh users file
    users = [
        {
            "user_id": 1,
            "username": "admin",
            "password": hashlib.sha256("admin".encode()).hexdigest(),
            "role": "admin",
            "full_name": "System Administrator",
            "email": "admin@canteen.com",
            "is_active": True,
            "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": None
        }
    ]
    
    try:
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)
        print("✅ Fresh system created!")
        print("✅ Default credentials:")
        print("   Username: admin")
        print("   Password: admin")
        return True
    except Exception as e:
        print(f"❌ Error creating system: {e}")
        return False

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Reset admin password to 'admin'")
    print("2. Create completely fresh system (WARNING: Deletes all data)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        reset_admin_password()
    elif choice == "2":
        confirm = input("Are you sure? This will delete all existing data! (y/n): ")
        if confirm.lower() == 'y':
            create_fresh_system()
        else:
            print("Operation cancelled.")
    else:
        print("Invalid choice.")