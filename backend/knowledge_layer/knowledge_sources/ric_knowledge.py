import json
import inspect
from ..knowledge_getter import knowledge_getter
from ..knowledge_explainer import knowledge_explainer
from ..tags import KnowledgeTag
from ..relationships import KnowledgeRelationship
from network_layer.ric import NearRTRIC

from network_layer.xApps.xapp_base import xAppBase


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
    ric = getattr(sim, "nearRT_ric", None)
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
            xapp_ids = list(attribute.keys())
            return json.dumps(xapp_ids)

        if isinstance(attribute, (dict, list)):
            return json.dumps(attribute)

        return str(attribute)
    else:
        return f"Attribute {attribute_name} not found in RIC class. Supported attributes: {', '.join(SUPPORTED_RIC_ATTRIBUTES)}"


def ric_knowledge_root(sim, knowledge_router, query_key, params):
    ric = getattr(sim, "nearRT_ric", None)
    if not ric or not hasattr(ric, "xapp_list"):
        return "RIC or xApp list not found."
    xapp_ids = list(ric.xapp_list.keys())
    text = (
        "Welcome to the Near Real-Time RAN Intelligent Controller (NearRT RIC) knowledge base!\n\n"
        "This knowledge base provides access to the simulated NearRT RIC, which orchestrates xApps and manages RAN control in the network simulation.\n\n"
        "You can interact with the RIC knowledge base in the following ways:\n"
        "1. **Retrieve live attribute values for the RIC:**\n"
        "   - Format: `/net/ric/attribute/{attribute_name}`\n"
        "2. **Get explanations for a specific RIC attribute or method:**\n"
        "   - Attribute explanation: `/net/ric/attribute/{attribute_name}`\n"
        "   - Method explanation: `/net/ric/method/{method_name}`\n"
        "3. **Explore loaded xApps:**\n"
        "   - List all loaded xApps: `/net/ric/xapps`\n"
        "   - Get source code and explanation for a specific xApp: `/net/ric/xapps/{xapp_id}`\n"
        "Supported RIC attributes include:\n"
        f"    {', '.join(SUPPORTED_RIC_ATTRIBUTES)}\n\n"
        "Supported RIC methods include:\n"
        f"    {', '.join(SUPPORTED_RIC_METHODS)}\n\n"
        "List of loaded xApps:\n"
        f"    {json.dumps(xapp_ids, indent=2)}\n\n"
        "Use the above query formats to explore live data or request explanations for any supported attribute, method, or xApp."
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
        "Each xApp implements specific RAN control logic (such as handover, load balancing, etc.) and is dynamically loaded by the RIC at runtime. "
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
        "The `load_xApps` method dynamically discovers and loads all available xApps from the xApps directory. "
        "It instantiates each xApp, assigns it to the RIC, and stores it in the `xapp_list` attribute. "
        "After loading, it calls the `start` method on each xApp to initialize their operation. "
        "This enables modular, plug-and-play RAN control logic, allowing new xApps to be added to the simulation without modifying the RIC core code. "
        "The method also ensures that no duplicate xApp IDs are loaded, maintaining the integrity of the xApp registry."
    )
    return f"```python\n{code}\n```\n\n{explanation}"


# --- xApp knowledge routes ---


def ric_xapps_root(sim, knowledge_router, query_key, params):
    ric = getattr(sim, "nearRT_ric", None)
    if not ric or not hasattr(ric, "xapp_list"):
        return "RIC or xApp list not found."
    xapp_ids = list(ric.xapp_list.keys())
    try:
        base_code = inspect.getsource(xAppBase)
    except Exception:
        base_code = "Source code unavailable."
    base_doc = (
        inspect.getdoc(xAppBase) or "No docstring/documentation available for xAppBase."
    )
    return (
        "xApps are modular applications loaded by the NearRT RIC to implement specific RAN control logic (e.g., handover, load balancing, etc.).\n"
        "The following xApps are currently loaded:\n"
        f"{json.dumps(xapp_ids, indent=2)}\n\n"
        "Query `/net/ric/xapps/{xapp_id}` to view the source code and explanation for a specific xApp.\n\n"
        "## xAppBase (Base class for all xApps)\n"
        f"**Documentation:**\n{base_doc}\n\n"
        f"**Source code:**\n```python\n{base_code}\n```"
    )


knowledge_getter(
    key="/net/ric/xapps",
)(ric_xapps_root)

knowledge_explainer(
    "/net/ric/xapps",
    tags=[KnowledgeTag.KNOWLEDGE_GUIDE, KnowledgeTag.RIC],
    related=[],
)(ric_xapps_root)


def ric_xapp_detail(sim, knowledge_router, query_key, params):
    ric = getattr(sim, "nearRT_ric", None)
    if not ric or not hasattr(ric, "xapp_list"):
        return "RIC or xApp list not found."
    xapp_id = params["xapp_id"]
    xapp = ric.xapp_list.get(xapp_id)
    if not xapp:
        return f"xApp '{xapp_id}' not found. Loaded xApps: {list(ric.xapp_list.keys())}"
    # Get source code
    try:
        code = inspect.getsource(xapp.__class__)
    except Exception:
        code = "Source code unavailable."
    doc = (
        inspect.getdoc(xapp.__class__)
        or "No docstring/documentation available for this xApp."
    )
    return (
        f"## xApp: {xapp_id}\n\n"
        f"**Documentation:**\n{doc}\n\n"
        f"**Source code:**\n```python\n{code}\n```"
    )


knowledge_getter(
    key="/net/ric/xapps/{xapp_id}",
)(ric_xapp_detail)

knowledge_explainer(
    "/net/ric/xapps/{xapp_id}",
    tags=[KnowledgeTag.RIC],
    related=[],
)(ric_xapp_detail)
