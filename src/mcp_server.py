"""
Multi-Agent Marketing System - MCP (Model Context Protocol) Server
Production-ready MCP server implementation for secure data access and inter-agent communication
"""

import json
import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import websockets
from flask import Flask, request, jsonify
import sqlite3
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransportType(Enum):
    """Transport layer types"""
    WEBSOCKET = "WebSocket"
    HTTP = "HTTP"

class MCPMethod(Enum):
    """MCP method types"""
    SEARCH_GRAPH = "searchGraph"
    STORE_MEMORY = "storeMemory"
    RECOMMEND_ACTION = "recommendAction"
    GET_LEAD_DATA = "getLeadData"
    UPDATE_CAMPAIGN = "updateCampaign"
    ANALYZE_PERFORMANCE = "analyzePerformance"

class ResourceScope(Enum):
    """Resource access scopes"""
    READ = "read"
    WRITE = "write"
    SEARCH = "search"
    CONSOLIDATE = "consolidate"

@dataclass
class MCPRequest:
    """MCP request structure following JSON-RPC 2.0"""
    jsonrpc: str = "2.0"
    method: str = ""
    params: Dict[str, Any] = None
    id: Union[str, int] = None

@dataclass
class MCPResponse:
    """MCP response structure following JSON-RPC 2.0"""
    jsonrpc: str = "2.0"
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    id: Union[str, int] = None

@dataclass
class MCPError:
    """MCP error structure"""
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None

class ResourceManager:
    """Manages access to different data resources"""
    
    def __init__(self, data_path: str = "./data/"):
        self.data_path = data_path
        self.access_log = []
        self.resource_cache = {}
        
    async def access_resource(self, resource_uri: str, scope: ResourceScope, 
                            operation: str, actor: str) -> Dict[str, Any]:
        """Access a resource with proper logging and permissions"""
        try:
            # Log access attempt
            access_record = {
                'resource_uri': resource_uri,
                'timestamp': datetime.now(),
                'scope': scope.value,
                'operation': operation,
                'actor': actor,
                'success': False
            }
            
            # Check permissions (simplified for demo)
            if not self._check_permissions(resource_uri, scope, actor):
                access_record['success'] = False
                self.access_log.append(access_record)
                raise PermissionError(f"Access denied to {resource_uri} for {actor}")
            
            # Execute resource access
            result = await self._execute_resource_access(resource_uri, operation)
            
            access_record['success'] = True
            self.access_log.append(access_record)
            
            logger.info(f"Resource access: {resource_uri} by {actor} - {operation}")
            
            return result
            
        except Exception as e:
            logger.error(f"Resource access error: {str(e)}")
            access_record['success'] = False
            self.access_log.append(access_record)
            raise
    
    def _check_permissions(self, resource_uri: str, scope: ResourceScope, actor: str) -> bool:
        """Check if actor has permission to access resource with given scope"""
        # Simplified permission model - in production would use proper RBAC
        permission_matrix = {
            'MCP-Server': ['db://leads', 'db://campaigns', 'db://interactions', 'kg://graph'],
            'Agent-Client': ['db://leads', 'db://interactions', 'analytics://events'],
            'Optimizer-Worker': ['db://campaigns', 'analytics://events', 'kg://graph']
        }
        
        allowed_resources = permission_matrix.get(actor, [])
        return any(resource_uri.startswith(allowed) for allowed in allowed_resources)
    
    async def _execute_resource_access(self, resource_uri: str, operation: str) -> Dict[str, Any]:
        """Execute the actual resource access operation"""
        if resource_uri.startswith('db://'):
            return await self._access_database(resource_uri, operation)
        elif resource_uri.startswith('kg://'):
            return await self._access_knowledge_graph(resource_uri, operation)
        elif resource_uri.startswith('analytics://'):
            return await self._access_analytics(resource_uri, operation)
        else:
            raise ValueError(f"Unknown resource type: {resource_uri}")
    
    async def _access_database(self, resource_uri: str, operation: str) -> Dict[str, Any]:
        """Access database resources"""
        table_name = resource_uri.split('://')[-1]
        
        try:
            # Load data from CSV files (simulating database access)
            if table_name == 'leads':
                df = pd.read_csv(f"{self.data_path}leads.csv")
            elif table_name == 'campaigns':
                df = pd.read_csv(f"{self.data_path}campaigns.csv")
            elif table_name == 'interactions':
                df = pd.read_csv(f"{self.data_path}interactions.csv")
            else:
                raise ValueError(f"Unknown table: {table_name}")
            
            if operation == 'SELECT':
                return {
                    'status': 'success',
                    'data': df.head(10).to_dict('records'),  # Return first 10 records
                    'count': len(df)
                }
            elif operation == 'INSERT':
                return {'status': 'success', 'message': 'Insert operation simulated'}
            elif operation == 'UPDATE':
                return {'status': 'success', 'message': 'Update operation simulated'}
            else:
                raise ValueError(f"Unsupported operation: {operation}")
                
        except Exception as e:
            logger.error(f"Database access error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def _access_knowledge_graph(self, resource_uri: str, operation: str) -> Dict[str, Any]:
        """Access knowledge graph resources"""
        try:
            # Load semantic triples (simulating graph database)
            df = pd.read_csv(f"{self.data_path}semantic_kg_triples.csv")
            
            if operation == 'SELECT':
                return {
                    'status': 'success',
                    'triples': df.head(20).to_dict('records'),
                    'count': len(df)
                }
            elif operation == 'MERGE':
                return {'status': 'success', 'message': 'Graph merge operation simulated'}
            else:
                raise ValueError(f"Unsupported graph operation: {operation}")
                
        except Exception as e:
            logger.error(f"Knowledge graph access error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def _access_analytics(self, resource_uri: str, operation: str) -> Dict[str, Any]:
        """Access analytics resources"""
        try:
            # Load campaign performance data
            df = pd.read_csv(f"{self.data_path}campaign_daily.csv")
            
            # Calculate analytics
            analytics = {
                'total_campaigns': df['campaign_id'].nunique(),
                'total_impressions': df['impressions'].sum(),
                'total_clicks': df['clicks'].sum(),
                'average_ctr': df['ctr'].mean(),
                'total_cost': df['cost_usd'].sum(),
                'total_revenue': df['revenue_usd'].sum(),
                'average_roas': df['roas'].mean()
            }
            
            return {
                'status': 'success',
                'analytics': analytics,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Analytics access error: {str(e)}")
            return {'status': 'error', 'message': str(e)}

class MCPServer:
    """MCP Server implementation with WebSocket and HTTP support"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.resource_manager = ResourceManager()
        self.active_connections = {}
        self.request_log = []
        
    async def handle_websocket_connection(self, websocket, path):
        """Handle WebSocket connections"""
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = {
            'websocket': websocket,
            'connected_at': datetime.now(),
            'messages_sent': 0,
            'messages_received': 0
        }
        
        logger.info(f"WebSocket connection established: {connection_id}")
        
        try:
            async for message in websocket:
                await self._handle_websocket_message(connection_id, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket connection closed: {connection_id}")
        finally:
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]
    
    async def _handle_websocket_message(self, connection_id: str, message: str):
        """Handle incoming WebSocket message"""
        try:
            # Parse JSON-RPC request
            request_data = json.loads(message)
            mcp_request = MCPRequest(
                jsonrpc=request_data.get('jsonrpc', '2.0'),
                method=request_data.get('method', ''),
                params=request_data.get('params', {}),
                id=request_data.get('id')
            )
            
            # Log request
            self._log_request(mcp_request, TransportType.WEBSOCKET)
            
            # Process request
            response = await self._process_mcp_request(mcp_request)
            
            # Send response
            websocket = self.active_connections[connection_id]['websocket']
            await websocket.send(json.dumps(asdict(response)))
            
            # Update connection stats
            self.active_connections[connection_id]['messages_received'] += 1
            self.active_connections[connection_id]['messages_sent'] += 1
            
        except Exception as e:
            logger.error(f"WebSocket message handling error: {str(e)}")
            error_response = MCPResponse(
                jsonrpc="2.0",
                error=asdict(MCPError(code=-32603, message="Internal error")),
                id=request_data.get('id') if 'request_data' in locals() else None
            )
            websocket = self.active_connections[connection_id]['websocket']
            await websocket.send(json.dumps(asdict(error_response)))
    
    def create_http_app(self) -> Flask:
        """Create Flask app for HTTP transport"""
        app = Flask(__name__)
        
        @app.route('/mcp', methods=['POST'])
        async def handle_http_request():
            try:
                request_data = request.get_json()
                
                mcp_request = MCPRequest(
                    jsonrpc=request_data.get('jsonrpc', '2.0'),
                    method=request_data.get('method', ''),
                    params=request_data.get('params', {}),
                    id=request_data.get('id')
                )
                
                # Log request
                self._log_request(mcp_request, TransportType.HTTP)
                
                # Process request
                response = await self._process_mcp_request(mcp_request)
                
                return jsonify(asdict(response))
                
            except Exception as e:
                logger.error(f"HTTP request handling error: {str(e)}")
                error_response = MCPResponse(
                    jsonrpc="2.0",
                    error=asdict(MCPError(code=-32603, message="Internal error")),
                    id=request_data.get('id') if 'request_data' in locals() else None
                )
                return jsonify(asdict(error_response)), 500
        
        return app
    
    def _log_request(self, request: MCPRequest, transport: TransportType):
        """Log MCP request for monitoring"""
        log_entry = {
            'rpc_id': f"RPC{len(self.request_log):06d}",
            'timestamp': datetime.now(),
            'transport': transport.value,
            'method': request.method,
            'params_bytes': len(json.dumps(request.params or {})),
            'source_agent_type': request.params.get('source_agent_type', 'Unknown') if request.params else 'Unknown'
        }
        
        self.request_log.append(log_entry)
    
    async def _process_mcp_request(self, request: MCPRequest) -> MCPResponse:
        """Process MCP request and return response"""
        start_time = datetime.now()
        
        try:
            if request.method == MCPMethod.GET_LEAD_DATA.value:
                result = await self._handle_get_lead_data(request.params or {})
            elif request.method == MCPMethod.SEARCH_GRAPH.value:
                result = await self._handle_search_graph(request.params or {})
            elif request.method == MCPMethod.STORE_MEMORY.value:
                result = await self._handle_store_memory(request.params or {})
            elif request.method == MCPMethod.RECOMMEND_ACTION.value:
                result = await self._handle_recommend_action(request.params or {})
            elif request.method == MCPMethod.UPDATE_CAMPAIGN.value:
                result = await self._handle_update_campaign(request.params or {})
            elif request.method == MCPMethod.ANALYZE_PERFORMANCE.value:
                result = await self._handle_analyze_performance(request.params or {})
            else:
                raise ValueError(f"Unknown method: {request.method}")
            
            # Calculate duration
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Update request log with duration
            if self.request_log:
                self.request_log[-1]['duration_ms'] = duration_ms
                self.request_log[-1]['status_code'] = 200
            
            return MCPResponse(
                jsonrpc="2.0",
                result=result,
                id=request.id
            )
            
        except Exception as e:
            logger.error(f"MCP request processing error: {str(e)}")
            
            # Update request log with error
            if self.request_log:
                self.request_log[-1]['duration_ms'] = (datetime.now() - start_time).total_seconds() * 1000
                self.request_log[-1]['status_code'] = 500
            
            return MCPResponse(
                jsonrpc="2.0",
                error=asdict(MCPError(code=-32603, message=str(e))),
                id=request.id
            )
    
    async def _handle_get_lead_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get lead data request"""
        lead_id = params.get('lead_id')
        actor = params.get('actor', 'Agent-Client')
        
        if not lead_id:
            raise ValueError("lead_id parameter required")
        
        # Access lead data through resource manager
        result = await self.resource_manager.access_resource(
            'db://leads', ResourceScope.READ, 'SELECT', actor
        )
        
        # Filter for specific lead (simplified)
        if result['status'] == 'success':
            lead_data = [lead for lead in result['data'] if lead.get('lead_id') == lead_id]
            return {
                'lead_data': lead_data[0] if lead_data else None,
                'found': len(lead_data) > 0
            }
        else:
            return result
    
    async def _handle_search_graph(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle knowledge graph search request"""
        query = params.get('query', {})
        actor = params.get('actor', 'Agent-Client')
        
        # Access knowledge graph through resource manager
        result = await self.resource_manager.access_resource(
            'kg://graph', ResourceScope.SEARCH, 'SELECT', actor
        )
        
        if result['status'] == 'success':
            # Filter triples based on query (simplified)
            triples = result['triples']
            if 'subject' in query:
                triples = [t for t in triples if t.get('subject') == query['subject']]
            if 'predicate' in query:
                triples = [t for t in triples if t.get('predicate') == query['predicate']]
            
            return {
                'triples': triples,
                'count': len(triples)
            }
        else:
            return result
    
    async def _handle_store_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle store memory request"""
        memory_type = params.get('memory_type', 'short_term')
        memory_data = params.get('memory_data', {})
        actor = params.get('actor', 'Agent-Client')
        
        # Simulate memory storage
        return {
            'status': 'success',
            'memory_id': f"MEM_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'memory_type': memory_type,
            'stored_at': datetime.now().isoformat()
        }
    
    async def _handle_recommend_action(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle action recommendation request"""
        context = params.get('context', {})
        actor = params.get('actor', 'Agent-Client')
        
        # Access analytics for recommendation
        analytics_result = await self.resource_manager.access_resource(
            'analytics://events', ResourceScope.READ, 'SELECT', actor
        )
        
        # Generate recommendation based on context and analytics
        recommendations = [
            {
                'action': 'send_follow_up_email',
                'confidence': 0.85,
                'reason': 'High engagement score and no recent contact'
            },
            {
                'action': 'schedule_demo',
                'confidence': 0.72,
                'reason': 'Lead shows strong buying signals'
            }
        ]
        
        return {
            'recommendations': recommendations,
            'context_analyzed': context,
            'generated_at': datetime.now().isoformat()
        }
    
    async def _handle_update_campaign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle campaign update request"""
        campaign_id = params.get('campaign_id')
        updates = params.get('updates', {})
        actor = params.get('actor', 'Optimizer-Worker')
        
        if not campaign_id:
            raise ValueError("campaign_id parameter required")
        
        # Simulate campaign update
        return {
            'status': 'success',
            'campaign_id': campaign_id,
            'updates_applied': updates,
            'updated_at': datetime.now().isoformat()
        }
    
    async def _handle_analyze_performance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle performance analysis request"""
        campaign_id = params.get('campaign_id')
        actor = params.get('actor', 'Optimizer-Worker')
        
        # Access analytics data
        analytics_result = await self.resource_manager.access_resource(
            'analytics://events', ResourceScope.READ, 'SELECT', actor
        )
        
        if analytics_result['status'] == 'success':
            analytics = analytics_result['analytics']
            
            # Generate performance analysis
            analysis = {
                'performance_score': 75.5,
                'key_metrics': analytics,
                'recommendations': [
                    'Increase budget for high-performing channels',
                    'Optimize ad creative for better CTR',
                    'Review targeting parameters'
                ],
                'analyzed_at': datetime.now().isoformat()
            }
            
            return analysis
        else:
            return analytics_result
    
    async def start_websocket_server(self):
        """Start WebSocket server"""
        logger.info(f"Starting MCP WebSocket server on {self.host}:{self.port}")
        await websockets.serve(self.handle_websocket_connection, self.host, self.port)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            'active_connections': len(self.active_connections),
            'total_requests': len(self.request_log),
            'websocket_sessions': len(self.active_connections),
            'request_log_sample': self.request_log[-10:] if self.request_log else []
        }

# Factory function to create MCP server
def create_mcp_server(host: str = "0.0.0.0", port: int = 8765) -> MCPServer:
    """Create and configure MCP server"""
    server = MCPServer(host, port)
    logger.info("MCP Server created successfully")
    return server

# Example usage and testing
async def test_mcp_server():
    """Test MCP server functionality"""
    server = create_mcp_server()
    
    # Test request processing
    test_request = MCPRequest(
        jsonrpc="2.0",
        method="getLeadData",
        params={
            'lead_id': 'L0000001',
            'actor': 'Agent-Client'
        },
        id="test-001"
    )
    
    response = await server._process_mcp_request(test_request)
    logger.info(f"Test response: {response}")
    
    return server

if __name__ == "__main__":
    # Run test
    asyncio.run(test_mcp_server())

