#!/usr/bin/env python3
"""
Setup script for Yaswanth's AI Twin project
"""

import os
import subprocess
import sys
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("🔧 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def create_env_file():
    """Create .env file for API key"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("\n🔑 Setting up API key...")
        api_key = input("Enter your OpenAI API key: ").strip()
        
        if api_key:
            with open(env_file, 'w') as f:
                f.write(f"OPENAI_API_KEY={api_key}\n")
            print("✅ API key saved to .env file")
            return True
        else:
            print("❌ No API key provided")
            return False
    else:
        print("✅ .env file already exists")
        return True

def main():
    """Main setup function"""
    print("🚀 Setting up Yaswanth's AI Twin...")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        print("Setup failed at package installation")
        return False
    
    # Create env file
    if not create_env_file():
        print("Setup failed at API key configuration")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Setup complete!")
    print("\nTo run your AI Twin:")
    print("python ai_twin.py")
    print("\nOr for advanced features:")
    print("python advanced_twin.py")
    
    return True

if __name__ == "__main__":
    main()
