import json
import inspect
from ..knowledge_getter import knowledge_getter
from ..knowledge_explainer import knowledge_explainer
from ..tags import KnowledgeTag
from ..relationships import KnowledgeRelationship
from network_layer.simulation_engine import SimulationEngine

SUPPORTED_SIM_ATTRIBUTES = [
    "sim_started",
    "sim_step",
    "base_station_list",
    "cell_list",
    "ue_list",
    "global_UE_counter",
    "logs",
]

SUPPORTED_SIM_METHODS = [
    "network_setup",
    "spawn_random_ue",
    "add_ue",
    "spawn_UEs",
    "step_UEs",
    "remove_UE",
    "step_BSs",
    "step",
    "start_simulation",
    "stop",
    "to_json",
]


@knowledge_getter(
    key="/sim/attribute/{attribute_name}",
)
def sim_attribute_getter(sim, knowledge_router, query_key, params):
    attribute_name = params["attribute_name"]

    if attribute_name not in SUPPORTED_SIM_ATTRIBUTES:
        return f"Attribute {attribute_name} not supported. Supported attributes: {', '.join(SUPPORTED_SIM_ATTRIBUTES)}"

    if hasattr(sim, attribute_name):
        attribute = getattr(sim, attribute_name)
        if callable(attribute):
            return f"{attribute_name} is a method, query it via /sim/method/{attribute_name} instead."
        if (
            attribute_name == "base_station_list"
            or attribute_name == "cell_list"
            or attribute_name == "ue_list"
        ):
            # we can only return the keys of the dict not the base station, cell or ue objects.
            return json.dumps(list(attribute.keys()))
        if isinstance(attribute, dict) or isinstance(attribute, list):
            return json.dumps(attribute)
        return str(attribute)
    else:
        return f"Attribute {attribute_name} not found in SimulationEngine class. Supported attributes: {', '.join(SUPPORTED_SIM_ATTRIBUTES)}"


def sim_knowledge_root(sim, knowledge_router, query_key, params):
    """
    Combined getter and explainer for the SimulationEngine knowledge base.
    Returns a narrative textual description of supported query routes, attributes, and methods.
    """
    text = (
        "Welcome to the Simulation Engine knowledge base!\n\n"
        "This knowledge base provides access to the core simulation engine that orchestrates the entire network simulation, "
        "including the management of base stations, cells, UEs, and simulation steps.\n\n"
        "You can interact with the SimulationEngine knowledge base in the following ways:\n"
        "1. **Get real-time attribute values of the simulation engine instance:**\n"
        "   - Format: `/sim/attribute/{attribute_name}`\n"
        "2. **Get explanations for a specific attribute or method:**\n"
        "   - Attribute explanation: `/sim/attribute/{attribute_name}`\n"
        "   - Method explanation: `/sim/method/{method_name}`\n"
        "Supported SimulationEngine attributes include:\n"
        f"    {', '.join(SUPPORTED_SIM_ATTRIBUTES)}\n\n"
        "Supported SimulationEngine methods include:\n"
        f"    {', '.join(SUPPORTED_SIM_METHODS)}\n\n"
        "Use the above query formats to explore live data or request explanations for any supported attribute or method.\n"
        "For example, you can get the list of base stations in the simulation by querying get_knowledge_value(`/sim/attribute/base_station_list`).\n"
        "or you can get source code and explanation on the simulation step method by querying get_knowledge_explanation(`/sim/method/step`).\n\n"
    )
    return text


knowledge_getter(
    key="/sim",
)(sim_knowledge_root)

knowledge_explainer(
    key="/sim",
    tags=[KnowledgeTag.SIMULATION, KnowledgeTag.KNOWLEDGE_GUIDE],
    related=[],
)(sim_knowledge_root)

# Attribute explainers


@knowledge_explainer(
    "/sim/attribute/sim_started",
    tags=[KnowledgeTag.SIMULATION],
    related=[],
)
def sim_started_explainer(sim, knowledge_router, query_key, params):
    return (
        "The `sim_started` attribute is a boolean flag indicating whether the simulation is currently running. "
        "It is set to `True` when the simulation is started and `False` when stopped or not yet started. "
        "This flag is used to control the main simulation loop and prevent multiple concurrent runs."
    )


@knowledge_explainer(
    "/sim/attribute/sim_step",
    tags=[KnowledgeTag.SIMULATION],
    related=[],
)
def sim_step_attribute_explainer(sim, knowledge_router, query_key, params):
    return (
        "The `sim_step` attribute tracks the current time step of the simulation. "
        "It is incremented at each iteration of the simulation loop."
    )


@knowledge_explainer(
    "/sim/attribute/base_station_list",
    tags=[KnowledgeTag.SIMULATION, KnowledgeTag.BS],
    related=[
        (KnowledgeRelationship.HAS_ATTRIBUTE, "/net/base_station"),
    ],
)
def sim_base_station_list_explainer(sim, knowledge_router, query_key, params):
    return (
        "The `base_station_list` attribute is a dictionary mapping base station IDs to BaseStation objects managed by the simulation engine. "
        "It provides centralized access to all base stations in the simulation and is used for network setup, resource allocation, and mobility management."
    )


@knowledge_explainer(
    "/sim/attribute/cell_list",
    tags=[KnowledgeTag.SIMULATION, KnowledgeTag.CELL],
    related=[
        (KnowledgeRelationship.HAS_ATTRIBUTE, "/net/cell"),
    ],
)
def sim_cell_list_explainer(sim, knowledge_router, query_key, params):
    return (
        "The `cell_list` attribute is a dictionary mapping cell IDs to Cell objects managed by the simulation engine. "
        "It allows the simulation to efficiently access and update the state of all cells in the network."
    )


@knowledge_explainer(
    "/sim/attribute/ue_list",
    tags=[KnowledgeTag.SIMULATION, KnowledgeTag.UE],
    related=[
        (KnowledgeRelationship.HAS_ATTRIBUTE, "/net/ue"),
    ],
)
def sim_ue_list_explainer(sim, knowledge_router, query_key, params):
    return (
        "The `ue_list` attribute is a dictionary mapping UE IMSIs to UE objects currently present in the simulation. "
        "It is updated as UEs are spawned, move, or deregister, and is essential for tracking all active UEs in the network."
    )


@knowledge_explainer(
    "/sim/attribute/global_UE_counter",
    tags=[KnowledgeTag.SIMULATION, KnowledgeTag.UE],
    related=[],
)
def sim_global_UE_counter_explainer(sim, knowledge_router, query_key, params):
    return (
        "The `global_UE_counter` attribute is an integer counter that tracks the total number of UEs ever created in the simulation. "
        "It is used to assign unique IMSIs to new UEs and ensures that each UE can be uniquely identified."
    )


@knowledge_explainer(
    "/sim/attribute/logs",
    tags=[KnowledgeTag.SIMULATION],
    related=[],
)
def sim_logs_explainer(sim, knowledge_router, query_key, params):
    return (
        "The `logs` attribute is a list of log messages generated during the simulation. "
        "It records significant events, errors, and state changes, providing a trace of simulation activity for debugging and analysis."
    )


# Method explainers


@knowledge_explainer(
    "/sim/method/network_setup",
    tags=[KnowledgeTag.SIMULATION, KnowledgeTag.CODE],
    related=[
        (KnowledgeRelationship.SET_ATTRIBUTE, "/sim/attribute/core_network"),
        (KnowledgeRelationship.CALL_METHOD, "/sim/method/add_base_station"),
        (KnowledgeRelationship.SET_ATTRIBUTE, "/sim/attribute/nearRT_ric"),
    ],
)
def sim_network_setup_explainer(sim, knowledge_router, query_key, params):
    code = inspect.getsource(getattr(SimulationEngine, "network_setup"))
    explanation = (
        "The `network_setup` method initializes the core network, base stations, and the RAN Intelligent Controller (RIC) for the simulation. "
        "It reads configuration data, creates all required network elements, and ensures that the simulation environment is ready for operation. "
        "This method must be called before starting the simulation to ensure all components are properly instantiated and connected."
    )
    return f"```python\n{code}\n```\n\n{explanation}"


@knowledge_explainer(
    "/sim/method/spawn_random_ue",
    tags=[KnowledgeTag.SIMULATION, KnowledgeTag.UE, KnowledgeTag.CODE],
    related=[
        (KnowledgeRelationship.CALL_METHOD, "/net/ue/method/power_up"),
        (KnowledgeRelationship.CALL_METHOD, "/sim/method/add_ue"),
    ],
)
def sim_spawn_random_ue_explainer(sim, knowledge_router, query_key, params):
    code = inspect.getsource(getattr(SimulationEngine, "spawn_random_ue"))
    explanation = (
        "The `spawn_random_ue` method creates a new UE at a random position within the simulation boundaries, assigns it a random target and speed, "
        "and attempts to power it up and register it with the network. If successful, the UE is added to the simulation's UE list. "
        "This method is used to dynamically introduce new UEs into the simulation, supporting scenarios with varying UE density and mobility."
    )
    return f"```python\n{code}\n```\n\n{explanation}"


@knowledge_explainer(
    "/sim/method/add_ue",
    tags=[KnowledgeTag.SIMULATION, KnowledgeTag.UE, KnowledgeTag.CODE],
    related=[
        (KnowledgeRelationship.CALLED_BY_METHOD, "/sim/method/spawn_random_ue"),
        (KnowledgeRelationship.SET_ATTRIBUTE, "/sim/attribute/ue_list"),
    ],
)
def sim_add_ue_explainer(sim, knowledge_router, query_key, params):
    code = inspect.getsource(getattr(SimulationEngine, "add_ue"))
    explanation = (
        "The `add_ue` method adds a UE object to the simulation's UE list and increments the global UE counter. "
        "It ensures that each UE is uniquely identified and tracked throughout its lifecycle in the simulation."
    )
    return f"```python\n{code}\n```\n\n{explanation}"


@knowledge_explainer(
    "/sim/method/spawn_UEs",
    tags=[KnowledgeTag.SIMULATION, KnowledgeTag.UE, KnowledgeTag.CODE],
    related=[
        (KnowledgeRelationship.CALL_METHOD, "/sim/method/spawn_random_ue"),
        (KnowledgeRelationship.CALLED_BY_METHOD, "/sim/method/step"),
    ],
)
def sim_spawn_UEs_explainer(sim, knowledge_router, query_key, params):
    code = inspect.getsource(getattr(SimulationEngine, "spawn_UEs"))
    explanation = (
        "The `spawn_UEs` method determines how many new UEs to introduce in the current simulation step, based on configuration and randomization. "
        "It repeatedly calls `spawn_random_ue` to create and register new UEs, up to the maximum allowed UE count. "
    )
    return f"```python\n{code}\n```\n\n{explanation}"


@knowledge_explainer(
    "/sim/method/step_UEs",
    tags=[KnowledgeTag.SIMULATION, KnowledgeTag.UE, KnowledgeTag.CODE],
    related=[
        (KnowledgeRelationship.CALLED_BY_METHOD, "/net/ue/method/step"),
        (KnowledgeRelationship.USES_ATTRIBUTE, "/sim/attribute/ue_list"),
        (KnowledgeRelationship.CALL_METHOD, "/sim/method/remove_UE"),
    ],
)
def sim_step_UEs_explainer(sim, knowledge_router, query_key, params):
    code = inspect.getsource(getattr(SimulationEngine, "step_UEs"))
    explanation = (
        "The `step_UEs` method advances the state of all UEs in the simulation by one time step. "
        "It calls each UE's `step` method to update its position, connectivity, and state, and removes UEs that are no longer connected. "
    )
    return f"```python\n{code}\n```\n\n{explanation}"


@knowledge_explainer(
    "/sim/method/remove_UE",
    tags=[KnowledgeTag.SIMULATION, KnowledgeTag.UE, KnowledgeTag.CODE],
    related=[
        (KnowledgeRelationship.CALLED_BY_METHOD, "/sim/method/step_UEs"),
        (KnowledgeRelationship.SET_ATTRIBUTE, "/sim/attribute/ue_list"),
    ],
)
def sim_remove_UE_explainer(sim, knowledge_router, query_key, params):
    code = inspect.getsource(getattr(SimulationEngine, "remove_UE"))
    explanation = (
        "The `remove_UE` method removes a specified UE from the simulation's UE list and logs the deregistration event. "
        "It is used to cleanly remove UEs that have completed their session or are no longer active in the simulation."
    )
    return f"```python\n{code}\n```\n\n{explanation}"


@knowledge_explainer(
    "/sim/method/step_BSs",
    tags=[KnowledgeTag.SIMULATION, KnowledgeTag.BS, KnowledgeTag.CODE],
    related=[
        (KnowledgeRelationship.CALLED_BY_METHOD, "/sim/method/step"),
        (KnowledgeRelationship.USES_ATTRIBUTE, "/sim/attribute/base_station_list"),
        (KnowledgeRelationship.CALL_METHOD, "/net/base_station/method/step"),
    ],
)
def sim_step_BSs_explainer(sim, knowledge_router, query_key, params):
    code = inspect.getsource(getattr(SimulationEngine, "step_BSs"))
    explanation = (
        "The `step_BSs` method advances the state of all base stations in the simulation by one time step. "
        "It calls each base station's `step` method, which in turn updates all managed cells and processes control actions. "
    )
    return f"```python\n{code}\n```\n\n{explanation}"


@knowledge_explainer(
    "/sim/method/step",
    tags=[KnowledgeTag.SIMULATION, KnowledgeTag.CODE],
    related=[
        (KnowledgeRelationship.CALLED_BY_METHOD, "/sim/method/start_simulation"),
        (KnowledgeRelationship.CALL_METHOD, "/sim/method/spawn_UEs"),
        (KnowledgeRelationship.CALL_METHOD, "/sim/method/step_UEs"),
        (KnowledgeRelationship.CALL_METHOD, "/sim/method/step_BSs"),
    ],
)
def sim_step_explainer(sim, knowledge_router, query_key, params):
    code = inspect.getsource(getattr(SimulationEngine, "step"))
    explanation = (
        "The `step` method orchestrates a single simulation time step. "
        "It performs the following actions in sequence: spawns new UEs if needed, updates all UEs, and advances all base stations. "
        "This method is called repeatedly during the simulation loop and is responsible for driving the overall progression of the simulation."
    )
    return f"```python\n{code}\n```\n\n{explanation}"


@knowledge_explainer(
    "/sim/method/start_simulation",
    tags=[KnowledgeTag.SIMULATION, KnowledgeTag.CODE],
    related=[
        (KnowledgeRelationship.CALL_METHOD, "/sim/method/step"),
        (KnowledgeRelationship.SET_ATTRIBUTE, "/sim/attribute/sim_started"),
    ],
)
def sim_start_simulation_explainer(sim, knowledge_router, query_key, params):
    code = inspect.getsource(getattr(SimulationEngine, "start_simulation"))
    explanation = (
        "The `start_simulation` method is an asynchronous coroutine that starts the main simulation loop. "
        "It repeatedly calls the `step` method, sends simulation state updates, and advances the simulation time until the maximum number of steps is reached or the simulation is stopped. "
        "This method is the entry point for running the simulation and coordinating all network activities."
    )
    return f"```python\n{code}\n```\n\n{explanation}"


@knowledge_explainer(
    "/sim/method/stop",
    tags=[KnowledgeTag.SIMULATION, KnowledgeTag.CODE],
    related=[
        (KnowledgeRelationship.SET_ATTRIBUTE, "/sim/attribute/sim_started"),
    ],
)
def sim_stop_explainer(sim, knowledge_router, query_key, params):
    code = inspect.getsource(getattr(SimulationEngine, "stop"))
    explanation = "The `stop` method pause the simulation by setting the `sim_started` flag to `False` and logging the stop event. "
    return f"```python\n{code}\n```\n\n{explanation}"
