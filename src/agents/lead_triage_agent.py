class LeadTriageAgent(BaseAgent):
    def __init__(self):
        super().__init__("lead_triage", MCPClient("marketing_db"))
        
    async def categorize_lead(self, lead_data: dict) -> dict:
        """
        Categorize lead using ML model and historical patterns
        Returns: {category, confidence, recommended_actions}
        """
        # Extract features from lead data
        features = self._extract_features(lead_data)
        
        # Get historical patterns from episodic memory
        patterns = await self.memory.episodic.get_similar_scenarios(features)
        
        # Apply ML classification model
        category = self._classify_lead(features, patterns)
        
        # Update short-term memory for conversation context
        await self.memory.short_term.store(lead_data['lead_id'], {
            'category': category,
            'features': features,
            'timestamp': datetime.now().isoformat()
        })
        
        return category
        
    async def score_lead(self, lead_id: str) -> int:
        """Calculate lead score 0-100 based on multiple factors"""
        lead_data = await self.mcp_client.get_lead(lead_id)
        long_term_data = await self.memory.long_term.get(lead_id)
        
        score_factors = {
            'company_size': self._score_company_size(lead_data.get('company_size')),
            'industry': self._score_industry(lead_data.get('industry')),
            'engagement_history': self._score_engagement(long_term_data),
            'source_quality': self._score_source(lead_data.get('source'))
        }
        
        final_score = sum(score_factors.values()) // len(score_factors)
        
        # Update lead score in database via MCP
        await self.mcp_client.update_lead_score(lead_id, final_score)
        
        return final_score