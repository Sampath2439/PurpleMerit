import asyncio
from typing import Any, Callable, Dict
import tenacity
from openai import AsyncOpenAI, APIError, RateLimitError
import logging
from .config import OPENAI_CONFIG

logger = logging.getLogger(__name__)

class OpenAIUtils:
    @staticmethod
    def create_retry_decorator():
        """Create a retry decorator with configured parameters"""
        return tenacity.retry(
            stop=tenacity.stop_after_attempt(
                OPENAI_CONFIG['retry']['max_attempts']
            ),
            wait=tenacity.wait_exponential(
                multiplier=OPENAI_CONFIG['retry']['initial_delay'],
                max=OPENAI_CONFIG['retry']['max_delay'],
                exp_base=OPENAI_CONFIG['retry']['backoff_factor']
            ),
            retry=tenacity.retry_if_exception_type(
                (APIError, RateLimitError)
            ),
            before=tenacity.before_log(logger, logging.INFO),
            after=tenacity.after_log(logger, logging.INFO),
            reraise=True
        )

    @staticmethod
    async def with_retry(func: Callable, *args, **kwargs) -> Any:
        """Execute a function with retry logic"""
        retry_decorator = OpenAIUtils.create_retry_decorator()
        
        @retry_decorator
        async def wrapped_func():
            return await func(*args, **kwargs)
            
        return await wrapped_func()

    @staticmethod
    def format_messages(
        system_message: str,
        user_message: str,
        additional_context: Dict[str, Any] = None
    ) -> list:
        """Format messages for OpenAI API"""
        messages = [{
            "role": "system",
            "content": system_message
        }]
        
        if additional_context:
            messages.append({
                "role": "system",
                "content": f"Additional context: {str(additional_context)}"
            })
            
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages

    @staticmethod
    def get_model_config(operation_type: str) -> Dict[str, Any]:
        """Get model configuration for specific operation type"""
        return {
            'model': OPENAI_CONFIG['models'][operation_type],
            'temperature': OPENAI_CONFIG['temperature'][operation_type],
            'max_tokens': OPENAI_CONFIG['max_tokens'][operation_type]
        }

    @staticmethod
    def validate_response(response: Dict[str, Any]) -> bool:
        """Validate OpenAI API response"""
        required_fields = ['choices']
        return all(field in response for field in required_fields)

class OpenAIRateLimiter:
    def __init__(self):
        self.requests_per_minute = OPENAI_CONFIG['rate_limits']['requests_per_minute']
        self.tokens_per_minute = OPENAI_CONFIG['rate_limits']['tokens_per_minute']
        self.request_timestamps = []
        self.token_usage = []
        
    async def acquire(self, tokens: int):
        """Acquire rate limit permission"""
        await self._cleanup_old_entries()
        
        if not self._check_limits(tokens):
            wait_time = self._calculate_wait_time()
            await asyncio.sleep(wait_time)
            
        self._record_usage(tokens)
        
    def _check_limits(self, tokens: int) -> bool:
        """Check if current usage is within limits"""
        current_time = asyncio.get_event_loop().time()
        minute_ago = current_time - 60
        
        recent_requests = sum(1 for ts in self.request_timestamps if ts > minute_ago)
        recent_tokens = sum(t for t, ts in self.token_usage if ts > minute_ago)
        
        return (recent_requests < self.requests_per_minute and
                recent_tokens + tokens <= self.tokens_per_minute)
                
    def _record_usage(self, tokens: int):
        """Record API usage"""
        current_time = asyncio.get_event_loop().time()
        self.request_timestamps.append(current_time)
        self.token_usage.append((tokens, current_time))
        
    async def _cleanup_old_entries(self):
        """Clean up entries older than 1 minute"""
        current_time = asyncio.get_event_loop().time()
        minute_ago = current_time - 60
        
        self.request_timestamps = [ts for ts in self.request_timestamps if ts > minute_ago]
        self.token_usage = [(t, ts) for t, ts in self.token_usage if ts > minute_ago]
        
    def _calculate_wait_time(self) -> float:
        """Calculate time to wait before next request"""
        current_time = asyncio.get_event_loop().time()
        minute_ago = current_time - 60
        
        oldest_request = min(self.request_timestamps) if self.request_timestamps else minute_ago
        return max(0, oldest_request + 60 - current_time)

class OpenAICache:
    def __init__(self):
        self.cache = {}
        self.ttl = OPENAI_CONFIG['cache']['ttl']
        self.max_size = OPENAI_CONFIG['cache']['max_size']
        
    async def get(self, key: str) -> Any:
        """Get value from cache"""
        if key in self.cache:
            entry = self.cache[key]
            if asyncio.get_event_loop().time() < entry['expires_at']:
                return entry['value']
            else:
                del self.cache[key]
        return None
        
    async def set(self, key: str, value: Any):
        """Set value in cache"""
        current_time = asyncio.get_event_loop().time()
        
        # Clean up expired entries
        await self._cleanup()
        
        # If at max size, remove oldest entry
        if len(self.cache) >= self.max_size:
            oldest_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k]['expires_at']
            )
            del self.cache[oldest_key]
            
        self.cache[key] = {
            'value': value,
            'expires_at': current_time + self.ttl
        }
        
    async def _cleanup(self):
        """Remove expired entries"""
        current_time = asyncio.get_event_loop().time()
        expired_keys = [
            k for k, v in self.cache.items()
            if v['expires_at'] <= current_time
        ]
        for k in expired_keys:
            del self.cache[k]
