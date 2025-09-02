class CampaignOptimizationAgent(BaseAgent):
    def __init__(self):
        super().__init__("campaign_optimizer", MCPClient("analytics_db"))
        
    async def analyze_campaign_performance(self, campaign_id: str) -> dict:
        """Analyze campaign performance and recommend optimizations"""
        
        # Get campaign metrics
        daily_metrics = await self.mcp_client.get_campaign_daily_metrics(campaign_id)
        conversion_data = await self.mcp_client.get_conversions(campaign_id)
        
        # Calculate key metrics
        performance_metrics = {
            'total_leads': sum(day['leads_created'] for day in daily_metrics),
            'total_conversions': len(conversion_data),
            'conversion_rate': len(conversion_data) / max(sum(day['leads_created'] for day in daily_metrics), 1),
            'roas': sum(day['roas'] for day in daily_metrics) / len(daily_metrics),
            'cpl': sum(day['cpl_usd'] for day in daily_metrics) / len(daily_metrics)
        }
        
        # Identify optimization opportunities
        optimizations = await self._identify_optimizations(
            campaign_id, performance_metrics, daily_metrics
        )
        
        # Check if escalation needed
        if performance_metrics['roas'] < 1.0 and performance_metrics['conversion_rate'] < 0.05:
            await self.escalate(
                "low_performance", 
                {
                    'campaign_id': campaign_id,
                    'metrics': performance_metrics,
                    'recommended_actions': optimizations
                }
            )
            
        return {
            'metrics': performance_metrics,
            'optimizations': optimizations,
            'status': 'escalated' if performance_metrics['roas'] < 1.0 else 'optimizing'
        }
        
    async def auto_optimize_campaign(self, campaign_id: str, optimization_type: str):
        """Automatically optimize campaign based on performance data"""
        
        if optimization_type == 'budget_reallocation':
            await self._reallocate_budget(campaign_id)
        elif optimization_type == 'audience_refinement':
            await self._refine_audience(campaign_id)
        elif optimization_type == 'creative_optimization':
            await self._optimize_creatives(campaign_id)
            
        # Log optimization action
        await self.mcp_client.log_agent_action({
            'action_type': 'optimize',
            'campaign_id': campaign_id,
            'optimization_type': optimization_type,
            'timestamp': datetime.now().isoformat()
        })