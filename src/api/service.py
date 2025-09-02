from fastapi import FastAPI, HTTPException, Depends
from typing import Dict, List, Optional
from datetime import datetime
import uvicorn
import asyncio
from agents import LeadTriageAgent, EngagementAgent, CampaignOptimizationAgent
from memory import MemorySystem
from ai import OpenAIService, OpenAIUtils
from auth import get_current_user, User

app = FastAPI(
    title="Marketing Multi-Agent System API",
    description="AI-Enhanced Marketing Automation API",
    version="1.0.0"
)

# Initialize services
lead_triage_agent = LeadTriageAgent()
engagement_agent = EngagementAgent()
campaign_optimizer = CampaignOptimizationAgent()
ai_service = OpenAIService()

@app.post("/api/v1/leads/{lead_id}/triage")
async def triage_lead(
    lead_id: str,
    request: Dict,
    current_user: User = Depends(get_current_user)
):
    """
    Triage a lead using AI-enhanced analysis
    """
    try:
        # Get AI insights
        lead_data = await lead_triage_agent.mcp_client.get_lead(lead_id)
        ai_insights = await ai_service.analyze_lead(lead_data)
        
        # Enhance request with AI insights
        enhanced_request = {
            'lead_id': lead_id,
            'ai_insights': ai_insights,
            **request
        }
        
        result = await lead_triage_agent.categorize_lead(enhanced_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/campaigns/{campaign_id}/optimize")
async def optimize_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Optimize campaign using AI-driven insights
    """
    try:
        # Get campaign data and metrics
        campaign_data = await campaign_optimizer.mcp_client.get_campaign(campaign_id)
        campaign_metrics = await campaign_optimizer.mcp_client.get_campaign_metrics(campaign_id)
        
        # Get AI-driven optimization recommendations
        optimization_insights = await ai_service.optimize_campaign_strategy(
            campaign_data,
            campaign_metrics
        )
        
        # Apply optimizations
        result = await campaign_optimizer.analyze_campaign_performance(
            campaign_id,
            ai_recommendations=optimization_insights
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/content/generate")
async def generate_content(
    request: Dict,
    current_user: User = Depends(get_current_user)
):
    """
    Generate personalized content using AI
    """
    try:
        result = await ai_service.generate_personalized_content(
            lead_profile=request.get('lead_profile'),
            campaign_type=request.get('campaign_type'),
            tone=request.get('tone', 'professional')
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/agents/handoff")
async def handle_agent_handoff(
    request: Dict,
    current_user: User = Depends(get_current_user)
):
    """
    Handle agent handoff with context preservation
    """
    try:
        source_agent = _get_agent_by_id(request['from_agent'])
        target_agent = _get_agent_by_id(request['to_agent'])
        
        # Get AI-enhanced context
        ai_context = await ai_service.analyze_lead_context(request['context'])
        
        # Execute handoff with enhanced context
        success = await source_agent.handle_handoff({
            'target_agent': request['to_agent'],
            'lead_id': request['lead_id'],
            'conversation_id': request['conversation_id'],
            'context': request['context'],
            'ai_insights': ai_context
        })
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Handoff failed"
            )
            
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/insights/lead/{lead_id}")
async def get_lead_insights(
    lead_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-generated insights for a lead
    """
    try:
        lead_data = await lead_triage_agent.mcp_client.get_lead(lead_id)
        insights = await ai_service.analyze_lead(lead_data)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/insights/campaign/{campaign_id}")
async def get_campaign_insights(
    campaign_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-generated insights for a campaign
    """
    try:
        campaign_data = await campaign_optimizer.mcp_client.get_campaign(campaign_id)
        insights = await ai_service.optimize_campaign_strategy(
            campaign_data,
            await campaign_optimizer.mcp_client.get_campaign_metrics(campaign_id)
        )
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/insights/engagement/{lead_id}")
async def get_engagement_insights(
    lead_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-generated engagement insights for a lead
    """
    try:
        lead_data = await lead_triage_agent.mcp_client.get_lead(lead_id)
        engagement_history = await engagement_agent.get_engagement_history(lead_id)
        
        insights = await ai_service.analyze_engagement_patterns({
            'lead_data': lead_data,
            'engagement_history': engagement_history
        })
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _get_agent_by_id(agent_id: str):
    """Get agent instance by ID"""
    if agent_id == 'lead_triage':
        return lead_triage_agent
    elif agent_id == 'engagement':
        return engagement_agent
    elif agent_id == 'campaign_optimizer':
        return campaign_optimizer
    raise ValueError(f"Unknown agent: {agent_id}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
