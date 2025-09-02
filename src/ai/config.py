# Configuration for OpenAI integration in agents

OPENAI_CONFIG = {
    # Model configurations
    'models': {
        'lead_analysis': 'gpt-4',
        'content_generation': 'gpt-4',
        'campaign_optimization': 'gpt-4'
    },
    
    # Temperature settings for different tasks
    'temperature': {
        'lead_analysis': 0.3,  # More focused/deterministic
        'content_generation': 0.7,  # More creative
        'campaign_optimization': 0.4  # Balanced
    },
    
    # Maximum tokens for different operations
    'max_tokens': {
        'lead_analysis': 1000,
        'content_generation': 2000,
        'campaign_optimization': 1500
    },
    
    # Retry configurations
    'retry': {
        'max_attempts': 3,
        'initial_delay': 1,
        'max_delay': 10,
        'backoff_factor': 2
    },
    
    # Caching settings
    'cache': {
        'enabled': True,
        'ttl': 3600,  # 1 hour
        'max_size': 1000  # entries
    },
    
    # Rate limiting
    'rate_limits': {
        'requests_per_minute': 60,
        'tokens_per_minute': 10000
    },
    
    # Custom prompting configurations
    'prompts': {
        'lead_analysis': {
            'system_message': """You are an expert marketing analyst specializing in lead qualification.
            Analyze leads based on industry standards and provide actionable insights.""",
            'output_format': 'json'
        },
        'content_generation': {
            'system_message': """You are an expert marketing copywriter specializing in 
            personalized B2B content. Create engaging, conversion-focused content.""",
            'output_format': 'json'
        },
        'campaign_optimization': {
            'system_message': """You are an expert marketing strategist specializing in 
            campaign optimization. Analyze performance and provide data-driven recommendations.""",
            'output_format': 'json'
        }
    },
    
    # Monitoring and logging
    'monitoring': {
        'log_level': 'INFO',
        'track_usage': True,
        'track_performance': True
    },
    
    # Error handling
    'error_handling': {
        'fallback_enabled': True,
        'notification_threshold': 0.1,  # 10% error rate
        'critical_error_types': [
            'RateLimitError',
            'AuthenticationError',
            'ServiceUnavailableError'
        ]
    }
}
