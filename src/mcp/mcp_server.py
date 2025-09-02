class MCPServer:
    def __init__(self, database_config: dict):
        self.db_pool = asyncpg.create_pool(**database_config)
        self.resource_handlers = {
            'db://leads': self.handle_leads_resource,
            'db://campaigns': self.handle_campaigns_resource,
            'db://interactions': self.handle_interactions_resource,
            'kg://graph': self.handle_knowledge_graph_resource
        }
        
    async def handle_jsonrpc_request(self, request: dict) -> dict:
        """Handle JSON-RPC 2.0 requests"""
        method = request.get('method')
        params = request.get('params', {})
        rpc_id = request.get('id')
        
        try:
            if method == 'resource.read':
                result = await self.read_resource(params['uri'], params.get('scope', 'read'))
            elif method == 'resource.write':
                result = await self.write_resource(params['uri'], params['data'])
            elif method == 'resource.search':
                result = await self.search_resource(params['uri'], params['query'])
            else:
                raise ValueError(f"Unknown method: {method}")
                
            # Log the request
            await self.log_request(method, params, 200, rpc_id)
            
            return {
                'jsonrpc': '2.0',
                'id': rpc_id,
                'result': result
            }
            
        except Exception as e:
            await self.log_request(method, params, 500, rpc_id)
            return {
                'jsonrpc': '2.0',
                'id': rpc_id,
                'error': {
                    'code': -32603,
                    'message': str(e)
                }
            }
            
    async def read_resource(self, uri: str, scope: str) -> dict:
        handler = self.resource_handlers.get(uri)
        if not handler:
            raise ValueError(f"Unknown resource: {uri}")
            
        return await handler('read', {'scope': scope})
        
    async def handle_leads_resource(self, operation: str, params: dict) -> dict:
        if operation == 'read':
            async with self.db_pool.acquire() as conn:
                if params.get('lead_id'):
                    result = await conn.fetchrow(
                        "SELECT * FROM leads WHERE lead_id = $1",
                        params['lead_id']
                    )
                    return dict(result) if result else None
                else:
                    results = await conn.fetch(
                        "SELECT * FROM leads ORDER BY created_at DESC LIMIT 100"
                    )
                    return [dict(r) for r in results]