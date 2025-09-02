class EpisodicMemory:
    """Successful interaction patterns storage"""
    def __init__(self):
        self.db_client = DatabaseClient("memory_db")
        
    async def store_successful_pattern(self, episode: dict):
        episode_id = f"ep_{uuid.uuid4().hex[:8]}"
        await self.db_client.insert("episodic_memory", {
            'episode_id': episode_id,
            'scenario': episode['scenario'],
            'action_sequence_json': json.dumps(episode.get('actions', [])),
            'outcome_score': episode['outcome_score'],
            'notes': episode.get('notes', '')
        })
        
    async def get_successful_patterns(self, **criteria) -> list:
        query = "SELECT * FROM episodic_memory WHERE outcome_score > 0.7"
        results = await self.db_client.query(query)
        return [
            {
                'episode_id': r['episode_id'],
                'scenario': r['scenario'],
                'actions': json.loads(r['action_sequence_json']),
                'outcome_score': r['outcome_score']
            }
            for r in results
        ]