import json
import os
import hashlib
from datetime import datetime

class SimpleAuth:
    ROLE_LABELS = {
        "admin": "System Administrator",
        "user": "Regular User"
    }

    def __init__(self):
        self.data_dir = "data"
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.current_user = None
        self.ensure_data_directory()
        self.load_users()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def load_users(self):
        """Load users from JSON file"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    self.users = json.load(f)
                print(f"Loaded {len(self.users)} users")
            else:
                self.create_default_admin()
        except Exception as e:
            print(f"Error loading users: {e}")
            self.create_default_admin()
    
    def create_default_admin(self):
        """Create default admin user"""
        self.users = [
            {
                "user_id": 1,
                "username": "admin",
                "password": self.hash_password("admin"),
                "role": "admin",  # internal value
                "full_name": self.ROLE_LABELS["admin"],  # display label
                "email": "admin@canteen.com",
                "is_active": True,
                "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_login": None
            }
        ]
        self.save_users()
        print("Created default admin user")
    
    def save_users(self):
        """Save users to JSON file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self, username, password):
        """Login system"""
        if not username or not password:
            return False, "Username and password are required"
        
        for user in self.users:
            if user['username'] == username and user.get('is_active', True):
                if user['password'] == self.hash_password(password):
                    user['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.save_users()
                    self.current_user = user
                    display_role = self.ROLE_LABELS.get(user['role'], user['role'])
                    print(f"Login successful for {username} ({display_role})")
                    return True, f"Login successful as {display_role}"
                else:
                    print(f"Password incorrect for {username}")
                    return False, "Invalid password"
        
        print(f"User not found: {username}")
        return False, "Invalid username or password"
    
    def logout(self):
        """Logout current user"""
        self.current_user = None
    
    def get_current_user(self):
        """Get current user info"""
        return self.current_user
    
    def is_admin(self):
        """Check if current user is admin"""
        if not self.current_user:
            print("is_admin: No current user")
            return False
        
        role = self.current_user.get('role')
        print(f"is_admin check: role='{role}'")
        
        result = role == 'admin'
        print(f"is_admin result: {result}")
        return result
    
    def add_user(self, username, password, role, full_name, email=""):
        """Add new user (admin only)"""
        print(f"add_user called by: {self.current_user.get('username') if self.current_user else 'None'}")
        
        if not self.current_user or self.current_user.get('role') != 'admin':
            print("add_user: Not admin")
            return False, "Only admin users can add accounts"
        
        if not username or not password or not role or not full_name:
            return False, "All fields are required"
        
        # Check if username exists
        for user in self.users:
            if user['username'] == username:
                return False, "Username already exists"
        
        # Create new user
        new_user = {
            "user_id": len(self.users) + 1,
            "username": username,
            "password": self.hash_password(password),
            "role": role,  # internal value
            "full_name": full_name,
            "email": email,
            "is_active": True,
            "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": None
        }
        
        self.users.append(new_user)
        self.save_users()
        display_role = self.ROLE_LABELS.get(role, role)
        print(f"User '{username}' created successfully as {display_role}")
        return True, f"User '{username}' added successfully as {display_role}"
    
    def get_all_users(self):
        """Get all users (admin only)"""
        if not self.is_admin():
            return []
        return self.users