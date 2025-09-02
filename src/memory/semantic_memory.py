class SemanticMemory:
    """Domain knowledge graph storage"""
    def __init__(self):
        self.graph = NetworkXGraph()
        
    async def add_relationship(self, subject: str, predicate: str, object: str, weight: float):
        self.graph.add_edge(subject, object, predicate=predicate, weight=weight)
        
    async def query_related(self, entity: str, max_depth: int = 2) -> list:
        return list(nx.neighbors(self.graph, entity))