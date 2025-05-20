from ..knowledge_entry import knowledge_entry
from ..tags import KnowledgeTag


@knowledge_entry(
    key="/net",
    tags=[KnowledgeTag.KNOWLEDGE_GUIDE],
    related=[],
)
def network_knowledge_root(sim, knowledge_router, query_key, params):
    """
    Combined getter and explainer for the network knowledge layer.
    Returns both a textual description and a list of supported query routes for User Equipments (UE).
    """
    return (
        "📘 **Welcome to the Network Knowledge Database!**\n\n"
        "You can query everything about the simulated User Equipments (UE) in the simulated network.\n\n"
        "call `/docs/user_equipments` for a full documentation on the UE knowledge database.\n"
    )
