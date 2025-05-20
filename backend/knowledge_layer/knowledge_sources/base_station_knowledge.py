import json
import inspect
from ..knowledge_getter import knowledge_getter
from ..knowledge_explainer import knowledge_explainer
from ..tags import KnowledgeTag
from ..relationships import KnowledgeRelationship
from network_layer.ran import BaseStation

SUPPORTED_BS_ATTRIBUTES = [
    "bs_id",
    "position_x",
    "position_y",
    "cell_list",
    "rrc_measurement_events",
    "ue_registry",
    "ue_rrc_meas_events",
    "ue_rrc_meas_event_handlers",
    "ric_control_actions",
]

SUPPORTED_BS_METHODS = [
    "receive_ue_rrc_meas_events",
    "handle_ue_authentication_and_registration",
    "handle_deregistration_request",
    "to_json",
    "init_rrc_measurement_event_handler",
    "process_ric_control_actions",
    "execute_handover",
    "step",
]


@knowledge_getter(
    key="/net/base_station/attribute/{bs_id}/{attribute_name}",
)
def base_station_attribute_getter(sim, knowledge_router, query_key, params):
    bs = sim.base_station_list.get(params["bs_id"], None)
    if not bs:
        return f"BaseStation {params['bs_id']} not found."
    attribute_name = params["attribute_name"]

    if attribute_name not in SUPPORTED_BS_ATTRIBUTES:
        return f"Attribute {attribute_name} not supported. Supported attributes: {', '.join(SUPPORTED_BS_ATTRIBUTES)}"

    if hasattr(bs, attribute_name):
        attribute = getattr(bs, attribute_name)
        if callable(attribute):
            return f"{attribute_name} is a method, query it via /net/base_station/method/{attribute_name} instead."
        if attribute_name == "cell_list":
            cell_ids = list(attribute.keys())
            return json.dumps(cell_ids)
        if attribute_name == "ue_registry":
            ue_ids = list(attribute.keys())
            return json.dumps(ue_ids)
        if isinstance(attribute, dict) or isinstance(attribute, list):
            return json.dumps(attribute)
        return str(attribute)
    else:
        return f"Attribute {attribute_name} not found in BaseStation class. Supported attributes: {', '.join(SUPPORTED_BS_ATTRIBUTES)}"


def base_station_knowledge_root(sim, knowledge_router, query_key, params):
    """
    Combined getter and explainer for the BaseStation knowledge base.
    Returns a narrative textual description of supported query routes, attributes, and methods.
    """
    text = (
        "Welcome to the BaseStation knowledge base!\n\n"
        "This knowledge base provides access to the knowledge of all simulated Base Stations (gNBs) in the network simulation.\n\n"
        "You can interact with the BaseStation knowledge base in the following ways:\n"
        "1. **Retrieve live attribute values for a specific Base Station:**\n"
        "   - Format: `/net/base_station/attribute/{bs_id}/{attribute_name}`\n"
        "2. **Get explanations for a specific attribute or method:**\n"
        "   - Attribute explanation: `/net/base_station/attribute/{attribute_name}`\n"
        "   - Method explanation: `/net/base_station/method/{method_name}`\n"
        "Supported BaseStation attributes include:\n"
        f"    {', '.join(SUPPORTED_BS_ATTRIBUTES)}\n\n"
        "Supported BaseStation methods include:\n"
        f"    {', '.join(SUPPORTED_BS_METHODS)}\n\n"
        "Use the above query formats to explore live data or request explanations for any supported attribute or method."
    )
    return text


knowledge_getter(
    key="/net/base_station",
)(base_station_knowledge_root)

knowledge_explainer(
    key="/net/base_station",
    tags=[KnowledgeTag.BS, KnowledgeTag.KNOWLEDGE_GUIDE],
    related=[],
)(base_station_knowledge_root)

# Attribute explainers


@knowledge_explainer(
    "/net/base_station/attribute/bs_id",
    tags=[KnowledgeTag.BS, KnowledgeTag.ID],
    related=[],
)
def bs_id_explainer(sim, knowledge_router, query_key, params):
    return "The `bs_id` attribute is a unique identifier assigned to each Base Station (gNB) in the network."


@knowledge_explainer(
    "/net/base_station/attribute/position_x",
    tags=[KnowledgeTag.BS, KnowledgeTag.LOCATION],
    related=[
        (KnowledgeRelationship.ASSOCIATED_WITH, "/net/cell/attribute/position_x"),
    ],
)
def bs_position_x_explainer(sim, knowledge_router, query_key, params):
    return (
        "The `position_x` attribute specifies the X-coordinate of the Base Station's location in the simulation environment. "
        "This coordinate, together with `position_y`, determines the physical placement of the base station and its cells. "
    )


@knowledge_explainer(
    "/net/base_station/attribute/position_y",
    tags=[KnowledgeTag.BS, KnowledgeTag.LOCATION],
    related=[
        (KnowledgeRelationship.ASSOCIATED_WITH, "/net/cell/attribute/position_y"),
    ],
)
def bs_position_y_explainer(sim, knowledge_router, query_key, params):
    return (
        "The `position_y` attribute specifies the Y-coordinate of the Base Station's location in the simulation environment. "
        "This coordinate, together with `position_x`, determines the physical placement of the base station and its cells."
    )


@knowledge_explainer(
    "/net/base_station/attribute/cell_list",
    tags=[KnowledgeTag.BS, KnowledgeTag.CELL],
    related=[],
)
def bs_cell_list_explainer(sim, knowledge_router, query_key, params):
    return (
        "The `cell_list` attribute is a dictionary mapping cell IDs to Cell objects managed by this Base Station. "
        "Each Base Station may manage one or more cells, each with its own configuration."
    )


@knowledge_explainer(
    "/net/base_station/attribute/ue_registry",
    tags=[KnowledgeTag.BS, KnowledgeTag.UE],
    related=[
        (
            KnowledgeRelationship.SET_BY_METHOD,
            "/net/base_station/method/handle_ue_authentication_and_registration",
        ),
        (
            KnowledgeRelationship.SET_BY_METHOD,
            "/net/base_station/method/handle_deregistration_request",
        ),
    ],
)
def bs_ue_registry_explainer(sim, knowledge_router, query_key, params):
    return (
        "The `ue_registry` attribute is a dictionary mapping UE IMSIs to registration data. "
        "It tracks all UEs currently registered with this Base Station, including their slice type, QoS profile, and serving cell. "
        "This registry is updated during UE authentication, registration, and deregistration, and is essential for managing network state, resource allocation, and mobility."
    )


@knowledge_explainer(
    "/net/base_station/attribute/rrc_measurement_events",
    tags=[KnowledgeTag.BS, KnowledgeTag.SIMULATION],
    related=[
        (
            KnowledgeRelationship.USED_BY_METHOD,
            "/net/base_station/method/init_rrc_measurement_event_handler",
        ),
        (
            KnowledgeRelationship.AFFECTS,
            "/net/base_station/attribute/ue_rrc_meas_event_handers",
        ),
    ],
)
def bs_rrc_measurement_events_explainer(sim, knowledge_router, query_key, params):
    return (
        "The `rrc_measurement_events` attribute lists the RRC measurement event types supported by this Base Station. "
        "These events are used for mobility management and handover decisions."
    )


@knowledge_explainer(
    "/net/base_station/attribute/ue_rrc_meas_events",
    tags=[KnowledgeTag.BS, KnowledgeTag.SIMULATION],
    related=[
        (
            KnowledgeRelationship.SET_BY_METHOD,
            "/net/base_station/method/receive_ue_rrc_meas_events",
        )
    ],
)
def bs_ue_rrc_meas_events_explainer(sim, knowledge_router, query_key, params):
    return (
        "The `ue_rrc_meas_events` attribute is a list that stores RRC measurement events reported by UEs to this Base Station. "
        "These events are queued for processing and may trigger actions such as handovers or other mobility management procedures."
    )


@knowledge_explainer(
    "/net/base_station/attribute/ue_rrc_meas_event_handers",
    tags=[KnowledgeTag.BS, KnowledgeTag.CODE],
    related=[
        (
            KnowledgeRelationship.SET_BY_METHOD,
            "/net/base_station/method/init_rrc_measurement_event_handler",
        ),
        (
            KnowledgeRelationship.USED_BY_METHOD,
            "/net/base_station/method/step",
        ),
    ],
)
def bs_ue_rrc_meas_event_handers_explainer(sim, knowledge_router, query_key, params):
    return (
        "The `ue_rrc_meas_event_handers` attribute is a dictionary mapping RRC measurement event IDs to their corresponding handler functions. "
        "Each handler processes a specific type of RRC measurement event when it is received by the Base Station."
    )


@knowledge_explainer(
    "/net/base_station/attribute/ric_control_actions",
    tags=[KnowledgeTag.BS, KnowledgeTag.SIMULATION],
    related=[
        (
            KnowledgeRelationship.USED_BY_METHOD,
            "/net/base_station/method/process_ric_control_actions",
        ),
        (KnowledgeRelationship.SET_BY_METHOD, "/net/base_station/method/step"),
    ],
)
def bs_ric_control_actions_explainer(sim, knowledge_router, query_key, params):
    return (
        "The `ric_control_actions` attribute contains a list of RIC (RAN Intelligent Controller) control actions to be processed by the Base Station. "
        "These actions may include handover commands and other network control operations."
    )


# Method explainers


@knowledge_explainer(
    "/net/base_station/method/receive_ue_rrc_meas_events",
    tags=[KnowledgeTag.BS, KnowledgeTag.CODE],
    related=[
        (
            KnowledgeRelationship.CALLED_BY_METHOD,
            "/net/ue/method/check_rrc_meas_events_to_monitor",
        ),
        (
            KnowledgeRelationship.SET_ATTRIBUTE,
            "/net/base_station/attribute/ue_rrc_meas_events",
        ),
    ],
)
def bs_receive_ue_rrc_meas_events_explainer(sim, knowledge_router, query_key, params):
    code = inspect.getsource(getattr(BaseStation, "receive_ue_rrc_meas_events"))
    explanation = (
        "The `receive_ue_rrc_meas_events` method is called when a UE reports an RRC measurement event to the Base Station. "
        "It performs several checks to ensure the event is valid (such as verifying the UE and current cell), then appends the event to the Base Station's internal event queue (`ue_rrc_meas_events`). "
        "This queue is processed during each simulation step, allowing the Base Station to react to UE mobility and signal quality changes. "
        "This method is a key entry point for mobility management and is typically triggered by UEs as they monitor their radio environment."
    )
    return f"```python\n{code}\n```\n\n{explanation}"


@knowledge_explainer(
    "/net/base_station/method/handle_ue_authentication_and_registration",
    tags=[KnowledgeTag.BS, KnowledgeTag.CODE],
    related=[
        (
            KnowledgeRelationship.SET_ATTRIBUTE,
            "/net/base_station/attribute/ue_registry",
        ),
        (KnowledgeRelationship.CALL_METHOD, "/net/cell/method/register_ue"),
        (
            KnowledgeRelationship.CALLED_BY_METHOD,
            "/net/ue/method/authenticate_and_register",
        ),
    ],
)
def bs_handle_ue_auth_and_reg_explainer(sim, knowledge_router, query_key, params):
    code = inspect.getsource(
        getattr(BaseStation, "handle_ue_authentication_and_registration")
    )
    explanation = (
        "The `handle_ue_authentication_and_registration` method authenticates a UE and registers it with the Base Station and its serving cell. "
        "It first interacts with the core network to perform authentication and retrieve the appropriate slice type and QoS profile for the UE. "
        "The method then updates the `ue_registry` to track the UE's registration state and calls the cell's `register_ue` method to allocate radio resources. "
        "This process is essential for enabling UEs to access network services and is a prerequisite for all subsequent communication and mobility events."
    )
    return f"```python\n{code}\n```\n\n{explanation}"


@knowledge_explainer(
    "/net/base_station/method/handle_deregistration_request",
    tags=[KnowledgeTag.BS, KnowledgeTag.CODE],
    related=[
        (KnowledgeRelationship.CALL_METHOD, "/net/cell/method/deregister_ue"),
        (
            KnowledgeRelationship.SET_ATTRIBUTE,
            "/net/base_station/attribute/ue_registry",
        ),
        (KnowledgeRelationship.CALLED_BY_METHOD, "/net/ue/method/deregister"),
    ],
)
def bs_handle_deregistration_request_explainer(
    sim, knowledge_router, query_key, params
):
    code = inspect.getsource(getattr(BaseStation, "handle_deregistration_request"))
    explanation = (
        "The `handle_deregistration_request` method processes a UE's deregistration request. "
        "It interacts with the core network to update the UE's state, releases radio resources in the serving cell, and removes the UE from the Base Station's registry. "
        "Additionally, it cleans up any pending RRC measurement events associated with the UE. "
        "This method ensures that network resources are efficiently managed and that UEs are properly removed from the simulation when their session ends."
    )
    return f"```python\n{code}\n```\n\n{explanation}"


@knowledge_explainer(
    "/net/base_station/method/init_rrc_measurement_event_handler",
    tags=[KnowledgeTag.BS, KnowledgeTag.CODE],
    related=[
        (
            KnowledgeRelationship.SET_ATTRIBUTE,
            "/net/base_station/attribute/ue_rrc_meas_event_handers",
        )
    ],
)
def bs_init_rrc_meas_event_handler_explainer(sim, knowledge_router, query_key, params):
    code = inspect.getsource(getattr(BaseStation, "init_rrc_measurement_event_handler"))
    explanation = (
        "The `init_rrc_measurement_event_handler` method registers a handler function for a specific RRC measurement event type. "
        "This allows the Base Station to define custom logic for processing different types of measurement events reported by UEs. "
        "Handlers are stored in the `ue_rrc_meas_event_handers` dictionary and invoked during each simulation step as events are processed. "
    )
    return f"```python\n{code}\n```\n\n{explanation}"


@knowledge_explainer(
    "/net/base_station/method/process_ric_control_actions",
    tags=[KnowledgeTag.BS, KnowledgeTag.CODE],
    related=[
        (
            KnowledgeRelationship.CALL_METHOD,
            "/net/base_station/method/execute_handover",
        ),
        (
            KnowledgeRelationship.USES_ATTRIBUTE,
            "/net/base_station/attribute/ric_control_actions",
        ),
        (KnowledgeRelationship.CALLED_BY_METHOD, "/net/base_station/method/step"),
    ],
)
def bs_process_ric_control_actions_explainer(sim, knowledge_router, query_key, params):
    code = inspect.getsource(getattr(BaseStation, "process_ric_control_actions"))
    explanation = (
        "The `process_ric_control_actions` method processes all pending RIC (RAN Intelligent Controller) control actions for the Base Station. "
        "Currently, it primarily handles handover actions, ensuring that only one handover is executed per simulation step. "
        "This is because once a handover for one UE is completed, everything else (load of relevant cells, other UE's SINR etc) is updated. "
        "The method checks for conflicting or duplicate actions, merges or rejects them as needed, and then calls `execute_handover` to perform the actual handover. "
    )
    return f"```python\n{code}\n```\n\n{explanation}"


@knowledge_explainer(
    "/net/base_station/method/execute_handover",
    tags=[KnowledgeTag.BS, KnowledgeTag.CODE],
    related=[
        (
            KnowledgeRelationship.CALLED_BY_METHOD,
            "/net/base_station/method/process_ric_control_actions",
        ),
        (
            KnowledgeRelationship.SET_ATTRIBUTE,
            "/net/base_station/attribute/ue_registry",
        ),
        (KnowledgeRelationship.CALL_METHOD, "/net/cell/method/deregister_ue"),
        (KnowledgeRelationship.CALL_METHOD, "/net/cell/method/register_ue"),
        (
            KnowledgeRelationship.CALL_METHOD,
            "/net/ue/method/execute_handover",
        ),
    ],
)
def bs_execute_handover_explainer(sim, knowledge_router, query_key, params):
    code = inspect.getsource(getattr(BaseStation, "execute_handover"))
    explanation = (
        "The `execute_handover` method performs a handover for a UE from a source cell to a target cell, updating all relevant data structures. "
        "It ensures that the UE is properly deregistered from the source cell, registered with the target cell, and that the Base Station's UE registry reflects the new association. "
        "If the handover is inter-base-station, it also updates the registries of both the source and target base stations. "
        "This method is central to mobility management and enables realistic simulation of handover procedures in the RAN."
    )
    return f"```python\n{code}\n```\n\n{explanation}"


@knowledge_explainer(
    "/net/base_station/method/step",
    tags=[KnowledgeTag.BS, KnowledgeTag.SIMULATION, KnowledgeTag.CODE],
    related=[
        (KnowledgeRelationship.CALL_METHOD, "/net/cell/method/step"),
        (
            KnowledgeRelationship.CALL_METHOD,
            "/net/base_station/method/process_ric_control_actions",
        ),
        (
            KnowledgeRelationship.USES_ATTRIBUTE,
            "/net/base_station/attribute/ue_rrc_meas_events",
        ),
    ],
)
def bs_step_explainer(sim, knowledge_router, query_key, params):
    code = inspect.getsource(getattr(BaseStation, "step"))
    explanation = (
        "The `step` method advances the simulation state of the Base Station by one time step. "
        "It updates all managed cells, processes RRC measurement events reported by UEs, and executes any pending RIC control actions (such as handovers). "
        "This method is called once per simulation tick and is responsible for orchestrating the dynamic behavior of the base station and its associated cells. "
        "It ensures that mobility, resource allocation, and control logic are applied consistently throughout the simulation."
    )
    return f"```python\n{code}\n```\n\n{explanation}"
