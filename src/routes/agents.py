"""
Multi-Agent Marketing System - Agent API Routes
Flask blueprint for agent-related API endpoints
"""

import json
import asyncio
from datetime import datetime
from flask import Blueprint, request, jsonify
from typing import Dict, Any
import logging

# Import agent classes
from agents import (
    create_agent_system, AgentType, ActionType, EscalationReason,
    HandoffContext, AgentAction, enum_safe_asdict
)
from mcp.mcp_server import create_mcp_server
from utils.data_processing import DataProcessor, MLPipeline, AgentMemorySystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
agents_bp = Blueprint('agents', __name__)

# Global variables for system components
orchestrator = None
agents = None
mcp_server = None
data_processor = None
ml_pipeline = None
memory_system = None

def initialize_system():
    """Initialize the multi-agent system components"""
    global orchestrator, agents, mcp_server, data_processor, ml_pipeline, memory_system
    
    if orchestrator is None:
        # Create agent system
        orchestrator, agents = create_agent_system()
        
        # Create MCP server
        mcp_server = create_mcp_server()
        
        # Create data processor and ML pipeline
        data_processor = DataProcessor(data_path="./data/")
        ml_pipeline = MLPipeline()
        
        # Create memory system
        memory_system = AgentMemorySystem()
        
        logger.info("Multi-agent system initialized successfully")

@agents_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    initialize_system()
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'agents': {
            'triage': agents['triage'].agent_id if agents else None,
            'engagement': agents['engagement'].agent_id if agents else None,
            'optimization': agents['optimization'].agent_id if agents else None
        },
        'mcp_server': 'active' if mcp_server else 'inactive'
    })

@agents_bp.route('/triage', methods=['POST'])
def triage_lead():
    """Endpoint for lead triage requests"""
    try:
        initialize_system()
        
        # Get request data
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({'error': 'No request data provided'}), 400
        
        # Prepare request for triage agent
        triage_request = {
            'type': 'lead_triage',
            'lead_data': request_data.get('lead_data', {}),
            'conversation_id': request_data.get('conversation_id', f"C{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        }
        
        # Process request through orchestrator
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(orchestrator.route_request(triage_request))
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in triage endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/engage', methods=['POST'])
def engage_lead():
    """Endpoint for lead engagement requests"""
    try:
        initialize_system()
        
        # Get request data
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({'error': 'No request data provided'}), 400
        
        # Prepare request for engagement agent
        engagement_request = {
            'type': 'engagement',
            'lead_data': request_data.get('lead_data', {}),
            'engagement_type': request_data.get('engagement_type', 'welcome'),
            'conversation_id': request_data.get('conversation_id', f"C{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        }
        
        # Process request through orchestrator
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(orchestrator.route_request(engagement_request))
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in engagement endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/optimize', methods=['POST'])
def optimize_campaign():
    """Endpoint for campaign optimization requests"""
    try:
        initialize_system()
        
        # Get request data
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({'error': 'No request data provided'}), 400
        
        # Prepare request for optimization agent
        optimization_request = {
            'type': 'campaign_optimization',
            'campaign_data': request_data.get('campaign_data', {}),
            'optimization_type': request_data.get('optimization_type', 'performance_check'),
            'conversation_id': request_data.get('conversation_id', f"C{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        }
        
        # Process request through orchestrator
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(orchestrator.route_request(optimization_request))
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in optimization endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/handoff', methods=['POST'])
def execute_handoff():
    """Endpoint for executing agent handoffs"""
    try:
        initialize_system()
        
        # Get request data
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({'error': 'No request data provided'}), 400
        
        # Create handoff context
        context = HandoffContext(
            summary=request_data.get('summary', ''),
            confidence=request_data.get('confidence', 0.5),
            lead_id=request_data.get('lead_id', ''),
            conversation_id=request_data.get('conversation_id', ''),
            previous_actions=request_data.get('previous_actions', []),
            metadata=request_data.get('metadata', {}),
            timestamp=datetime.now()
        )
        
        # Execute handoff
        source_agent_id = request_data.get('source_agent_id', '')
        dest_agent_type = AgentType(request_data.get('dest_agent_type', 'Engagement'))
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            orchestrator.execute_handoff(source_agent_id, dest_agent_type, context)
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in handoff endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/memory/store', methods=['POST'])
def store_memory():
    """Endpoint for storing agent memory"""
    try:
        initialize_system()
        
        # Get request data
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({'error': 'No request data provided'}), 400
        
        memory_type = request_data.get('memory_type', 'short_term')
        
        if memory_type == 'short_term':
            memory_system.store_short_term(
                conversation_id=request_data.get('conversation_id', ''),
                context=request_data.get('context', {}),
                ttl_hours=request_data.get('ttl_hours', 24)
            )
        elif memory_type == 'long_term':
            memory_system.update_long_term(
                lead_id=request_data.get('lead_id', ''),
                preferences=request_data.get('preferences', {}),
                rfm_score=request_data.get('rfm_score', 0.5)
            )
        elif memory_type == 'episodic':
            memory_system.store_episode(
                scenario=request_data.get('scenario', ''),
                actions=request_data.get('actions', []),
                outcome_score=request_data.get('outcome_score', 0.5),
                notes=request_data.get('notes', '')
            )
        elif memory_type == 'semantic':
            memory_system.update_semantic_knowledge(
                subject=request_data.get('subject', ''),
                predicate=request_data.get('predicate', ''),
                object_val=request_data.get('object', ''),
                weight=request_data.get('weight', 1.0)
            )
        else:
            return jsonify({'error': f'Unknown memory type: {memory_type}'}), 400
        
        return jsonify({
            'status': 'success',
            'memory_type': memory_type,
            'stored_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in memory storage endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/memory/retrieve', methods=['GET'])
def retrieve_memory():
    """Endpoint for retrieving agent memory"""
    try:
        initialize_system()
        
        memory_type = request.args.get('memory_type', 'short_term')
        
        if memory_type == 'short_term':
            conversation_id = request.args.get('conversation_id', '')
            if not conversation_id:
                return jsonify({'error': 'conversation_id required for short-term memory'}), 400
            
            memory = memory_system.retrieve_short_term(conversation_id)
            return jsonify({
                'status': 'success',
                'memory': memory,
                'memory_type': memory_type
            })
            
        elif memory_type == 'episodic':
            scenario = request.args.get('scenario', '')
            top_k = int(request.args.get('top_k', 5))
            
            episodes = memory_system.retrieve_similar_episodes(scenario, top_k)
            return jsonify({
                'status': 'success',
                'episodes': episodes,
                'count': len(episodes)
            })
            
        elif memory_type == 'semantic':
            subject = request.args.get('subject')
            predicate = request.args.get('predicate')
            object_val = request.args.get('object')
            
            knowledge = memory_system.query_semantic_knowledge(subject, predicate, object_val)
            return jsonify({
                'status': 'success',
                'knowledge': knowledge,
                'count': len(knowledge)
            })
            
        else:
            return jsonify({'error': f'Unknown memory type: {memory_type}'}), 400
        
    except Exception as e:
        logger.error(f"Error in memory retrieval endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/analytics/performance', methods=['GET'])
def get_performance_analytics():
    """Endpoint for retrieving agent performance analytics"""
    try:
        initialize_system()
        
        # Get performance metrics from agents
        performance_data = {}
        
        for agent_name, agent in agents.items():
            performance_data[agent_name] = {
                'agent_id': agent.agent_id,
                'agent_type': agent.agent_type.value,
                'active_conversations': len(agent.active_conversations),
                'performance_metrics': agent.performance_metrics
            }
        
        # Get MCP server stats
        mcp_stats = mcp_server.get_connection_stats()
        
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'agent_performance': performance_data,
            'mcp_server_stats': mcp_stats,
            'memory_stats': {
                'short_term_memories': len(memory_system.short_term_memory),
                'long_term_memories': len(memory_system.long_term_memory),
                'episodes': len(memory_system.episodic_memory),
                'semantic_triples': len(memory_system.semantic_knowledge)
            }
        })
        
    except Exception as e:
        logger.error(f"Error in performance analytics endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/data/process', methods=['POST'])
def process_data():
    """Endpoint for triggering data processing pipeline"""
    try:
        initialize_system()
        
        # Load and process data
        raw_data = data_processor.load_data()
        clean_data = data_processor.clean_data(raw_data)
        feature_data = data_processor.engineer_features(clean_data)
        
        # Prepare training data
        X, y = ml_pipeline.prepare_training_data(feature_data)
        
        # Train models
        trained_models = ml_pipeline.train_ensemble_models(X, y)
        
        return jsonify({
            'status': 'success',
            'data_files_processed': len(clean_data),
            'features_engineered': X.shape[1],
            'training_samples': X.shape[0],
            'models_trained': len(trained_models),
            'processed_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in data processing endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/predict/lead_score', methods=['POST'])
def predict_lead_score():
    """Endpoint for predicting lead scores"""
    try:
        initialize_system()
        
        # Get request data
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({'error': 'No request data provided'}), 400
        
        lead_data = request_data.get('lead_data', {})
        
        # Simple lead scoring logic (would use trained ML models in production)
        score = 0.0
        
        # Company size scoring
        company_size_weights = {
            '5000+': 30, '1001-5000': 25, '201-1000': 20,
            '51-200': 15, '11-50': 10, '1-10': 5
        }
        score += company_size_weights.get(lead_data.get('company_size', ''), 5)
        
        # Industry scoring
        high_value_industries = ['SaaS', 'FinTech', 'HealthTech']
        if lead_data.get('industry', '') in high_value_industries:
            score += 25
        
        # Persona scoring
        decision_makers = ['Founder', 'CMO', 'CTO']
        if lead_data.get('persona', '') in decision_makers:
            score += 20
        
        # Source scoring
        high_intent_sources = ['Website', 'Referral']
        if lead_data.get('source', '') in high_intent_sources:
            score += 15
        
        # Region scoring
        priority_regions = ['US', 'EU']
        if lead_data.get('region', '') in priority_regions:
            score += 10
        
        # Cap at 100
        score = min(score, 100.0)
        
        return jsonify({
            'status': 'success',
            'lead_score': score,
            'lead_id': lead_data.get('lead_id', ''),
            'predicted_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in lead scoring endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/system/status', methods=['GET'])
def system_status():
    """Endpoint for getting overall system status"""
    try:
        initialize_system()
        
        return jsonify({
            'status': 'operational',
            'timestamp': datetime.now().isoformat(),
            'components': {
                'orchestrator': 'active' if orchestrator else 'inactive',
                'agents': {
                    'triage': 'active' if agents and 'triage' in agents else 'inactive',
                    'engagement': 'active' if agents and 'engagement' in agents else 'inactive',
                    'optimization': 'active' if agents and 'optimization' in agents else 'inactive'
                },
                'mcp_server': 'active' if mcp_server else 'inactive',
                'data_processor': 'active' if data_processor else 'inactive',
                'ml_pipeline': 'active' if ml_pipeline else 'inactive',
                'memory_system': 'active' if memory_system else 'inactive'
            },
            'version': '1.0.0',
            'environment': 'development'
        })
        
    except Exception as e:
        logger.error(f"Error in system status endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

