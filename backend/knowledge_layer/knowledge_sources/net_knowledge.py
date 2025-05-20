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
        "You can query everything about the simulated User Equipments (UE), Cells and Base Stations in the simulated network.\n\n"
        "All knowledge entries can be queried using URL-like query keys. For example:\n"
        "  • To get the live attribute value of a user equipment, a cell, a base station or the RAN Intelligent Controller (RIC), call get_knowledge_value on one of the following queries:\n"
        '      "/net/user_equipments/attribute/{ue_imsi}/{attribute_name}"\n'
        '      "/net/cell/attribute/{cell_id}/{attribute_name}"\n'
        '      "/net/base_station/attribute/{bs_id}/{attribute_name}"\n\n'
        '      "/net/ric/attribute/{attribute_name}"\n\n'
        "  • To get the explanation of the UE, Cell, Base Station and RIC class attribute or method, call get_knowledge_explanation on one of the following queries:\n"
        '      "/net/user_equipments/attribute/{attribute_name}"\n'
        '      "/net/user_equipments/method/{method_name}"\n\n'
        '      "/net/cell/attribute/{attribute_name}"\n'
        '      "/net/cell/method/{method_name}"\n\n'
        '      "/net/base_station/attribute/{attribute_name}"\n'
        '      "/net/base_station/method/{method_name}"\n\n'
        '      "/net/ric/attribute/{attribute_name}"\n'
        '      "/net/ric/method/{method_name}"\n'
        '      "/net/ric/xapps"\n'
        '      "/net/ric/xapps/{xapp_id}"\n\n'
        "If you don't know the supported attribute or method names, you can first call get_knowledge_explanation on the following queries: \n"
        '  "/net/user_equipments"\n'
        '  "/net/cell"\n'
        '  "/net/base_station"\n'
        '  "/net/ric"\n\n'
    )


knowledge_explainer(
    key="/net",
    tags=[KnowledgeTag.KNOWLEDGE_GUIDE],
    related=[],
)(network_knowledge_root)

knowledge_getter(
    key="/net",
)(network_knowledge_root)
