from ..knowledge_getter import knowledge_getter
from ..knowledge_explainer import knowledge_explainer
from ..tags import KnowledgeTag


def network_knowledge_root(sim, knowledge_router, query_key, params):
    """
    Combined getter and explainer for the network knowledge layer.
    Returns both a textual description and a list of supported query routes.
    """
    return (
        "Welcome to the network knowledge database!\n"
        "You can query everything about the User Equipments (UE) and Cells in the simulated network.\n\n"
        "All knowledge entries can be queried using URL-like query keys. For example:\n"
        "  • To get the live attribute value of a user equipment or a cell, call:\n"
        '      get_knowledge_value("/net/ue/attribute/{ue_imsi}/{attribute_name}")\n'
        '      get_knowledge_value("/net/cell/attribute/{cell_id}/{attribute_name}")\n\n'
        "  • To get the explanation of the simulated UE class attribute or method, call:\n"
        '      get_knowledge_explanation("/net/ue/attribute/{attribute_name}")\n'
        '      get_knowledge_explanation("/net/ue/method/{method_name}")\n\n'
        "  • To get the explanation of the simulated Cell class attribute or method, call:\n"
        '      get_knowledge_explanation("/net/cell/attribute/{attribute_name}")\n'
        '      get_knowledge_explanation("/net/cell/method/{method_name}")\n\n'
        "If you don't know the supported UE or Cell attributes or methods, you can first call\n"
        '  get_knowledge_explanation("/net/ue")\n'
        '  or get_knowledge_explanation("/net/cell")'
    )


knowledge_explainer(
    key="/net",
    tags=[KnowledgeTag.KNOWLEDGE_GUIDE],
    related=[],
)(network_knowledge_root)

knowledge_getter(
    key="/net",
)(network_knowledge_root)
