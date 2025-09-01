#!/usr/bin/env python3
"""
Multi-Agent Marketing System - Startup Script
Simple script to start the application from the root directory
"""

import os
import sys
import subprocess

def main():
    """Main startup function"""
    print("🚀 Multi-Agent Marketing System")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('src/main.py'):
        print("❌ Error: Please run this script from the project root directory")
        print("   Current directory:", os.getcwd())
        sys.exit(1)
    
    # Check if virtual environment exists
    venv_path = os.path.join('venv', 'Scripts' if os.name == 'nt' else 'bin')
    if not os.path.exists(venv_path):
        print("⚠️  Virtual environment not found. Creating one...")
        try:
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
            print("✅ Virtual environment created successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to create virtual environment")
            sys.exit(1)
    
    # Check if requirements are installed
    print("📦 Checking dependencies...")
    try:
        # Try to import key packages
        import flask
        import pandas
        import numpy
        import sklearn
        print("✅ All dependencies are installed")
    except ImportError:
        print("📥 Installing dependencies...")
        pip_cmd = os.path.join(venv_path, 'pip')
        try:
            subprocess.run([pip_cmd, 'install', '-r', 'requirements.txt'], check=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            sys.exit(1)
    
    # Start the application
    print("🚀 Starting the application...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🔌 API endpoints at: http://localhost:5000/api")
    print("=" * 50)
    
    try:
        # Change to src directory and run main.py
        os.chdir('src')
        subprocess.run([sys.executable, 'main.py'])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

