import subprocess
import sys
import os

def setup_project():
    """One-time setup for the project"""
    print("Setting up PDF Q&A Application...")
    
    # Create directories
    dirs = ['uploads', 'static', 'templates']
    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"Created directory: {dir_name}")
    
    # Install requirements
    print("Installing Python packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("All packages installed successfully!")
    except Exception as e:
        print(f"Error installing packages: {e}")
        return False
    
    print("\n" + "="*50)
    print("SETUP COMPLETE!")
    print("="*50)
    print("IMPORTANT: You need to get an OpenRouter API key!")
    print("1. Go to: https://openrouter.ai/")
    print("2. Create an account and get your API key")
    print("3. Edit app.py file and replace 'PUT_YOUR_OPENROUTER_API_KEY_HERE' with your actual API key")
    print("\nAfter adding your API key, run: python run.py")
    print("="*50)

if __name__ == "__main__":
    setup_project()
    input("Press Enter to exit...")