#!/usr/bin/env python3
"""
Database Setup Script for Multi-Agent Marketing System
This script helps you set up and configure your database connection.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def test_database_connection(database_url):
    """Test database connection"""
    try:
        engine = create_engine(database_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print(f"✅ Database connection successful!")
            return True
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def setup_postgresql():
    """Setup PostgreSQL database"""
    print("🐘 Setting up PostgreSQL database...")
    
    # Get connection details
    host = input("Enter PostgreSQL host (default: localhost): ").strip() or "localhost"
    port = input("Enter PostgreSQL port (default: 5432): ").strip() or "5432"
    database = input("Enter database name (default: marketing_system): ").strip() or "marketing_system"
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    
    database_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    
    if test_database_connection(database_url):
        print(f"\n📝 Add this to your environment variables:")
        print(f"export DATABASE_URL='{database_url}'")
        return database_url
    return None

def setup_mysql():
    """Setup MySQL database"""
    print("🐬 Setting up MySQL database...")
    
    # Get connection details
    host = input("Enter MySQL host (default: localhost): ").strip() or "localhost"
    port = input("Enter MySQL port (default: 3306): ").strip() or "3306"
    database = input("Enter database name (default: marketing_system): ").strip() or "marketing_system"
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    
    database_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    
    if test_database_connection(database_url):
        print(f"\n📝 Add this to your environment variables:")
        print(f"export DATABASE_URL='{database_url}'")
        return database_url
    return None

def setup_sqlite():
    """Setup SQLite database"""
    print("🗃️ Setting up SQLite database...")
    
    database_path = input("Enter database file path (default: ./database/app.db): ").strip() or "./database/app.db"
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(database_path), exist_ok=True)
    
    database_url = f"sqlite:///{database_path}"
    
    if test_database_connection(database_url):
        print(f"\n📝 Add this to your environment variables:")
        print(f"export DATABASE_URL='{database_url}'")
        return database_url
    return None

def main():
    """Main setup function"""
    print("🚀 Multi-Agent Marketing System - Database Setup")
    print("=" * 50)
    
    print("\nChoose your database type:")
    print("1. PostgreSQL (Recommended for production)")
    print("2. MySQL")
    print("3. SQLite (Good for development)")
    print("4. Test existing connection")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        setup_postgresql()
    elif choice == "2":
        setup_mysql()
    elif choice == "3":
        setup_sqlite()
    elif choice == "4":
        database_url = input("Enter your DATABASE_URL: ").strip()
        test_database_connection(database_url)
    else:
        print("❌ Invalid choice!")
        sys.exit(1)
    
    print("\n✨ Database setup complete!")
    print("\nNext steps:")
    print("1. Set the DATABASE_URL environment variable")
    print("2. Run: python start.py")
    print("3. The application will automatically create the required tables")

if __name__ == "__main__":
    main()
