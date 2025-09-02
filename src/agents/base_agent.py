class BaseAgent:
    def __init__(self, agent_id: str, mcp_client: MCPClient):
        self.agent_id = agent_id
        self.mcp_client = mcp_client
        self.memory = MemorySystem(agent_id)
        self.rpc_server = JSONRPCServer()
        
    async def handle_handoff(self, context: HandoffContext) -> bool:
        """Handle agent handoff with context preservation"""
        pass
        
    async def escalate(self, reason: str, context: dict) -> bool:
        """Escalate to human manager"""
        pass