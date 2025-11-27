import hashlib

def verify_password():
    """Verify what the password hash should be"""
    print("=== PASSWORD VERIFICATION ===")
    
    # Test different passwords
    test_passwords = ["admin", "Admin", "ADMIN", "admin123", "password"]
    
    for pwd in test_passwords:
        hash_result = hashlib.sha256(pwd.encode()).hexdigest()
        print(f"Password: '{pwd}'")
        print(f"Hash:     {hash_result}")
        print()
    
    # The CORRECT hash for "admin" should be:
    correct_hash = hashlib.sha256("admin".encode()).hexdigest()
    print(f"✅ CORRECT hash for 'admin': {correct_hash}")

if __name__ == "__main__":
    verify_password()