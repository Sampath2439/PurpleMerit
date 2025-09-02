from typing import Dict, Any, List
from datetime import datetime
import json
from .short_term_memory import ShortTermMemory
from .long_term_memory import LongTermMemory
from .episodic_memory import EpisodicMemory
from .semantic_memory import SemanticMemory

class MemorySystem:
    def __init__(self, agent_id: str):
        """Initialize memory subsystems"""
        self.agent_id = agent_id
        self.short_term = ShortTermMemory(agent_id)
        self.long_term = LongTermMemory(agent_id)
        self.episodic = EpisodicMemory(agent_id)
        self.semantic = SemanticMemory(agent_id)
        
    async def consolidate_memories(self):
        """
        Consolidate short-term memories into long-term storage
        using importance scoring and pattern recognition
        """
        # Get recent short-term memories
        recent_memories = await self.short_term.get_recent()
        
        # Score memories for importance
        scored_memories = await self._score_memories(recent_memories)
        
        # Filter and consolidate important memories
        for memory in scored_memories:
            if memory['importance_score'] > 0.7:
                # Store in long-term memory
                await self.long_term.store(
                    key=f"{memory['type']}_{memory['id']}",
                    value=memory['data']
                )
                
                # Extract patterns for episodic memory
                if memory['type'] == 'interaction':
                    await self.episodic.store_pattern(memory['data'])
                    
                # Update semantic knowledge graph
                await self.semantic.update_knowledge(memory['data'])
                
        # Cleanup consolidated short-term memories
        await self.short_term.cleanup_old()
        
    async def _score_memories(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score memories based on importance factors"""
        scored = []
        for memory in memories:
            score = await self._calculate_importance(memory)
            scored.append({
                **memory,
                'importance_score': score
            })
        return sorted(scored, key=lambda x: x['importance_score'], reverse=True)
        
    async def _calculate_importance(self, memory: Dict[str, Any]) -> float:
        """Calculate memory importance score"""
        score = 0.0
        
        # Emotional impact
        if 'sentiment' in memory:
            score += abs(memory['sentiment']) * 0.3
            
        # Novelty factor
        similar_memories = await self.long_term.find_similar(memory['data'])
        novelty_score = 1.0 - (len(similar_memories) / 10)  # Normalize
        score += novelty_score * 0.2
        
        # Business impact
        if 'metrics' in memory['data']:
            metrics = memory['data']['metrics']
            if 'revenue_impact' in metrics:
                score += min(metrics['revenue_impact'] / 10000, 1.0) * 0.3
            if 'lead_score' in metrics:
                score += metrics['lead_score'] * 0.2
                
        return min(score, 1.0)  # Normalize to 0-1
        
    async def retrieve_relevant_context(
        self,
        query: Dict[str, Any],
        memory_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve relevant context from all memory systems
        """
        if memory_types is None:
            memory_types = ['short_term', 'long_term', 'episodic', 'semantic']
            
        results = {}
        
        # Query each specified memory system
        for memory_type in memory_types:
            if memory_type == 'short_term':
                results['short_term'] = await self.short_term.search(query)
            elif memory_type == 'long_term':
                results['long_term'] = await self.long_term.search(query)
            elif memory_type == 'episodic':
                results['episodic'] = await self.episodic.find_patterns(query)
            elif memory_type == 'semantic':
                results['semantic'] = await self.semantic.query_knowledge(query)
                
        return results
