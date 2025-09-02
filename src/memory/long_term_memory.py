class LongTermMemory:
    """Persistent customer profiles and preferences"""
    def __init__(self):
        self.db_client = DatabaseClient("memory_db")
        
    async def store_preferences(self, lead_id: str, preferences: dict):
        await self.db_client.upsert("long_term_memory", {
            'lead_id': lead_id,
            'preferences_json': json.dumps(preferences),
            'last_updated_at': datetime.now().isoformat()
        })
        
    async def get_preferences(self, lead_id: str) -> dict:
        result = await self.db_client.query(
            "SELECT preferences_json FROM long_term_memory WHERE lead_id = ?",
            [lead_id]
        )
        if result:
            return json.loads(result[0]['preferences_json'])
        return {}