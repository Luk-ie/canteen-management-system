import streamlit as st
import json
import os
import hashlib
from datetime import datetime

class DebugAuth:
    def __init__(self):
        self.data_dir = "data"
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.current_user = None
        self.debug_messages = []
        self.initialize_system()
    
    def log(self, message):
        """Add debug message"""
        self.debug_messages.append(message)
        print(message)
    
    def initialize_system(self):
        """Initialize the authentication system"""
        self.log("Initializing authentication system...")
        
        # Ensure data directory exists
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            self.log(f"Created directory: {self.data_dir}")
        
        # Check if users file exists
        if os.path.exists(self.users_file):
            self.log(f"Users file exists: {self.users_file}")
            self.load_users()
        else:
            self.log("Users file does not exist. Creating default admin...")
            self.create_default_admin()
    
    def create_default_admin(self):
        """Create default admin user"""
        default_admin = {
            "user_id": 1,
            "username": "admin",
            "password": self.hash_password("admin"),  # password: admin
            "role": "admin", 
            "full_name": "System Administrator",
            "email": "admin@canteen.com",
            "is_active": True,
            "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": None
        }
        
        self.users = [default_admin]
        self.save_users()
        self.log("Default admin user created successfully!")
        self.log(f"Admin password hash: {default_admin['password']}")
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_users(self):
        """Load users from file"""
        try:
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
            self.log(f"Loaded {len(self.users)} users")
            for user in self.users:
                self.log(f"User: {user['username']} (active: {user['is_active']})")
        except Exception as e:
            self.log(f"Error loading users: {e}")
            self.create_default_admin()
    
    def save_users(self):
        """Save users to file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=2)
            self.log("Users saved successfully")
        except Exception as e:
            self.log(f"Error saving users: {e}")
    
    def login(self, username, password):
        """Attempt login with detailed debugging"""
        self.log(f"=== LOGIN ATTEMPT ===")
        self.log(f"Username: '{username}'")
        self.log(f"Password length: {len(password)}")
        
        if not username or not password:
            self.log("Username or password empty")
            return False, "Username and password are required"
        
        # Find user
        user_found = None
        for user in self.users:
            if user['username'] == username:
                user_found = user
                break
        
        if not user_found:
            self.log("User not found")
            return False, "Invalid username or password"
        
        if not user_found['is_active']:
            self.log("User account is inactive")
            return False, "Account is inactive"
        
        # Verify password
        input_hash = self.hash_password(password)
        stored_hash = user_found['password']
        
        self.log(f"Input hash:  {input_hash}")
        self.log(f"Stored hash: {stored_hash}")
        self.log(f"Password match: {input_hash == stored_hash}")
        
        if input_hash == stored_hash:
            user_found['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.save_users()
            self.current_user = user_found
            self.log("LOGIN SUCCESSFUL!")
            return True, "Login successful"
        else:
            self.log("Password incorrect")
            return False, "Invalid username or password"
    
    def get_debug_info(self):
        """Get debug information for display"""
        return self.debug_messages
    
    def get_current_user(self):
        return self.current_user
    
    def logout(self):
        self.current_user = None