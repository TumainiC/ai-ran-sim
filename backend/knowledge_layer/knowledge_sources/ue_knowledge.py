from ..knowledge_getter import knowledge_getter
from ..knowledge_explainer import knowledge_explainer
from ..tags import KnowledgeTag
from ..relationships import KnowledgeRelationship
from .ue_attribute_knowledge import SUPPORTED_UE_ATTRIBUTES
from .ue_method_knowledge import SUPPORTED_UE_METHODS

# Resource-oriented RESTful API structure

# Collection of UEs:
# /net/ues — List all UEs or their IDs

# Single UE resource:
# /net/ues/{ue_imsi} — Get all attributes for a specific UE

# Single UE attribute:
# /net/ues/{ue_imsi}/attributes/{attribute_name} — Get a specific attribute value

# All attributes for a UE:
# /net/ues/{ue_imsi}/attributes — Get all attributes as a dictionary

# All methods for a UE:
# /net/ues/{ue_imsi}/methods — List callable methods for this UE

# Method explanation:
# /net/ues/methods/{method_name} — Get explanation for a method

# Attribute explanation:
# /net/ues/attributes/{attribute_name} — Get explanation for an attribute

def ue_knowledge_root(sim, knowledge_router, query_key, params):
    """
    Combined getter and explainer for the UE knowledge base.
    Returns a narrative textual description of supported query routes, attributes, and methods.
    """
    text = (
        "Welcome to the User Equipment (UE) knowledge base!\n\n"
        "This knowledge base provides access to the knowledge of all simulated UEs in the network simulation.\n\n"
        "You can interact with the UE knowledge base in the following ways:\n"
        "1. **Retrieve live attribute values for a specific UE:**\n"
        "   - Format: `/net/user_equipments/attribute/{ue_imsi}/{attribute_name}`\n"
        "2. **Get explanations for a specific attribute or method:**\n"
        "   - Attribute explanation: `/net/user_equipments/attribute/{attribute_name}`\n"
        "   - Method explanation: `/net/user_equipments/method/{method_name}`\n\n"
        "Supported UE attributes include:\n"
        f"    {', '.join(SUPPORTED_UE_ATTRIBUTES)}\n\n"
        "Supported UE methods include:\n"
        f"    {', '.join(SUPPORTED_UE_METHODS)}\n\n"
        "Use the above query formats to explore live data or request explanations for any supported attribute or method.\n"
        "For example, `/net/user_equipments/attribute/IMSI_1/downlink_bitrate` returns the downlink bitrate for a specific UE, "
        "while `/net/user_equipments/method/power_up` provides details about the UE power-up procedure."
    )
    return text


knowledge_getter(
    key="/net/user_equipments",
)(ue_knowledge_root)

knowledge_explainer(
    key="/net/user_equipments",
    tags=[KnowledgeTag.UE, KnowledgeTag.KNOWLEDGE_GUIDE],
    related=[],
)(ue_knowledge_root)
