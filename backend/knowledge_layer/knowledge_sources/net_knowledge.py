import json
from ..knowledge_getter import knowledge_getter
from ..knowledge_explainer import knowledge_explainer
from ..tags import KnowledgeTag


@knowledge_getter(
    key="/net",
)
def network_knowledge_getter(sim, knowledge_router, query_key, params):
    return json.dumps(
        {
            "description": "Network knowledge layer",
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
                # Add more query keys as needed
            ],
        },
        indent=4,
    )


@knowledge_explainer(
    key="/net",
    tags=[KnowledgeTag.KNOWLEDGE_GUIDE],
    related=[],
)
def network_knowledge_explainer(sim, knowledge_router, query_key, params):
    return (
        "Welcome to the network knowledge layer!\n"
        "You can query everything about the network here.\n"
        "The network knowledge layer is divided into two parts: UE knowledge (/net/ue) and cell knowledge (/net/cell).\n"
    )
