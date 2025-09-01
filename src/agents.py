"""
Multi-Agent Marketing System - Agent Classes
Production-ready agent implementations for lead triage, engagement, and campaign optimization
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnumJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle Enum types"""
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def enum_safe_asdict(obj):
    """Convert dataclass to dict with enum handling"""
    data = asdict(obj)
    return json.loads(json.dumps(data, cls=EnumJSONEncoder))

class AgentType(Enum):
    """Enumeration of agent types in the system"""
    LEAD_TRIAGE = "LeadTriage"
    ENGAGEMENT = "Engagement"
    CAMPAIGN_OPTIMIZER = "Optimizer"
    MANAGER = "Manager"

class ActionType(Enum):
    """Enumeration of action types agents can perform"""
    TRIAGE = "triage"
    OUTREACH = "outreach"
    OPTIMIZE = "optimize"
    HANDOFF = "handoff"
    ESCALATE = "escalate"
    PAUSE_CAMPAIGN = "pause_campaign"
    UPDATE_SEGMENT = "update_segment"

class EscalationReason(Enum):
    """Enumeration of escalation reasons"""
    NONE = "none"
    HIGH_VALUE = "high_value"
    COMPLAINT = "complaint"
    LEGAL = "legal"
    COMPLEX_REQUEST = "complex_request"

@dataclass
class HandoffContext:
    """Context information for agent handoffs"""
    summary: str
    confidence: float
    lead_id: str
    conversation_id: str
    previous_actions: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    timestamp: datetime

@dataclass
class AgentAction:
    """Represents an action taken by an agent"""
    action_id: str
    timestamp: datetime
    conversation_id: str
    lead_id: str
    action_type: ActionType
    source_agent: str
    source_agent_type: AgentType
    dest_agent_type: Optional[AgentType]
    handoff_context: Optional[HandoffContext]
    escalation_reason: EscalationReason
    result: Dict[str, Any]

class BaseAgent(ABC):
    """Abstract base class for all agents in the system"""
    
    def __init__(self, agent_id: str, agent_type: AgentType):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.active_conversations = {}
        self.performance_metrics = {}
        self.memory_system = None
        
    @abstractmethod
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an incoming request"""
        pass
    
    @abstractmethod
    async def handle_handoff(self, context: HandoffContext) -> Dict[str, Any]:
        """Handle a handoff from another agent"""
        pass
    
    def log_action(self, action: AgentAction):
        """Log an action taken by the agent"""
        logger.info(f"Agent {self.agent_id} performed action {action.action_type.value}")
        
    def update_performance_metrics(self, metric_name: str, value: float):
        """Update performance metrics for the agent"""
        if metric_name not in self.performance_metrics:
            self.performance_metrics[metric_name] = []
        self.performance_metrics[metric_name].append({
            'value': value,
            'timestamp': datetime.now()
        })

class LeadTriageAgent(BaseAgent):
    """
    Lead Triage Agent - Categorizes and scores incoming leads
    Implements sophisticated classification and routing logic
    """
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, AgentType.LEAD_TRIAGE)
        self.classification_model = None
        self.scoring_model = None
        self.triage_rules = self._load_triage_rules()
        
    def _load_triage_rules(self) -> Dict[str, Any]:
        """Load triage rules and thresholds"""
        return {
            'high_value_threshold': 80,
            'qualified_threshold': 60,
            'auto_escalate_industries': ['Legal', 'Healthcare'],
            'priority_regions': ['US', 'EU'],
            'company_size_weights': {
                '5000+': 1.0,
                '1001-5000': 0.8,
                '201-1000': 0.6,
                '51-200': 0.4,
                '11-50': 0.2,
                '1-10': 0.1
            }
        }
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process lead triage request"""
        try:
            lead_data = request.get('lead_data', {})
            
            # Perform lead classification
            triage_category = await self._classify_lead(lead_data)
            
            # Calculate lead score
            lead_score = await self._calculate_lead_score(lead_data)
            
            # Determine routing
            routing_decision = await self._determine_routing(lead_data, triage_category, lead_score)
            
            # Create action record
            action = AgentAction(
                action_id=f"ACT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                conversation_id=request.get('conversation_id', ''),
                lead_id=lead_data.get('lead_id', ''),
                action_type=ActionType.TRIAGE,
                source_agent=self.agent_id,
                source_agent_type=self.agent_type,
                dest_agent_type=routing_decision.get('dest_agent_type'),
                handoff_context=None,
                escalation_reason=EscalationReason.NONE,
                result={
                    'triage_category': triage_category,
                    'lead_score': lead_score,
                    'routing_decision': routing_decision
                }
            )
            
            self.log_action(action)
            
            return {
                'status': 'success',
                'triage_category': triage_category,
                'lead_score': lead_score,
                'routing_decision': {
                    'dest_agent_type': routing_decision['dest_agent_type'].value,
                    'priority': routing_decision['priority'],
                    'reason': routing_decision['reason']
                },
                'action': enum_safe_asdict(action)
            }
            
        except Exception as e:
            logger.error(f"Error in lead triage: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def _classify_lead(self, lead_data: Dict[str, Any]) -> str:
        """Classify lead into categories"""
        # Extract features for classification
        source = lead_data.get('source', '')
        industry = lead_data.get('industry', '')
        company_size = lead_data.get('company_size', '')
        persona = lead_data.get('persona', '')
        
        # Rule-based classification logic
        if source in ['Google Ads', 'Website'] and persona in ['Founder', 'CMO']:
            return 'Campaign Qualified'
        elif industry in self.triage_rules['auto_escalate_industries']:
            return 'General Inquiry'
        elif company_size in ['5000+', '1001-5000']:
            return 'Campaign Qualified'
        else:
            return 'Cold Lead'
    
    async def _calculate_lead_score(self, lead_data: Dict[str, Any]) -> float:
        """Calculate lead score based on multiple factors"""
        score = 0.0
        
        # Company size scoring
        company_size = lead_data.get('company_size', '')
        score += self.triage_rules['company_size_weights'].get(company_size, 0.1) * 30
        
        # Industry scoring
        industry = lead_data.get('industry', '')
        high_value_industries = ['SaaS', 'FinTech', 'HealthTech']
        if industry in high_value_industries:
            score += 25
        
        # Persona scoring
        persona = lead_data.get('persona', '')
        decision_maker_personas = ['Founder', 'CMO', 'CTO']
        if persona in decision_maker_personas:
            score += 20
        
        # Region scoring
        region = lead_data.get('region', '')
        if region in self.triage_rules['priority_regions']:
            score += 15
        
        # Source scoring
        source = lead_data.get('source', '')
        high_intent_sources = ['Website', 'Referral']
        if source in high_intent_sources:
            score += 10
        
        return min(score, 100.0)  # Cap at 100
    
    async def _determine_routing(self, lead_data: Dict[str, Any], 
                                triage_category: str, lead_score: float) -> Dict[str, Any]:
        """Determine routing based on triage results"""
        if lead_score >= self.triage_rules['high_value_threshold']:
            return {
                'dest_agent_type': AgentType.ENGAGEMENT,
                'priority': 'high',
                'reason': 'high_value_lead'
            }
        elif triage_category == 'Campaign Qualified':
            return {
                'dest_agent_type': AgentType.ENGAGEMENT,
                'priority': 'medium',
                'reason': 'qualified_lead'
            }
        else:
            return {
                'dest_agent_type': AgentType.ENGAGEMENT,
                'priority': 'low',
                'reason': 'nurture_lead'
            }
    
    async def handle_handoff(self, context: HandoffContext) -> Dict[str, Any]:
        """Handle handoff from another agent"""
        # Re-evaluate lead based on new context
        return await self.process_request({
            'lead_data': context.metadata,
            'conversation_id': context.conversation_id
        })

class EngagementAgent(BaseAgent):
    """
    Engagement Agent - Manages personalized outreach and communication
    Handles multi-channel engagement with context preservation
    """
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, AgentType.ENGAGEMENT)
        self.communication_templates = self._load_communication_templates()
        self.channel_preferences = {}
        self.engagement_history = {}
        
    def _load_communication_templates(self) -> Dict[str, Dict[str, str]]:
        """Load communication templates for different scenarios"""
        return {
            'welcome': {
                'email': "Welcome to Purple Merit! We're excited to help you optimize your marketing funnel.",
                'sms': "Welcome to Purple Merit! Let's boost your marketing ROI.",
                'social': "Thanks for connecting! Ready to transform your marketing?"
            },
            'follow_up': {
                'email': "Following up on our previous conversation about your marketing goals.",
                'sms': "Quick follow-up on your marketing optimization needs.",
                'social': "Checking in on your marketing transformation journey."
            },
            'demo_invite': {
                'email': "Ready to see Purple Merit in action? Let's schedule a personalized demo.",
                'sms': "Book your Purple Merit demo: [link]",
                'social': "See Purple Merit in action - book your demo today!"
            }
        }
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process engagement request"""
        try:
            lead_data = request.get('lead_data', {})
            engagement_type = request.get('engagement_type', 'welcome')
            
            # Determine optimal channel
            optimal_channel = await self._determine_optimal_channel(lead_data)
            
            # Generate personalized content
            content = await self._generate_personalized_content(
                lead_data, engagement_type, optimal_channel
            )
            
            # Schedule engagement
            engagement_result = await self._execute_engagement(
                lead_data, optimal_channel, content
            )
            
            # Create action record
            action = AgentAction(
                action_id=f"ACT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                conversation_id=request.get('conversation_id', ''),
                lead_id=lead_data.get('lead_id', ''),
                action_type=ActionType.OUTREACH,
                source_agent=self.agent_id,
                source_agent_type=self.agent_type,
                dest_agent_type=None,
                handoff_context=None,
                escalation_reason=EscalationReason.NONE,
                result={
                    'channel': optimal_channel,
                    'content': content,
                    'engagement_result': engagement_result
                }
            )
            
            self.log_action(action)
            
            return {
                'status': 'success',
                'channel': optimal_channel,
                'content': content,
                'engagement_result': engagement_result,
                'action': enum_safe_asdict(action)
            }
            
        except Exception as e:
            logger.error(f"Error in engagement: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def _determine_optimal_channel(self, lead_data: Dict[str, Any]) -> str:
        """Determine optimal communication channel"""
        preferred_channel = lead_data.get('preferred_channel', 'Email')
        
        # Channel optimization logic based on lead characteristics
        persona = lead_data.get('persona', '')
        region = lead_data.get('region', '')
        
        if persona in ['Founder', 'CMO'] and region in ['US', 'EU']:
            return 'Email'  # Professional preference
        elif persona == 'Marketing Manager':
            return 'Social'  # Social media engagement
        else:
            return preferred_channel.lower()
    
    async def _generate_personalized_content(self, lead_data: Dict[str, Any], 
                                           engagement_type: str, channel: str) -> str:
        """Generate personalized content for engagement"""
        base_template = self.communication_templates.get(engagement_type, {}).get(channel, '')
        
        # Personalization variables
        company_size = lead_data.get('company_size', '')
        industry = lead_data.get('industry', '')
        persona = lead_data.get('persona', '')
        
        # Add personalization
        personalized_content = base_template
        
        if industry:
            personalized_content += f" We've helped many {industry} companies achieve their goals."
        
        if company_size in ['5000+', '1001-5000']:
            personalized_content += " Our enterprise solutions are perfect for organizations of your size."
        
        return personalized_content
    
    async def _execute_engagement(self, lead_data: Dict[str, Any], 
                                channel: str, content: str) -> Dict[str, Any]:
        """Execute the engagement action"""
        # Simulate engagement execution
        lead_id = lead_data.get('lead_id', '')
        
        # Record engagement in history
        if lead_id not in self.engagement_history:
            self.engagement_history[lead_id] = []
        
        engagement_record = {
            'timestamp': datetime.now(),
            'channel': channel,
            'content': content,
            'status': 'sent'
        }
        
        self.engagement_history[lead_id].append(engagement_record)
        
        return {
            'status': 'sent',
            'timestamp': datetime.now().isoformat(),
            'channel': channel,
            'message_id': f"MSG_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
    
    async def handle_handoff(self, context: HandoffContext) -> Dict[str, Any]:
        """Handle handoff from another agent"""
        # Process engagement based on handoff context
        return await self.process_request({
            'lead_data': context.metadata,
            'conversation_id': context.conversation_id,
            'engagement_type': 'follow_up'
        })

class CampaignOptimizationAgent(BaseAgent):
    """
    Campaign Optimization Agent - Monitors and optimizes campaign performance
    Implements data-driven optimization strategies
    """
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, AgentType.CAMPAIGN_OPTIMIZER)
        self.optimization_rules = self._load_optimization_rules()
        self.performance_thresholds = self._load_performance_thresholds()
        self.campaign_data = {}
        
    def _load_optimization_rules(self) -> Dict[str, Any]:
        """Load campaign optimization rules"""
        return {
            'min_statistical_significance': 0.95,
            'min_sample_size': 100,
            'performance_check_interval': 3600,  # 1 hour
            'auto_pause_threshold': 0.1,  # 10% of budget with no conversions
            'scale_up_threshold': 2.0,  # 2x ROAS
            'scale_down_threshold': 0.5  # 0.5x ROAS
        }
    
    def _load_performance_thresholds(self) -> Dict[str, float]:
        """Load performance thresholds for different metrics"""
        return {
            'ctr_threshold': 0.02,  # 2% CTR
            'cpl_threshold': 50.0,  # $50 CPL
            'roas_threshold': 1.5,  # 1.5x ROAS
            'conversion_rate_threshold': 0.05  # 5% conversion rate
        }
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process campaign optimization request"""
        try:
            campaign_data = request.get('campaign_data', {})
            optimization_type = request.get('optimization_type', 'performance_check')
            
            if optimization_type == 'performance_check':
                result = await self._analyze_campaign_performance(campaign_data)
            elif optimization_type == 'ab_test_analysis':
                result = await self._analyze_ab_test(campaign_data)
            elif optimization_type == 'budget_optimization':
                result = await self._optimize_budget_allocation(campaign_data)
            else:
                result = {'status': 'unknown_optimization_type'}
            
            # Create action record
            action = AgentAction(
                action_id=f"ACT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                conversation_id=request.get('conversation_id', ''),
                lead_id='',  # Campaign optimization doesn't have specific lead
                action_type=ActionType.OPTIMIZE,
                source_agent=self.agent_id,
                source_agent_type=self.agent_type,
                dest_agent_type=None,
                handoff_context=None,
                escalation_reason=EscalationReason.NONE,
                result=result
            )
            
            self.log_action(action)
            
            return {
                'status': 'success',
                'optimization_result': result,
                'action': enum_safe_asdict(action)
            }
            
        except Exception as e:
            logger.error(f"Error in campaign optimization: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def _analyze_campaign_performance(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze campaign performance and recommend actions"""
        campaign_id = campaign_data.get('campaign_id', '')
        
        # Extract performance metrics
        ctr = campaign_data.get('ctr', 0.0)
        cpl = campaign_data.get('cpl_usd', 0.0)
        roas = campaign_data.get('roas', 0.0)
        conversions = campaign_data.get('conversions', 0)
        cost = campaign_data.get('cost_usd', 0.0)
        
        recommendations = []
        
        # CTR analysis
        if ctr < self.performance_thresholds['ctr_threshold']:
            recommendations.append({
                'type': 'creative_optimization',
                'priority': 'high',
                'message': f'CTR ({ctr:.3f}) below threshold. Consider testing new ad creatives.'
            })
        
        # CPL analysis
        if cpl > self.performance_thresholds['cpl_threshold']:
            recommendations.append({
                'type': 'targeting_optimization',
                'priority': 'medium',
                'message': f'CPL (${cpl:.2f}) above threshold. Review targeting parameters.'
            })
        
        # ROAS analysis
        if roas < self.performance_thresholds['roas_threshold']:
            recommendations.append({
                'type': 'budget_reallocation',
                'priority': 'high',
                'message': f'ROAS ({roas:.2f}) below threshold. Consider budget reallocation.'
            })
        
        # Auto-pause check
        if conversions == 0 and cost > campaign_data.get('daily_budget_usd', 0) * 0.1:
            recommendations.append({
                'type': 'auto_pause',
                'priority': 'critical',
                'message': 'No conversions with significant spend. Consider pausing campaign.'
            })
        
        return {
            'campaign_id': campaign_id,
            'performance_score': self._calculate_performance_score(campaign_data),
            'recommendations': recommendations,
            'metrics_analysis': {
                'ctr': {'value': ctr, 'status': 'good' if ctr >= self.performance_thresholds['ctr_threshold'] else 'poor'},
                'cpl': {'value': cpl, 'status': 'good' if cpl <= self.performance_thresholds['cpl_threshold'] else 'poor'},
                'roas': {'value': roas, 'status': 'good' if roas >= self.performance_thresholds['roas_threshold'] else 'poor'}
            }
        }
    
    def _calculate_performance_score(self, campaign_data: Dict[str, Any]) -> float:
        """Calculate overall performance score for campaign"""
        ctr = campaign_data.get('ctr', 0.0)
        roas = campaign_data.get('roas', 0.0)
        conversions = campaign_data.get('conversions', 0)
        
        # Weighted scoring
        ctr_score = min(ctr / self.performance_thresholds['ctr_threshold'], 1.0) * 30
        roas_score = min(roas / self.performance_thresholds['roas_threshold'], 1.0) * 50
        conversion_score = min(conversions / 10, 1.0) * 20  # Normalize to 10 conversions
        
        return ctr_score + roas_score + conversion_score
    
    async def _analyze_ab_test(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze A/B test results for statistical significance"""
        variants = campaign_data.get('variants', [])
        
        if len(variants) < 2:
            return {'status': 'insufficient_variants'}
        
        # Simple A/B test analysis (would use proper statistical tests in production)
        best_variant = max(variants, key=lambda x: x.get('conversion_rate', 0))
        
        return {
            'winner': best_variant,
            'confidence': 0.95,  # Placeholder
            'recommendation': f"Scale variant {best_variant.get('variant_id')} - highest conversion rate"
        }
    
    async def _optimize_budget_allocation(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize budget allocation across channels"""
        channels = campaign_data.get('channel_performance', {})
        
        # Calculate efficiency scores
        efficiency_scores = {}
        for channel, metrics in channels.items():
            roas = metrics.get('roas', 0)
            efficiency_scores[channel] = roas
        
        # Recommend budget reallocation
        total_budget = campaign_data.get('total_budget_usd', 0)
        recommendations = {}
        
        for channel, score in efficiency_scores.items():
            if score > self.optimization_rules['scale_up_threshold']:
                recommendations[channel] = 'increase_budget'
            elif score < self.optimization_rules['scale_down_threshold']:
                recommendations[channel] = 'decrease_budget'
            else:
                recommendations[channel] = 'maintain_budget'
        
        return {
            'efficiency_scores': efficiency_scores,
            'budget_recommendations': recommendations
        }
    
    async def handle_handoff(self, context: HandoffContext) -> Dict[str, Any]:
        """Handle handoff from another agent"""
        # Process optimization based on handoff context
        return await self.process_request({
            'campaign_data': context.metadata,
            'conversation_id': context.conversation_id,
            'optimization_type': 'performance_check'
        })

class AgentOrchestrator:
    """
    Agent Orchestrator - Manages agent interactions and handoffs
    Implements the coordination logic for the multi-agent system
    """
    
    def __init__(self):
        self.agents = {}
        self.handoff_rules = self._load_handoff_rules()
        self.active_conversations = {}
        
    def _load_handoff_rules(self) -> Dict[str, Any]:
        """Load rules for agent handoffs"""
        return {
            'triage_to_engagement': {
                'conditions': ['lead_classified', 'score_calculated'],
                'timeout': 300  # 5 minutes
            },
            'engagement_to_optimizer': {
                'conditions': ['campaign_performance_issue'],
                'timeout': 600  # 10 minutes
            },
            'escalation_to_manager': {
                'conditions': ['high_value_lead', 'complaint', 'legal_issue'],
                'timeout': 60  # 1 minute
            }
        }
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.agent_id] = agent
        logger.info(f"Registered agent {agent.agent_id} of type {agent.agent_type.value}")
    
    async def route_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to appropriate agent"""
        request_type = request.get('type', '')
        
        if request_type == 'lead_triage':
            return await self._route_to_triage_agent(request)
        elif request_type == 'engagement':
            return await self._route_to_engagement_agent(request)
        elif request_type == 'campaign_optimization':
            return await self._route_to_optimization_agent(request)
        else:
            return {'status': 'error', 'message': 'Unknown request type'}
    
    async def _route_to_triage_agent(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to available triage agent"""
        triage_agents = [agent for agent in self.agents.values() 
                        if agent.agent_type == AgentType.LEAD_TRIAGE]
        
        if not triage_agents:
            return {'status': 'error', 'message': 'No triage agents available'}
        
        # Simple round-robin selection (would implement load balancing in production)
        selected_agent = triage_agents[0]
        return await selected_agent.process_request(request)
    
    async def _route_to_engagement_agent(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to available engagement agent"""
        engagement_agents = [agent for agent in self.agents.values() 
                           if agent.agent_type == AgentType.ENGAGEMENT]
        
        if not engagement_agents:
            return {'status': 'error', 'message': 'No engagement agents available'}
        
        selected_agent = engagement_agents[0]
        return await selected_agent.process_request(request)
    
    async def _route_to_optimization_agent(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to available optimization agent"""
        optimization_agents = [agent for agent in self.agents.values() 
                             if agent.agent_type == AgentType.CAMPAIGN_OPTIMIZER]
        
        if not optimization_agents:
            return {'status': 'error', 'message': 'No optimization agents available'}
        
        selected_agent = optimization_agents[0]
        return await selected_agent.process_request(request)
    
    async def execute_handoff(self, source_agent_id: str, dest_agent_type: AgentType, 
                            context: HandoffContext) -> Dict[str, Any]:
        """Execute handoff between agents"""
        dest_agents = [agent for agent in self.agents.values() 
                      if agent.agent_type == dest_agent_type]
        
        if not dest_agents:
            return {'status': 'error', 'message': f'No {dest_agent_type.value} agents available'}
        
        # Select destination agent (simple selection for demo)
        dest_agent = dest_agents[0]
        
        # Execute handoff
        result = await dest_agent.handle_handoff(context)
        
        logger.info(f"Handoff executed from {source_agent_id} to {dest_agent.agent_id}")
        
        return result

# Factory function to create agents
def create_agent_system() -> Tuple[AgentOrchestrator, Dict[str, BaseAgent]]:
    """Create and configure the multi-agent system"""
    orchestrator = AgentOrchestrator()
    
    # Create agents
    triage_agent = LeadTriageAgent("LT-001")
    engagement_agent = EngagementAgent("EN-001")
    optimization_agent = CampaignOptimizationAgent("OP-001")
    
    # Register agents
    orchestrator.register_agent(triage_agent)
    orchestrator.register_agent(engagement_agent)
    orchestrator.register_agent(optimization_agent)
    
    agents = {
        'triage': triage_agent,
        'engagement': engagement_agent,
        'optimization': optimization_agent
    }
    
    return orchestrator, agents

