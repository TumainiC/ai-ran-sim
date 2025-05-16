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
            "available_queries": [
                "/net/ue",
                "/net/ue/attribute/{ue_imsi}/{attribute_name}",
                "/net/ue/method/{method_name}",
                "/net/cell/attribute/{cell_id}/{attribute_name}",
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
        "For example, use the query key `/net/ue` to get a list of UE attributes and UE methods in this database.\n"
        "You can also use the query key `/net/cell` to get a list of cell attributes and cell methods in this database.\n"
        "Then, you may use queries keys such as `/net/ue/attribute/{ue_imsi}/downlink_bitrate` or `/net/ue/method/power_up` to get the live value or explanation of the knowledge entry.\n"
    )
