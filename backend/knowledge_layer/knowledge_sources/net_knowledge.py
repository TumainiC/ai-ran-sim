import json
from ..knowledge_getter import knowledge_getter
from ..knowledge_explainer import knowledge_explainer
from ..tags import KnowledgeTag


def network_knowledge_root(sim, knowledge_router, query_key, params):
    """
    Combined getter and explainer for the network knowledge layer.
    Returns both a textual description and a list of supported query routes.
    """
    data = {
        "description": (
            "Welcome to the network knowledge layer!\n"
            "You can query everything about the the User Equipments (UE) and Cells in the simulated network.\n"
        ),
        "queries_for_getting_knowledge_value": [
            "/net/ue",
            "/net/ue/attribute/{ue_imsi}/{attribute_name}",
            "/net/ue/method/{method_name}",
            "/net/cell",
            "/net/cell/attribute/{cell_id}/{attribute_name}",
            "/net/cell/method/{method_name}",
        ],
        "queries_for_getting_knowledge_explanation": [
            "/net/ue",
            "/net/ue/attribute/{attribute_name}",
            "/net/ue/method/{method_name}",
            "/net/cell",
            "/net/cell/attribute/{attribute_name}",
            "/net/cell/method/{method_name}",
        ],
        "usage": (
            "Use the above routes to retrieve either the value or the explanation of UE, or cell knowledge. "
            "For example, `/net/ue/attribute/{ue_imsi}/downlink_bitrate` returns the downlink bitrate for a specific UE, "
            "while `/net/cell/method/allocate_prb` provides details about the PRB allocation method in the cell."
        ),
    }
    return json.dumps(data, indent=4)


knowledge_explainer(
    key="/net",
    tags=[KnowledgeTag.KNOWLEDGE_GUIDE],
    related=[],
)(network_knowledge_root)

knowledge_getter(
    key="/net",
)(network_knowledge_root)
