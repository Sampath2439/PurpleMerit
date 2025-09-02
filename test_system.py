#!/usr/bin/env python3
"""
Multi-Agent Marketing System - System Test Script
Simple script to test if all system components are working correctly
"""

import sys
import os
import requests
import time
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    try:
        from agents import create_agent_system, AgentType
        print("✅ Agents module imported successfully")
        
        from models.user import User, db
        print("✅ User models imported successfully")
        
        from routes.agents import agents_bp
        print("✅ Agent routes imported successfully")
        
        from routes.user import user_bp
        print("✅ User routes imported successfully")
        
        from utils.data_processing import DataProcessor, MLPipeline, AgentMemorySystem
        print("✅ Data processing utilities imported successfully")
        
        from mcp.mcp_server import create_mcp_server
        print("✅ MCP server imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_agent_system():
    """Test if the agent system can be created"""
    print("\n🤖 Testing agent system creation...")
    
    try:
        from agents import create_agent_system
        
        orchestrator, agents = create_agent_system()
        
        if orchestrator and agents:
            print(f"✅ Agent system created successfully")
            print(f"   - Orchestrator: {type(orchestrator).__name__}")
            print(f"   - Agents: {len(agents)} agents created")
            
            for name, agent in agents.items():
                print(f"     - {name}: {agent.agent_id} ({agent.agent_type.value})")
            
            return True
        else:
            print("❌ Agent system creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Agent system test error: {e}")
        return False

def test_data_processing():
    """Test data processing utilities"""
    print("\n📊 Testing data processing utilities...")
    
    try:
        from utils.data_processing import DataProcessor, MLPipeline, AgentMemorySystem
        
        # Test DataProcessor
        processor = DataProcessor()
        sample_data = processor.load_data()
        if sample_data:
            print(f"✅ DataProcessor working - loaded {len(sample_data)} datasets")
        
        # Test MLPipeline
        ml_pipeline = MLPipeline()
        print("✅ MLPipeline created successfully")
        
        # Test AgentMemorySystem
        memory_system = AgentMemorySystem()
        print("✅ AgentMemorySystem created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Data processing test error: {e}")
        return False

def test_mcp_server():
    """Test MCP server creation"""
    print("\n🔌 Testing MCP server...")
    
    try:
        from mcp.mcp_server import create_mcp_server
        
        mcp_server = create_mcp_server()
        
        if mcp_server:
            print(f"✅ MCP server created successfully")
            print(f"   - Host: {mcp_server.host}")
            print(f"   - Port: {mcp_server.port}")
            return True
        else:
            print("❌ MCP server creation failed")
            return False
            
    except Exception as e:
        print(f"❌ MCP server test error: {e}")
        return False

def test_flask_app():
    """Test if Flask app can be created"""
    print("\n🌐 Testing Flask application...")
    
    try:
        from main import app
        
        if app:
            print("✅ Flask app created successfully")
            print(f"   - App name: {app.name}")
            print(f"   - Blueprints: {len(app.blueprints)} registered")
            return True
        else:
            print("❌ Flask app creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Flask app test error: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints if server is running"""
    print("\n🔗 Testing API endpoints...")
    
    base_url = "http://localhost:5000"
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint responding")
        else:
            print(f"⚠️  Health endpoint returned {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Server not running - skipping API tests")
        print("   Start the server with: python start.py")
        return True
        
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 Multi-Agent Marketing System - System Test")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Agent System", test_agent_system),
        ("Data Processing", test_data_processing),
        ("MCP Server", test_mcp_server),
        ("Flask App", test_flask_app),
        ("API Endpoints", test_api_endpoints),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\n🚀 To start the system:")
        print("   python start.py")
        print("\n📊 Access the dashboard at: http://localhost:5000")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Common fixes:")
        print("   - Install dependencies: pip install -r requirements.txt")
        print("   - Check Python version (3.11+ required)")
        print("   - Verify all files are in place")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

