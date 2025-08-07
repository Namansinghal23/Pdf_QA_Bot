import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("All packages installed successfully!")

def run_app():
    """Run the Flask application"""
    print("Starting the application...")
    os.system("python app.py")

if __name__ == "__main__":
    try:
        # Install requirements first
        install_requirements()
        
        # Then run the app
        run_app()
        
    except Exception as e:
        print(f"Error: {e}")
        print("Please check if Python is installed correctly.")
        input("Press Enter to exit...")