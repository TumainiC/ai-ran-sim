from .router import knowledge_router, register_knowledge_routes
from . import knowledge_sources  # triggers decorators. Do not remove this line.


def initialize_knowledge(sim):
    register_knowledge_routes(sim)
    return knowledge_router
