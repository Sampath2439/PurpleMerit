"""
Multi-Agent Marketing System - Comprehensive Test Suite
Production-ready test suite covering all system components with edge cases
"""

import unittest
import asyncio
import json
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np

# Import system components
from src.agents import (
    LeadTriageAgent, EngagementAgent, CampaignOptimizationAgent,
    AgentOrchestrator, create_agent_system, AgentType, ActionType,
    EscalationReason, HandoffContext
)
from src.mcp_server import MCPServer, ResourceManager, MCPRequest, MCPResponse
from src.data_processor import DataProcessor, MLPipeline, AgentMemorySystem

class TestLeadTriageAgent(unittest.TestCase):
    """Test cases for Lead Triage Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = LeadTriageAgent("LT-TEST-001")
        
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertEqual(self.agent.agent_id, "LT-TEST-001")
        self.assertEqual(self.agent.agent_type, AgentType.LEAD_TRIAGE)
        self.assertIsNotNone(self.agent.triage_rules)
        
    def test_classify_lead_campaign_qualified(self):
        """Test lead classification for campaign qualified leads"""
        lead_data = {
            'source': 'Google Ads',
            'persona': 'Founder',
            'company_size': '5000+',
            'industry': 'SaaS'
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.agent._classify_lead(lead_data))
        loop.close()
        
        self.assertEqual(result, 'Campaign Qualified')
        
    def test_classify_lead_cold_lead(self):
        """Test lead classification for cold leads"""
        lead_data = {
            'source': 'Cold Email',
            'persona': 'Employee',
            'company_size': '1-10',
            'industry': 'Other'
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.agent._classify_lead(lead_data))
        loop.close()
        
        self.assertEqual(result, 'Cold Lead')
        
    def test_calculate_lead_score_high_value(self):
        """Test lead scoring for high-value leads"""
        lead_data = {
            'company_size': '5000+',
            'industry': 'SaaS',
            'persona': 'Founder',
            'region': 'US',
            'source': 'Website'
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        score = loop.run_until_complete(self.agent._calculate_lead_score(lead_data))
        loop.close()
        
        self.assertGreaterEqual(score, 80.0)
        
    def test_calculate_lead_score_low_value(self):
        """Test lead scoring for low-value leads"""
        lead_data = {
            'company_size': '1-10',
            'industry': 'Other',
            'persona': 'Employee',
            'region': 'Other',
            'source': 'Cold Email'
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        score = loop.run_until_complete(self.agent._calculate_lead_score(lead_data))
        loop.close()
        
        self.assertLessEqual(score, 30.0)
        
    def test_process_request_success(self):
        """Test successful request processing"""
        request = {
            'lead_data': {
                'lead_id': 'L0000001',
                'source': 'Website',
                'persona': 'Founder',
                'company_size': '1001-5000',
                'industry': 'SaaS'
            },
            'conversation_id': 'C0000001'
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.agent.process_request(request))
        loop.close()
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('triage_category', result)
        self.assertIn('lead_score', result)
        self.assertIn('routing_decision', result)
        
    def test_process_request_empty_data(self):
        """Test request processing with empty data"""
        request = {}
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.agent.process_request(request))
        loop.close()
        
        self.assertEqual(result['status'], 'success')  # Should handle gracefully
        
    def test_handle_handoff(self):
        """Test handoff handling"""
        context = HandoffContext(
            summary="Test handoff",
            confidence=0.8,
            lead_id="L0000001",
            conversation_id="C0000001",
            previous_actions=[],
            metadata={'source': 'Website', 'persona': 'Founder'},
            timestamp=datetime.now()
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.agent.handle_handoff(context))
        loop.close()
        
        self.assertEqual(result['status'], 'success')

class TestEngagementAgent(unittest.TestCase):
    """Test cases for Engagement Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = EngagementAgent("EN-TEST-001")
        
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertEqual(self.agent.agent_id, "EN-TEST-001")
        self.assertEqual(self.agent.agent_type, AgentType.ENGAGEMENT)
        self.assertIsNotNone(self.agent.communication_templates)
        
    def test_determine_optimal_channel(self):
        """Test optimal channel determination"""
        lead_data = {
            'preferred_channel': 'Email',
            'persona': 'Founder',
            'region': 'US'
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        channel = loop.run_until_complete(self.agent._determine_optimal_channel(lead_data))
        loop.close()
        
        self.assertEqual(channel, 'Email')
        
    def test_generate_personalized_content(self):
        """Test personalized content generation"""
        lead_data = {
            'company_size': '5000+',
            'industry': 'SaaS',
            'persona': 'Founder'
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        content = loop.run_until_complete(
            self.agent._generate_personalized_content(lead_data, 'welcome', 'email')
        )
        loop.close()
        
        self.assertIsInstance(content, str)
        self.assertGreater(len(content), 0)
        
    def test_process_request_success(self):
        """Test successful engagement request processing"""
        request = {
            'lead_data': {
                'lead_id': 'L0000001',
                'preferred_channel': 'Email',
                'persona': 'Founder',
                'industry': 'SaaS'
            },
            'engagement_type': 'welcome',
            'conversation_id': 'C0000001'
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.agent.process_request(request))
        loop.close()
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('channel', result)
        self.assertIn('content', result)
        self.assertIn('engagement_result', result)

class TestCampaignOptimizationAgent(unittest.TestCase):
    """Test cases for Campaign Optimization Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = CampaignOptimizationAgent("OP-TEST-001")
        
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertEqual(self.agent.agent_id, "OP-TEST-001")
        self.assertEqual(self.agent.agent_type, AgentType.CAMPAIGN_OPTIMIZER)
        self.assertIsNotNone(self.agent.optimization_rules)
        
    def test_calculate_performance_score(self):
        """Test performance score calculation"""
        campaign_data = {
            'ctr': 0.03,
            'roas': 2.5,
            'conversions': 15
        }
        
        score = self.agent._calculate_performance_score(campaign_data)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)
        
    def test_analyze_campaign_performance_good(self):
        """Test campaign performance analysis for good performance"""
        campaign_data = {
            'campaign_id': 'CMP0001',
            'ctr': 0.03,
            'cpl_usd': 30.0,
            'roas': 2.5,
            'conversions': 10,
            'cost_usd': 300.0,
            'daily_budget_usd': 100.0
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            self.agent._analyze_campaign_performance(campaign_data)
        )
        loop.close()
        
        self.assertIn('campaign_id', result)
        self.assertIn('performance_score', result)
        self.assertIn('recommendations', result)
        self.assertIn('metrics_analysis', result)
        
    def test_analyze_campaign_performance_poor(self):
        """Test campaign performance analysis for poor performance"""
        campaign_data = {
            'campaign_id': 'CMP0002',
            'ctr': 0.01,
            'cpl_usd': 80.0,
            'roas': 0.3,
            'conversions': 0,
            'cost_usd': 100.0,
            'daily_budget_usd': 50.0
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            self.agent._analyze_campaign_performance(campaign_data)
        )
        loop.close()
        
        self.assertGreater(len(result['recommendations']), 0)
        # Should have recommendations for poor performance
        
    def test_process_request_performance_check(self):
        """Test performance check request processing"""
        request = {
            'campaign_data': {
                'campaign_id': 'CMP0001',
                'ctr': 0.025,
                'roas': 1.8,
                'conversions': 5
            },
            'optimization_type': 'performance_check',
            'conversation_id': 'C0000001'
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.agent.process_request(request))
        loop.close()
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('optimization_result', result)

class TestAgentOrchestrator(unittest.TestCase):
    """Test cases for Agent Orchestrator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.orchestrator = AgentOrchestrator()
        self.triage_agent = LeadTriageAgent("LT-TEST-001")
        self.engagement_agent = EngagementAgent("EN-TEST-001")
        self.optimization_agent = CampaignOptimizationAgent("OP-TEST-001")
        
        self.orchestrator.register_agent(self.triage_agent)
        self.orchestrator.register_agent(self.engagement_agent)
        self.orchestrator.register_agent(self.optimization_agent)
        
    def test_register_agent(self):
        """Test agent registration"""
        test_agent = LeadTriageAgent("LT-TEST-002")
        self.orchestrator.register_agent(test_agent)
        
        self.assertIn("LT-TEST-002", self.orchestrator.agents)
        
    def test_route_request_triage(self):
        """Test routing triage requests"""
        request = {
            'type': 'lead_triage',
            'lead_data': {'lead_id': 'L0000001'}
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.orchestrator.route_request(request))
        loop.close()
        
        self.assertEqual(result['status'], 'success')
        
    def test_route_request_engagement(self):
        """Test routing engagement requests"""
        request = {
            'type': 'engagement',
            'lead_data': {'lead_id': 'L0000001'}
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.orchestrator.route_request(request))
        loop.close()
        
        self.assertEqual(result['status'], 'success')
        
    def test_route_request_unknown_type(self):
        """Test routing unknown request types"""
        request = {
            'type': 'unknown_type',
            'data': {}
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.orchestrator.route_request(request))
        loop.close()
        
        self.assertEqual(result['status'], 'error')
        
    def test_execute_handoff(self):
        """Test handoff execution"""
        context = HandoffContext(
            summary="Test handoff",
            confidence=0.8,
            lead_id="L0000001",
            conversation_id="C0000001",
            previous_actions=[],
            metadata={'test': 'data'},
            timestamp=datetime.now()
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            self.orchestrator.execute_handoff(
                "LT-TEST-001", AgentType.ENGAGEMENT, context
            )
        )
        loop.close()
        
        self.assertEqual(result['status'], 'success')

class TestMCPServer(unittest.TestCase):
    """Test cases for MCP Server"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.server = MCPServer()
        
    def test_server_initialization(self):
        """Test MCP server initialization"""
        self.assertEqual(self.server.host, "0.0.0.0")
        self.assertEqual(self.server.port, 8765)
        self.assertIsNotNone(self.server.resource_manager)
        
    def test_process_mcp_request_get_lead_data(self):
        """Test MCP request processing for lead data"""
        request = MCPRequest(
            jsonrpc="2.0",
            method="getLeadData",
            params={'lead_id': 'L0000001', 'actor': 'Agent-Client'},
            id="test-001"
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(self.server._process_mcp_request(request))
        loop.close()
        
        self.assertEqual(response.jsonrpc, "2.0")
        self.assertEqual(response.id, "test-001")
        self.assertIsNotNone(response.result)
        
    def test_process_mcp_request_unknown_method(self):
        """Test MCP request processing for unknown method"""
        request = MCPRequest(
            jsonrpc="2.0",
            method="unknownMethod",
            params={},
            id="test-002"
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(self.server._process_mcp_request(request))
        loop.close()
        
        self.assertIsNotNone(response.error)
        
    def test_get_connection_stats(self):
        """Test connection statistics retrieval"""
        stats = self.server.get_connection_stats()
        
        self.assertIn('active_connections', stats)
        self.assertIn('total_requests', stats)
        self.assertIn('websocket_sessions', stats)

class TestResourceManager(unittest.TestCase):
    """Test cases for Resource Manager"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory with test data
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test CSV files
        test_leads = pd.DataFrame({
            'lead_id': ['L0000001', 'L0000002'],
            'source': ['Website', 'Google Ads'],
            'persona': ['Founder', 'CMO']
        })
        test_leads.to_csv(os.path.join(self.temp_dir, 'leads.csv'), index=False)
        
        test_campaigns = pd.DataFrame({
            'campaign_id': ['CMP0001', 'CMP0002'],
            'name': ['Test Campaign 1', 'Test Campaign 2'],
            'objective': ['Lead Gen', 'Awareness']
        })
        test_campaigns.to_csv(os.path.join(self.temp_dir, 'campaigns.csv'), index=False)
        
        self.resource_manager = ResourceManager(data_path=self.temp_dir + "/")
        
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def test_check_permissions_allowed(self):
        """Test permission checking for allowed access"""
        result = self.resource_manager._check_permissions(
            'db://leads', None, 'MCP-Server'
        )
        self.assertTrue(result)
        
    def test_check_permissions_denied(self):
        """Test permission checking for denied access"""
        result = self.resource_manager._check_permissions(
            'db://campaigns', None, 'Unknown-Actor'
        )
        self.assertFalse(result)
        
    def test_access_database_leads(self):
        """Test database access for leads"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            self.resource_manager._access_database('db://leads', 'SELECT')
        )
        loop.close()
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('data', result)
        self.assertGreater(result['count'], 0)
        
    def test_access_resource_with_logging(self):
        """Test resource access with proper logging"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            self.resource_manager.access_resource(
                'db://leads', None, 'SELECT', 'MCP-Server'
            )
        )
        loop.close()
        
        self.assertEqual(result['status'], 'success')
        self.assertGreater(len(self.resource_manager.access_log), 0)

class TestDataProcessor(unittest.TestCase):
    """Test cases for Data Processor"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory with test data
        self.temp_dir = tempfile.mkdtemp()
        
        # Create minimal test data
        test_leads = pd.DataFrame({
            'lead_id': ['L0000001', 'L0000002', 'L0000003'],
            'created_at': ['2025-01-01T10:00:00', '2025-01-02T11:00:00', '2025-01-03T12:00:00'],
            'lead_status': ['Qualified', 'Open', 'Converted'],
            'lead_score': [75, 45, 90],
            'company_size': ['1001-5000', '51-200', '5000+'],
            'industry': ['SaaS', 'HealthTech', 'FinTech'],
            'persona': ['Founder', 'CMO', 'CTO'],
            'region': ['US', 'EU', 'APAC']
        })
        test_leads.to_csv(os.path.join(self.temp_dir, 'leads.csv'), index=False)
        
        # Create other required files
        for filename in ['campaigns.csv', 'interactions.csv', 'conversions.csv']:
            pd.DataFrame().to_csv(os.path.join(self.temp_dir, filename), index=False)
        
        self.processor = DataProcessor(data_path=self.temp_dir + "/")
        
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def test_load_data(self):
        """Test data loading"""
        data = self.processor.load_data()
        
        self.assertIn('leads', data)
        self.assertGreater(len(data['leads']), 0)
        
    def test_clean_data(self):
        """Test data cleaning"""
        raw_data = self.processor.load_data()
        clean_data = self.processor.clean_data(raw_data)
        
        self.assertIn('leads', clean_data)
        self.assertIsInstance(clean_data['leads'], pd.DataFrame)
        
    def test_engineer_features(self):
        """Test feature engineering"""
        raw_data = self.processor.load_data()
        clean_data = self.processor.clean_data(raw_data)
        feature_data = self.processor.engineer_features(clean_data)
        
        self.assertIsInstance(feature_data, pd.DataFrame)
        self.assertGreater(feature_data.shape[1], 0)

class TestMLPipeline(unittest.TestCase):
    """Test cases for ML Pipeline"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.pipeline = MLPipeline()
        
        # Create test data
        self.test_data = pd.DataFrame({
            'lead_id': ['L0000001', 'L0000002', 'L0000003', 'L0000004', 'L0000005'],
            'lead_status': ['Qualified', 'Open', 'Converted', 'Qualified', 'Open'],
            'lead_score': [75, 45, 90, 80, 50],
            'company_size': ['1001-5000', '51-200', '5000+', '1001-5000', '51-200'],
            'industry': ['SaaS', 'HealthTech', 'FinTech', 'SaaS', 'HealthTech'],
            'persona': ['Founder', 'CMO', 'CTO', 'Founder', 'CMO'],
            'region': ['US', 'EU', 'APAC', 'US', 'EU']
        })
        
    def test_prepare_training_data(self):
        """Test training data preparation"""
        X, y = self.pipeline.prepare_training_data(self.test_data)
        
        self.assertEqual(len(X), len(y))
        self.assertGreater(X.shape[1], 0)
        
    def test_create_preprocessing_pipeline(self):
        """Test preprocessing pipeline creation"""
        X, y = self.pipeline.prepare_training_data(self.test_data)
        preprocessor = self.pipeline.create_preprocessing_pipeline(X)
        
        self.assertIsNotNone(preprocessor)

class TestAgentMemorySystem(unittest.TestCase):
    """Test cases for Agent Memory System"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.memory_system = AgentMemorySystem()
        
    def test_store_short_term_memory(self):
        """Test short-term memory storage"""
        context = {'intent': 'product_inquiry', 'sentiment': 'positive'}
        self.memory_system.store_short_term('C0000001', context)
        
        self.assertIn('C0000001', self.memory_system.short_term_memory)
        
    def test_retrieve_short_term_memory(self):
        """Test short-term memory retrieval"""
        context = {'intent': 'product_inquiry', 'sentiment': 'positive'}
        self.memory_system.store_short_term('C0000001', context)
        
        retrieved = self.memory_system.retrieve_short_term('C0000001')
        self.assertEqual(retrieved, context)
        
    def test_retrieve_expired_short_term_memory(self):
        """Test retrieval of expired short-term memory"""
        context = {'intent': 'product_inquiry', 'sentiment': 'positive'}
        self.memory_system.store_short_term('C0000001', context, ttl_hours=0)
        
        # Memory should be expired immediately
        retrieved = self.memory_system.retrieve_short_term('C0000001')
        self.assertIsNone(retrieved)
        
    def test_update_long_term_memory(self):
        """Test long-term memory updates"""
        preferences = {'preferred_channel': 'email', 'contact_time': 'morning'}
        self.memory_system.update_long_term('L0000001', preferences, 0.75)
        
        self.assertIn('L0000001', self.memory_system.long_term_memory)
        
    def test_store_episode(self):
        """Test episodic memory storage"""
        actions = [{'action': 'send_email', 'result': 'opened'}]
        self.memory_system.store_episode('product_inquiry', actions, 0.85)
        
        self.assertGreater(len(self.memory_system.episodic_memory), 0)
        
    def test_retrieve_similar_episodes(self):
        """Test similar episode retrieval"""
        actions = [{'action': 'send_email', 'result': 'opened'}]
        self.memory_system.store_episode('product_inquiry', actions, 0.85)
        
        similar = self.memory_system.retrieve_similar_episodes('product')
        self.assertGreater(len(similar), 0)
        
    def test_update_semantic_knowledge(self):
        """Test semantic knowledge updates"""
        self.memory_system.update_semantic_knowledge(
            'lead_L0000001', 'prefers', 'email_communication', 0.9
        )
        
        self.assertGreater(len(self.memory_system.semantic_knowledge), 0)
        
    def test_query_semantic_knowledge(self):
        """Test semantic knowledge queries"""
        self.memory_system.update_semantic_knowledge(
            'lead_L0000001', 'prefers', 'email_communication', 0.9
        )
        
        results = self.memory_system.query_semantic_knowledge(subject='lead_L0000001')
        self.assertGreater(len(results), 0)

class TestEdgeCases(unittest.TestCase):
    """Test cases for edge cases and error conditions"""
    
    def test_empty_lead_data_triage(self):
        """Test triage agent with empty lead data"""
        agent = LeadTriageAgent("LT-TEST-001")
        request = {'lead_data': {}}
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(agent.process_request(request))
        loop.close()
        
        self.assertEqual(result['status'], 'success')  # Should handle gracefully
        
    def test_malformed_json_mcp_request(self):
        """Test MCP server with malformed JSON"""
        server = MCPServer()
        
        # This would normally be tested with actual WebSocket connection
        # For now, test the request processing directly
        request = MCPRequest(
            jsonrpc="2.0",
            method="invalidMethod",
            params=None,
            id="test"
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(server._process_mcp_request(request))
        loop.close()
        
        self.assertIsNotNone(response.error)
        
    def test_memory_system_with_invalid_data(self):
        """Test memory system with invalid data"""
        memory_system = AgentMemorySystem()
        
        # Test with None values
        memory_system.store_short_term(None, None)
        memory_system.update_long_term(None, None, None)
        
        # Should not crash
        self.assertTrue(True)
        
    def test_data_processor_with_missing_files(self):
        """Test data processor with missing files"""
        processor = DataProcessor(data_path="/nonexistent/path/")
        data = processor.load_data()
        
        # Should return empty dict or handle gracefully
        self.assertIsInstance(data, dict)
        
    def test_agent_orchestrator_no_agents(self):
        """Test orchestrator with no registered agents"""
        orchestrator = AgentOrchestrator()
        request = {'type': 'lead_triage', 'lead_data': {}}
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(orchestrator.route_request(request))
        loop.close()
        
        self.assertEqual(result['status'], 'error')
        
    def test_concurrent_agent_requests(self):
        """Test concurrent agent requests"""
        agent = LeadTriageAgent("LT-TEST-001")
        
        async def make_request():
            return await agent.process_request({
                'lead_data': {'lead_id': f'L{np.random.randint(1000, 9999)}'}
            })
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Make multiple concurrent requests
        tasks = [make_request() for _ in range(5)]
        results = loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()
        
        # All should succeed
        for result in results:
            self.assertEqual(result['status'], 'success')
            
    def test_memory_system_capacity_limits(self):
        """Test memory system with capacity limits"""
        memory_system = AgentMemorySystem()
        
        # Store many episodes to test capacity limits
        for i in range(1500):  # More than the 1000 limit
            memory_system.store_episode(
                f'scenario_{i}',
                [{'action': f'action_{i}'}],
                np.random.random(),
                f'notes_{i}'
            )
        
        # Should be limited to 1000
        self.assertLessEqual(len(memory_system.episodic_memory), 1000)
        
    def test_performance_under_load(self):
        """Test system performance under load"""
        orchestrator, agents = create_agent_system()
        
        async def process_many_requests():
            tasks = []
            for i in range(100):
                request = {
                    'type': 'lead_triage',
                    'lead_data': {
                        'lead_id': f'L{i:06d}',
                        'source': 'Website',
                        'persona': 'Founder'
                    }
                }
                tasks.append(orchestrator.route_request(request))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_time = datetime.now()
        results = loop.run_until_complete(process_many_requests())
        end_time = datetime.now()
        loop.close()
        
        # Check that most requests succeeded
        successful_results = [r for r in results if isinstance(r, dict) and r.get('status') == 'success']
        self.assertGreater(len(successful_results), 80)  # At least 80% success rate
        
        # Check performance (should complete within reasonable time)
        duration = (end_time - start_time).total_seconds()
        self.assertLess(duration, 30)  # Should complete within 30 seconds

def run_all_tests():
    """Run all test suites"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestLeadTriageAgent,
        TestEngagementAgent,
        TestCampaignOptimizationAgent,
        TestAgentOrchestrator,
        TestMCPServer,
        TestResourceManager,
        TestDataProcessor,
        TestMLPipeline,
        TestAgentMemorySystem,
        TestEdgeCases
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result

if __name__ == '__main__':
    # Run all tests
    print("Running Multi-Agent Marketing System Test Suite...")
    print("=" * 60)
    
    result = run_all_tests()
    
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    print("\nTest suite completed.")

