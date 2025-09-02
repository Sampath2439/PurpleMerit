class ShortTermMemory:
    """TTL-based conversation context storage"""
    def __init__(self, ttl_hours: int = 24):
        self.storage = {}
        self.ttl_hours = ttl_hours
        
    async def store(self, key: str, data: dict, ttl: int = None):
        expires_at = datetime.now() + timedelta(hours=ttl or self.ttl_hours)
        self.storage[key] = {
            'data': data,
            'expires_at': expires_at
        }
        
    async def get(self, key: str) -> dict:
        if key in self.storage:
            if datetime.now() < self.storage[key]['expires_at']:
                return self.storage[key]['data']
            else:
                del self.storage[key]
        return None
        