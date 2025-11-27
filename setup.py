import os
import subprocess
import sys

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def create_directories():
    """Create necessary directories"""
    directories = ['data', 'config', 'backups', 'reports']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        else:
            print(f"Directory already exists: {directory}")

def initialize_system():
    """Initialize the system"""
    print("Initializing Canteen Management System...")
    
    # Create directories
    create_directories()
    
    # Install requirements
    install_requirements()
    
    print("\n✅ System initialization complete!")
    print("\nTo start the system, run:")
    print("streamlit run app.py")
    
    print("\nSystem will be available at: http://localhost:8501")

if __name__ == "__main__":
    initialize_system()