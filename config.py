"""
Multi-Agent Marketing System - Configuration
Environment-specific configuration settings
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Agent settings
    MAX_CONCURRENT_AGENTS = int(os.environ.get('MAX_CONCURRENT_AGENTS', 10))
    AGENT_TIMEOUT_SECONDS = int(os.environ.get('AGENT_TIMEOUT_SECONDS', 300))
    
    # Memory settings
    MAX_MEMORY_ENTRIES = int(os.environ.get('MAX_MEMORY_ENTRIES', 10000))
    MEMORY_CLEANUP_INTERVAL = int(os.environ.get('MEMORY_CLEANUP_INTERVAL', 3600))
    
    # MCP server settings
    MCP_HOST = os.environ.get('MCP_HOST', 'localhost')
    MCP_PORT = int(os.environ.get('MCP_PORT', 8080))
    
    # Security settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    RATE_LIMIT_REQUESTS = int(os.environ.get('RATE_LIMIT_REQUESTS', 100))
    RATE_LIMIT_WINDOW = int(os.environ.get('RATE_LIMIT_WINDOW', 3600))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
    
    # Development-specific settings
    LOG_LEVEL = 'DEBUG'
    ENABLE_DEBUG_TOOLBAR = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    
    # Testing-specific settings
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False

class ProductionConfig(Config):
    """Production configuration"""
    
    # Production-specific settings
    LOG_LEVEL = 'INFO'
    ENABLE_DEBUG_TOOLBAR = False
    
    # Security settings for production
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'https://yourdomain.com').split(',')
    
    # Database settings for production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Redis settings for production
    REDIS_URL = os.environ.get('REDIS_URL')
    
    # Monitoring settings
    ENABLE_METRICS = True
    METRICS_PORT = int(os.environ.get('METRICS_PORT', 9090))

class DockerConfig(ProductionConfig):
    """Docker-specific configuration"""
    
    # Docker-specific settings
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))
    
    # Database settings for Docker
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://user:pass@db:5432/marketing_system')
    
    # Redis settings for Docker
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379')

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration class by name"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])

