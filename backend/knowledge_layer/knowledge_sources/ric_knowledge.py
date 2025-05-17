import json
import inspect
from ..knowledge_getter import knowledge_getter
from ..knowledge_explainer import knowledge_explainer
from ..tags import KnowledgeTag
from ..relationships import KnowledgeRelationship
from network_layer.ric import NearRTRIC

SUPPORTED_RIC_ATTRIBUTES = [
    "ric_id",
    "xapp_list",
]

SUPPORTED_RIC_METHODS = [
    "load_xApps",
]


@knowledge_getter(
    key="/net/ric/attribute/{attribute_name}",
)
def ric_attribute_getter(sim, knowledge_router, query_key, params):
    ric = getattr(sim, "ric", None)
    if not ric:
        return "RIC instance not found in simulation."
    attribute_name = params["attribute_name"]

    if attribute_name not in SUPPORTED_RIC_ATTRIBUTES:
        return f"Attribute {attribute_name} not supported. Supported attributes: {', '.join(SUPPORTED_RIC_ATTRIBUTES)}"

    if hasattr(ric, attribute_name):
        attribute = getattr(ric, attribute_name)
        if callable(attribute):
            return f"{attribute_name} is a method, query it via /net/ric/method/{attribute_name} instead."

        if attribute_name == "xapp_list":
            # return a list of xApp IDs instead of the full xApp objects
            xapp_ids = [xapp_id for xapp_id in attribute.keys()]
            return json.dumps(xapp_ids)

        if isinstance(attribute, dict) or isinstance(attribute, list):
            return json.dumps(attribute)

        return str(attribute)
    else:
        return f"Attribute {attribute_name} not found in RIC class. Supported attributes: {', '.join(SUPPORTED_RIC_ATTRIBUTES)}"


def ric_knowledge_root(sim, knowledge_router, query_key, params):
    """
    Combined getter and explainer for the NearRTRIC knowledge base.
    Returns a narrative textual description of supported query routes, attributes, and methods.
    """
    text = (
        "Welcome to the Near Real-Time RAN Intelligent Controller (NearRT RIC) knowledge base!\n\n"
        "This knowledge base provides access to the knowledge of the simulated NearRT RIC, which is responsible for orchestrating xApps and managing RAN control in the network simulation.\n\n"
        "You can interact with the RIC knowledge base in the following ways:\n"
        "1. **Retrieve live attribute values for the RIC:**\n"
        "   - Format: `/net/ric/attribute/{attribute_name}`\n"
        "2. **Get explanations for a specific attribute or method:**\n"
        "   - Attribute explanation: `/net/ric/attribute/{attribute_name}`\n"
        "   - Method explanation: `/net/ric/method/{method_name}`\n"
        "Supported RIC attributes include:\n"
        f"    {', '.join(SUPPORTED_RIC_ATTRIBUTES)}\n\n"
        "Supported RIC methods include:\n"
        f"    {', '.join(SUPPORTED_RIC_METHODS)}\n\n"
        "Use the above query formats to explore live data or request explanations for any supported attribute or method."
    )
    return text


knowledge_getter(
    key="/net/ric",
)(ric_knowledge_root)

knowledge_explainer(
    key="/net/ric",
    tags=[KnowledgeTag.KNOWLEDGE_GUIDE],
    related=[],
)(ric_knowledge_root)

# Attribute explainers


@knowledge_explainer(
    "/net/ric/attribute/ric_id",
    tags=[KnowledgeTag.KNOWLEDGE_GUIDE],
    related=[],
)
def ric_id_explainer(sim, knowledge_router, query_key, params):
    return (
        "The `ric_id` attribute is a unique identifier for the Near Real-Time RAN Intelligent Controller (NearRT RIC) instance. "
        "It distinguishes this RIC from other possible RICs in a multi-controller simulation environment."
    )


@knowledge_explainer(
    "/net/ric/attribute/xapp_list",
    tags=[KnowledgeTag.KNOWLEDGE_GUIDE, KnowledgeTag.CODE],
    related=[
        (KnowledgeRelationship.SET_BY_METHOD, "/net/ric/method/load_xApps"),
    ],
)
def ric_xapp_list_explainer(sim, knowledge_router, query_key, params):
    return (
        "The `xapp_list` attribute is a dictionary mapping xApp IDs to their instantiated xApp objects. "
        "Each xApp can implement a specific RAN control logic (such as handover, load balancing, etc.) and is dynamically loaded by the RIC at runtime. "
        "This attribute allows the RIC to manage, start, and coordinate all xApps in the simulation."
    )


# Method explainers


@knowledge_explainer(
    "/net/ric/method/load_xApps",
    tags=[KnowledgeTag.KNOWLEDGE_GUIDE, KnowledgeTag.CODE],
    related=[
        (KnowledgeRelationship.SET_ATTRIBUTE, "/net/ric/attribute/xapp_list"),
        (KnowledgeRelationship.CALLED_BY_METHOD, "/sim/method/network_setup"),
    ],
)
def ric_load_xapps_explainer(sim, knowledge_router, query_key, params):
    code = inspect.getsource(getattr(NearRTRIC, "load_xApps"))
    explanation = (
        "The `load_xApps` method is responsible for dynamically discovering and loading all available xApps from the xApps directory. "
        "It instantiates each xApp, assigns it to the RIC, and stores it in the `xapp_list` attribute. "
        "After loading, it calls the `start` method on each xApp to initialize their operation. "
        "This mechanism enables modular, plug-and-play RAN control logic, allowing new xApps to be added to the simulation without modifying the RIC core code. "
        "The method also ensures that no duplicate xApp IDs are loaded, maintaining the integrity of the xApp registry."
    )
    return f"```python\n{code}\n```\n\n{explanation}"
