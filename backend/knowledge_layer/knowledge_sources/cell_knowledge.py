import json
import inspect
from ..knowledge_getter import knowledge_getter
from ..knowledge_explainer import knowledge_explainer
from ..tags import KnowledgeTag
from ..relationships import KnowledgeRelationship

SUPPORTED_CELL_ATTRIBUTES = [
    "cell_id",
    "frequency_band",
    "carrier_frequency_MHz",
    "bandwidth_Hz",
    "max_prb",
    "max_dl_prb",
    "max_ul_prb",
    # "cell_radius",
    "transmit_power_dBm",
    "cell_individual_offset_dBm",
    "frequency_priority",
    "qrx_level_min",
    "prb_ue_allocation_dict",
    "connected_ue_list",
    "allocated_dl_prb",
    "allocated_ul_prb",
    "current_dl_load",
    "current_ul_load",
    "position_x",
    "position_y",
]

SUPPORTED_CELL_METHODS = [
    "register_ue",
    "monitor_ue_signal_strength",
    "select_ue_mcs",
    "allocate_prb",
    "estimate_ue_throughput_and_latency",
    "deregister_ue",
    "step",
    # "to_json",
]


@knowledge_getter(
    key="/net/cell/attribute/{cell_id}/{attribute_name}",
)
def cell_attribute_getter(sim, knowledge_router, query_key, params):
    cell = sim.cell_list.get(params["cell_id"], None)
    if not cell:
        return f"Cell {params['cell_id']} not found."
    attribute_name = params["attribute_name"]

    if attribute_name not in SUPPORTED_CELL_ATTRIBUTES:
        return f"Attribute {attribute_name} not supported. Supported attributes: {', '.join(SUPPORTED_CELL_ATTRIBUTES)}"

    if hasattr(cell, attribute_name):
        attribute = getattr(cell, attribute_name)
        if callable(attribute):
            return f"{attribute_name} is a method, query it via /net/cell/method/{attribute_name} instead."
        if isinstance(attribute, dict) or isinstance(attribute, list):
            return json.dumps(attribute)
        return str(attribute)
    else:
        return f"Attribute {attribute_name} not found in Cell class. Supported attributes: {', '.join(SUPPORTED_CELL_ATTRIBUTES)}"


@knowledge_getter(
    key="/net/cell/method/{method_name}",
)
def cell_method_getter(sim, knowledge_router, query_key, params):
    method_name = params["method_name"]
    if len(sim.cell_list.keys()) == 0:
        return f"No cells are available. Please start the simulation and try again."
    cell = list(sim.cell_list.values())[0]
    if hasattr(cell, method_name):
        method = getattr(cell, method_name)
        if callable(method):
            return inspect.getsource(method)
        else:
            return f"{method_name} is not a method."
    return f"Method {method_name} not found in Cell class. Supported methods: {', '.join(SUPPORTED_CELL_METHODS)}"


@knowledge_explainer(
    key="/net/cell",
    tags=[KnowledgeTag.CELL, KnowledgeTag.KNOWLEDGE_GUIDE],
    related=[],
)
def cell_knowledge_explainer(sim, knowledge_router, query_key, params):
    return f"""Welcome to the Cell knowledge base!
This knowledge base provides access to the knowledge of all the cells in the simulation.
You can retrieve information about Cell attributes and methods using the following query keys:
* `/net/cell/attribute/{{cell_id}}/{{attribute_name}}`: Retrieve a specific attribute of a Cell.
* `/net/cell/method/{{method_name}}`: Access a specific method of the Cell class.
For example, you can query `/net/cell/attribute/{{cell_id}}/bandwidth_Hz` to get the bandwidth of a cell,
or `/net/cell/method/allocate_prb` to get the source code or explanation of the `allocate_prb` method.

Supported attributes include:
{", ".join(SUPPORTED_CELL_ATTRIBUTES)}

Supported methods include:
{", ".join(SUPPORTED_CELL_METHODS)}
"""


@knowledge_explainer(
    "/net/cell/attribute/{cell_id}/cell_id",
    tags=[KnowledgeTag.CELL, KnowledgeTag.ID],
    related=[],
)
def cell_id_explainer(sim, knowledge_router, query_key, params):
    cell = sim.cell_list.get(params["cell_id"], None)
    if not cell:
        return f"Cell {params['cell_id']} not found."
    return f"The cell's unique identifier is {cell.cell_id}."


@knowledge_explainer(
    "/net/cell/attribute/{cell_id}/frequency_band",
    tags=[KnowledgeTag.CELL],
    related=[],
)
def cell_frequency_band_explainer(sim, knowledge_router, query_key, params):
    cell = sim.cell_list.get(params["cell_id"], None)
    if not cell:
        return f"Cell {params['cell_id']} not found."
    return (
        f"The `frequency_band` attribute specifies the frequency band (e.g., n78 or n258) in which the cell operates. "
        f"This determines the radio spectrum allocated to the cell, affecting propagation characteristics, coverage, and capacity. "
        f"The current value is: {cell.frequency_band}."
    )


@knowledge_explainer(
    "/net/cell/attribute/{cell_id}/max_dl_prb",
    tags=[KnowledgeTag.CELL, KnowledgeTag.QoS],
    related=[
        (KnowledgeRelationship.CONSTRAINED_BY, "/net/cell/attribute/{cell_id}/max_prb"),
        (KnowledgeRelationship.USED_BY_METHOD, "/net/cell/method/allocate_prb"),
    ],
)
def cell_max_dl_prb_explainer(sim, knowledge_router, query_key, params):
    cell = sim.cell_list.get(params["cell_id"], None)
    if not cell:
        return f"Cell {params['cell_id']} not found."
    return (
        f"The `max_dl_prb` attribute defines the maximum number of Physical Resource Blocks (PRBs) available for downlink (DL) transmission in this cell. "
        f"PRBs are the smallest unit of radio resource allocation in the system. "
        f"Downlink PRBs are allocated to UEs for data transmission from the cell to the UE. "
        f"Current value: {cell.max_dl_prb}."
    )


@knowledge_explainer(
    "/net/cell/attribute/{cell_id}/max_ul_prb",
    tags=[KnowledgeTag.CELL, KnowledgeTag.QoS],
    related=[
        (KnowledgeRelationship.CONSTRAINED_BY, "/net/cell/attribute/{cell_id}/max_prb"),
    ],
)
def cell_max_ul_prb_explainer(sim, knowledge_router, query_key, params):
    cell = sim.cell_list.get(params["cell_id"], None)
    if not cell:
        return f"Cell {params['cell_id']} not found."
    return (
        f"The `max_ul_prb` attribute specifies the maximum number of Physical Resource Blocks (PRBs) available for uplink (UL) transmission in this cell. "
        f"Uplink PRBs are used for data sent from the UE to the cell. "
        f"Current value: {cell.max_ul_prb}."
    )


@knowledge_explainer(
    "/net/cell/attribute/{cell_id}/transmit_power_dBm",
    tags=[KnowledgeTag.CELL, KnowledgeTag.QoS],
    related=[
        (KnowledgeRelationship.USED_BY_METHOD, "/net/ue/method/monitor_signal_strength")
    ],
)
def cell_transmit_power_explainer(sim, knowledge_router, query_key, params):
    cell = sim.cell_list.get(params["cell_id"], None)
    if not cell:
        return f"Cell {params['cell_id']} not found."
    return (
        f"The `transmit_power_dBm` attribute specifies the maximum transmit power of the cell in decibel-milliwatts (dBm). "
        f"This value affects the received signal strength at UEs. "
        f"Higher transmit power can improve coverage but may increase interference to neighboring cells. "
        f"Current value: {cell.transmit_power_dBm} dBm."
    )


@knowledge_explainer(
    "/net/cell/attribute/{cell_id}/cell_individual_offset_dBm",
    tags=[KnowledgeTag.CELL, KnowledgeTag.QoS],
    related=[
        (KnowledgeRelationship.USED_BY_METHOD, "/net/ue/method/monitor_signal_strength")
    ],
)
def cell_individual_offset_explainer(sim, knowledge_router, query_key, params):
    cell = sim.cell_list.get(params["cell_id"], None)
    if not cell:
        return f"Cell {params['cell_id']} not found."
    return (
        f"The `cell_individual_offset_dBm` attribute is a cell-specific offset (in dB) applied to signal measurements for handover and cell selection decisions. "
        f"This allows network operators to bias UE association towards or away from specific cells, supporting load balancing and coverage optimization. "
        f"Current value: {cell.cell_individual_offset_dBm} dB."
    )


@knowledge_explainer(
    "/net/cell/attribute/{cell_id}/frequency_priority",
    tags=[KnowledgeTag.CELL],
    related=[
        (
            KnowledgeRelationship.USED_BY_METHOD,
            "/net/ue/method/cell_selection_and_camping",
        )
    ],
)
def cell_frequency_priority_explainer(sim, knowledge_router, query_key, params):
    cell = sim.cell_list.get(params["cell_id"], None)
    if not cell:
        return f"Cell {params['cell_id']} not found."
    return (
        f"The `frequency_priority` attribute indicates the relative priority of this cell's frequency band for UE selection and reselection. "
        f"Higher values may cause UEs to prefer this cell when multiple candidates are available. "
        f"Current value: {cell.frequency_priority}."
    )


@knowledge_explainer(
    "/net/cell/attribute/{cell_id}/qrx_level_min",
    tags=[KnowledgeTag.CELL, KnowledgeTag.QoS],
    related=[
        (
            KnowledgeRelationship.USED_BY_METHOD,
            "/net/ue/method/monitor_signal_strength",
        )
    ],
)
def cell_qrx_level_min_explainer(sim, knowledge_router, query_key, params):
    cell = sim.cell_list.get(params["cell_id"], None)
    if not cell:
        return f"Cell {params['cell_id']} not found."
    return (
        f"The `qrx_level_min` attribute defines the minimum required received signal level (in dBm) for a UE to camp on or connect to this cell. "
        f"This threshold helps ensure that UEs only associate with cells where adequate signal quality is available. "
        f"Current value: {cell.qrx_level_min} dBm."
    )


@knowledge_explainer(
    "/net/cell/attribute/{cell_id}/prb_ue_allocation_dict",
    tags=[KnowledgeTag.CELL, KnowledgeTag.QoS],
    related=[
        (KnowledgeRelationship.SET_BY_METHOD, "/net/cell/method/allocate_prb"),
        (
            KnowledgeRelationship.USED_BY_METHOD,
            "/net/cell/method/estimate_ue_throughput_and_latency",
        ),
    ],
)
def cell_prb_ue_allocation_dict_explainer(sim, knowledge_router, query_key, params):
    cell = sim.cell_list.get(params["cell_id"], None)
    if not cell:
        return f"Cell {params['cell_id']} not found."
    return (
        f"The `prb_ue_allocation_dict` attribute is a dictionary mapping each connected UE's IMSI to its allocated number of downlink and uplink PRBs. "
        f"Example: {{'IMSI_1': {{'downlink': 10, 'uplink': 5}}, ...}}. "
        f"This structure is updated each scheduling cycle by the `allocate_prb` method and reflects the current radio resource allocation for all UEs in the cell."
    )


@knowledge_explainer(
    "/net/cell/attribute/{cell_id}/allocated_dl_prb",
    tags=[KnowledgeTag.CELL, KnowledgeTag.QoS],
    related=[
        (
            KnowledgeRelationship.DERIVED_FROM,
            "/net/cell/attribute/{cell_id}/prb_ue_allocation_dict",
        ),
    ],
)
def cell_allocated_dl_prb_explainer(sim, knowledge_router, query_key, params):
    cell = sim.cell_list.get(params["cell_id"], None)
    if not cell:
        return f"Cell {params['cell_id']} not found."
    return (
        f"The `allocated_dl_prb` attribute represents the total number of downlink PRBs currently allocated to all UEs in the cell. "
        f"It is computed as the sum of the 'downlink' PRB allocations for each UE in `prb_ue_allocation_dict`. "
        f"This value provides a snapshot of downlink resource usage in the cell."
    )


@knowledge_explainer(
    "/net/cell/attribute/{cell_id}/allocated_ul_prb",
    tags=[KnowledgeTag.CELL, KnowledgeTag.QoS],
    related=[
        (
            KnowledgeRelationship.DERIVED_FROM,
            "/net/cell/attribute/{cell_id}/prb_ue_allocation_dict",
        ),
    ],
)
def cell_allocated_ul_prb_explainer(sim, knowledge_router, query_key, params):
    cell = sim.cell_list.get(params["cell_id"], None)
    if not cell:
        return f"Cell {params['cell_id']} not found."
    return (
        f"The `allocated_ul_prb` attribute represents the total number of uplink PRBs currently allocated to all UEs in the cell. "
        f"It is computed as the sum of the 'uplink' PRB allocations for each UE in `prb_ue_allocation_dict`. "
        f"This value provides a snapshot of uplink resource usage in the cell."
    )


@knowledge_explainer(
    "/net/cell/attribute/{cell_id}/current_dl_load",
    tags=[KnowledgeTag.CELL, KnowledgeTag.QoS],
    related=[
        (
            KnowledgeRelationship.DERIVED_FROM,
            "/net/cell/attribute/{cell_id}/allocated_dl_prb",
        ),
        (
            KnowledgeRelationship.DERIVED_FROM,
            "/net/cell/attribute/{cell_id}/max_dl_prb",
        ),
    ],
)
def cell_current_dl_load_explainer(sim, knowledge_router, query_key, params):
    cell = sim.cell_list.get(params["cell_id"], None)
    if not cell:
        return f"Cell {params['cell_id']} not found."
    return (
        f"The `current_dl_load` attribute indicates the current downlink load of the cell, expressed as the ratio of allocated downlink PRBs to the maximum available downlink PRBs. "
        f"Formula: allocated_dl_prb / max_dl_prb. "
        f"This metric reflects how much of the cell's downlink capacity is currently in use."
    )


@knowledge_explainer(
    "/net/cell/attribute/{cell_id}/current_ul_load",
    tags=[KnowledgeTag.CELL, KnowledgeTag.QoS],
    related=[
        (
            KnowledgeRelationship.DERIVED_FROM,
            "/net/cell/attribute/{cell_id}/allocated_ul_prb",
        ),
        (
            KnowledgeRelationship.DERIVED_FROM,
            "/net/cell/attribute/{cell_id}/max_ul_prb",
        ),
    ],
)
def cell_current_ul_load_explainer(sim, knowledge_router, query_key, params):
    cell = sim.cell_list.get(params["cell_id"], None)
    if not cell:
        return f"Cell {params['cell_id']} not found."
    return (
        f"The `current_ul_load` attribute indicates the current uplink load of the cell, expressed as the ratio of allocated uplink PRBs to the maximum available uplink PRBs. "
        f"Formula: allocated_ul_prb / max_ul_prb. "
        f"This metric reflects how much of the cell's uplink capacity is currently in use."
    )


@knowledge_explainer(
    "/net/cell/attribute/{cell_id}/position_x",
    tags=[KnowledgeTag.CELL, KnowledgeTag.LOCATION],
    related=[
        (
            KnowledgeRelationship.USED_BY_METHOD,
            "/net/cell/method/monitor_ue_signal_strength",
        ),
        (
            KnowledgeRelationship.USED_BY_METHOD,
            "/net/ue/method/monitor_signal_strength",
        ),
    ],
)
def cell_position_x_explainer(sim, knowledge_router, query_key, params):
    cell = sim.cell_list.get(params["cell_id"], None)
    if not cell:
        return f"Cell {params['cell_id']} not found."
    return (
        f"The `position_x` attribute gives the X-coordinate of the cell's location in the simulation environment. "
        f"This value is inherited from the base station's position and is used for distance calculations, signal strength estimation, and visualization."
    )


@knowledge_explainer(
    "/net/cell/attribute/{cell_id}/position_y",
    tags=[KnowledgeTag.CELL, KnowledgeTag.LOCATION],
    related=[
        (
            KnowledgeRelationship.USED_BY_METHOD,
            "/net/cell/method/monitor_ue_signal_strength",
        ),
        (
            KnowledgeRelationship.USED_BY_METHOD,
            "/net/ue/method/monitor_signal_strength",
        ),
    ],
)
def cell_position_y_explainer(sim, knowledge_router, query_key, params):
    cell = sim.cell_list.get(params["cell_id"], None)
    if not cell:
        return f"Cell {params['cell_id']} not found."
    return (
        f"The `position_y` attribute gives the Y-coordinate of the cell's location in the simulation environment. "
        f"This value is inherited from the base station's position and is used for distance calculations, signal strength estimation, and visualization."
    )


@knowledge_explainer(
    "/net/cell/attribute/{cell_id}/carrier_frequency_MHz",
    tags=[KnowledgeTag.CELL],
    related=[],
)
def cell_carrier_frequency_explainer(sim, knowledge_router, query_key, params):
    cell = sim.cell_list.get(params["cell_id"], None)
    if not cell:
        return f"Cell {params['cell_id']} not found."
    return (
        f"The cell operates at a carrier frequency of {cell.carrier_frequency_MHz} MHz."
    )


@knowledge_explainer(
    "/net/cell/attribute/{cell_id}/bandwidth_Hz",
    tags=[KnowledgeTag.CELL],
    related=[],
)
def cell_bandwidth_explainer(sim, knowledge_router, query_key, params):
    cell = sim.cell_list.get(params["cell_id"], None)
    if not cell:
        return f"Cell {params['cell_id']} not found."
    return f"The cell's bandwidth is {cell.bandwidth_Hz} Hz."


@knowledge_explainer(
    "/net/cell/attribute/{cell_id}/max_prb",
    tags=[KnowledgeTag.CELL],
    related=[],
)
def cell_max_prb_explainer(sim, knowledge_router, query_key, params):
    cell = sim.cell_list.get(params["cell_id"], None)
    if not cell:
        return f"Cell {params['cell_id']} not found."
    return f"The cell supports a maximum of {cell.max_prb} Physical Resource Blocks (PRBs). The PRBs are divided into downlink PRBs and uplink PRBs."


@knowledge_explainer(
    "/net/cell/attribute/{cell_id}/connected_ue_list",
    tags=[KnowledgeTag.CELL, KnowledgeTag.UE],
    related=[],
)
def cell_connected_ue_list_explainer(sim, knowledge_router, query_key, params):
    cell = sim.cell_list.get(params["cell_id"], None)
    if not cell:
        return f"Cell {params['cell_id']} not found."
    return f"The cell currently serving the following UEs: {list(cell.connected_ue_list.keys())}"


@knowledge_explainer(
    "/net/cell/method/register_ue",
    tags=[KnowledgeTag.CELL, KnowledgeTag.CODE],
    related=[
        (
            KnowledgeRelationship.SET_ATTRIBUTE,
            "/net/cell/attribute/{cell_id}/connected_ue_list",
        ),
        (
            KnowledgeRelationship.CALLED_BY_METHOD,
            "/net/base_station/method/handle_ue_authentication_and_registration",
        ),
    ],
)
def cell_register_ue_explainer(sim, knowledge_router, query_key, params):
    return "The `register_ue` method adds a UE to the cell's list of connected UEs and initializes its PRB allocation (downlink: 0, uplink: 0)."


@knowledge_explainer(
    "/net/cell/method/allocate_prb",
    tags=[KnowledgeTag.CELL, KnowledgeTag.QoS, KnowledgeTag.CODE],
    related=[
        (
            KnowledgeRelationship.SET_ATTRIBUTE,
            "/net/cell/attribute/{cell_id}/prb_ue_allocation_dict",
        ),
        (
            KnowledgeRelationship.CALLED_BY_METHOD,
            "/net/cell/method/step",
        ),
    ],
)
def cell_allocate_prb_explainer(sim, knowledge_router, query_key, params):
    return (
        "The `allocate_prb` method in the Cell class performs QoS-aware Proportional Fair Scheduling (PFS) to allocate Physical Resource Blocks (PRBs) among all connected UEs. "
        "The allocation process is as follows:\n\n"
        "1. **Reset PRB Allocation:** All UEs' downlink and uplink PRB allocations are reset to zero at the start of each allocation cycle.\n\n"
        "2. **Calculate PRB Requirements:** For each connected UE, the method calculates the number of downlink PRBs required to meet its Guaranteed Bit Rate (GBR) using the UE's QoS profile and current downlink MCS (modulation and coding scheme). "
        "The required PRBs are computed by dividing the UE's GBR_DL by the estimated throughput per PRB (which depends on the modulation order and code rate from the MCS).\n\n"
        "3. **Total PRB Demand:** The method sums the required PRBs for all UEs to determine the total downlink PRB demand.\n\n"
        "4. **PRB Allocation:**\n"
        "   - If the total PRB demand is less than or equal to the cell's maximum available downlink PRBs, each UE is allocated the exact number of PRBs it requires.\n"
        "   - If the total demand exceeds the available PRBs, the method first allocates at least one PRB to each UE to ensure minimum service. "
        "The remaining PRBs are then distributed proportionally based on each UE's required share of the total demand.\n\n"
        "This approach ensures that UEs with higher QoS requirements or better channel conditions receive more resources, while still providing a minimum allocation to all UEs. "
        "The final allocation is stored in the `prb_ue_allocation_dict` attribute, which maps each UE's IMSI to its downlink and uplink PRB allocation."
    )


@knowledge_explainer(
    "/net/cell/method/monitor_ue_signal_strength",
    tags=[KnowledgeTag.CELL, KnowledgeTag.CODE, KnowledgeTag.SIMULATION],
    related=[
        (
            KnowledgeRelationship.SET_ATTRIBUTE,
            "/net/cell/attribute/{cell_id}/ue_uplink_signal_strength_dict",
        ),
        (
            KnowledgeRelationship.CALLED_BY_METHOD,
            "/net/cell/method/step",
        ),
    ],
)
def cell_monitor_ue_signal_strength_explainer(sim, knowledge_router, query_key, params):
    return (
        "The `monitor_ue_signal_strength` method in the Cell class measures and updates the uplink signal strength for each connected UE. "
        "This is a key step in simulating realistic radio conditions and is typically called at every simulation time step.\n\n"
        "The process works as follows:\n"
        "1. The method initializes or clears the cell's `ue_uplink_signal_strength_dict`, which will store the measured uplink signal strength (in dBm) for each UE.\n"
        "2. For each connected UE, it calculates the distance between the cell and the UE using their current positions (`position_x`, `position_y`).\n"
        "3. It retrieves the UE's uplink transmit power (in dBm).\n"
        "4. The method applies a path loss model (as configured in the simulation settings, e.g., Urban Macro NLOS) to estimate the signal attenuation over the distance and frequency.\n"
        "5. The received uplink power at the cell is computed as the UE's transmit power minus the path loss.\n"
        "6. The result is stored in `ue_uplink_signal_strength_dict` under the UE's IMSI.\n\n"
    )


@knowledge_explainer(
    "/net/cell/method/select_ue_mcs",
    tags=[KnowledgeTag.CELL, KnowledgeTag.QoS, KnowledgeTag.CODE],
    related=[
        (
            KnowledgeRelationship.CALL_METHOD,
            "/net/ue/method/set_downlink_mcs_index",
        ),
        (
            KnowledgeRelationship.CALL_METHOD,
            "/net/ue/method/set_downlink_mcs_data",
        ),
        (
            KnowledgeRelationship.CALLED_BY_METHOD,
            "/net/cell/method/step",
        ),
    ],
)
def cell_select_ue_mcs_explainer(sim, knowledge_router, query_key, params):
    return (
        "The `select_ue_mcs` method in the Cell class determines and assigns the most suitable Modulation and Coding Scheme (MCS) for each connected UE based on its current Channel Quality Indicator (CQI).\n\n"
        "The process works as follows:\n"
        "1. For each connected UE, the method resets the UE's `downlink_mcs_index` to -1 and `downlink_mcs_data` to None.\n"
        "2. It retrieves the spectral efficiency for the UE's current CQI from the `UE_CQI_MCS_SPECTRAL_EFFICIENCY_TABLE`.\n"
        "3. If the CQI is 0 or there is no matching entry, the UE is skipped (no MCS assigned).\n"
        "4. Otherwise, the method iterates through the available MCS indices in `RAN_MCS_SPECTRAL_EFFICIENCY_TABLE` and selects the highest MCS index whose spectral efficiency does not exceed the UE's CQI spectral efficiency.\n"
        "5. The selected MCS index and its associated parameters (such as modulation order, target code rate, and spectral efficiency) are assigned to the UE's `downlink_mcs_index` and `downlink_mcs_data` attributes.\n\n"
        "This method ensures that each UE is assigned the most aggressive MCS it can reliably support, maximizing throughput while maintaining link reliability. "
        "The assigned MCS is then used in subsequent resource allocation and throughput estimation steps."
    )


@knowledge_explainer(
    "/net/cell/method/estimate_ue_throughput_and_latency",
    tags=[KnowledgeTag.CELL, KnowledgeTag.QoS, KnowledgeTag.CODE],
    related=[
        (
            KnowledgeRelationship.SET_BY_METHOD,
            "/net/ue/attribute/{ue_imsi}/downlink_bitrate",
        ),
    ],
)
def cell_estimate_ue_throughput_and_latency_explainer(
    sim, knowledge_router, query_key, params
):
    return (
        "The `estimate_ue_throughput_and_latency` method in the Cell class calculates the downlink (and potentially uplink) throughput and latency for each connected UE, "
        "based on the PRB (Physical Resource Block) allocation and the selected Modulation and Coding Scheme (MCS) for each UE.\n\n"
        "The process works as follows:\n"
        "1. For each connected UE, the method first checks if the UE has valid downlink MCS data. If not, the UE is skipped for this estimation cycle.\n"
        "2. For UEs with valid MCS data, the method retrieves the modulation order and target code rate from the UE's `downlink_mcs_data` attribute.\n"
        "3. It then obtains the number of downlink PRBs allocated to the UE from the cell's `prb_ue_allocation_dict`.\n"
        "4. The method calls the `estimate_throughput` utility function, passing the modulation order, code rate, and number of PRBs, to compute the estimated downlink bitrate for the UE.\n"
        "5. The computed bitrate is set on the UE using the `set_downlink_bitrate` method.\n"
        "6. (TODO in code) The method is also intended to estimate downlink and uplink latency, but this is not yet implemented.\n\n"
        "This method ensures that each UE's throughput reflects both its channel quality (via MCS) and its allocated radio resources (PRBs). "
    )


@knowledge_explainer(
    "/net/cell/method/deregister_ue",
    tags=[KnowledgeTag.CELL, KnowledgeTag.CODE],
    related=[
        (
            KnowledgeRelationship.SET_ATTRIBUTE,
            "/net/cell/attribute/{cell_id}/connected_ue_list",
        ),
    ],
)
def cell_deregister_ue_explainer(sim, knowledge_router, query_key, params):
    return "The `deregister_ue` method removes a UE from the cell's list of connected UEs and releases its allocated PRBs."


@knowledge_explainer(
    "/net/cell/method/step",
    tags=[KnowledgeTag.CELL, KnowledgeTag.SIMULATION, KnowledgeTag.CODE],
    related=[
        (
            KnowledgeRelationship.CALL_METHOD,
            "/net/cell/method/monitor_ue_signal_strength",
        ),
        (
            KnowledgeRelationship.CALL_METHOD,
            "/net/cell/method/select_ue_mcs",
        ),
        (
            KnowledgeRelationship.CALL_METHOD,
            "/net/cell/method/allocate_prb",
        ),
        (
            KnowledgeRelationship.CALL_METHOD,
            "/net/cell/method/estimate_ue_throughput_and_latency",
        ),
    ],
)
def cell_step_explainer(sim, knowledge_router, query_key, params):
    return (
        "The `step` method advances the simulation state of the Cell by one time step. "
        "It orchestrates the main per-timestep operations for the cell and its connected UEs. The method performs the following actions in sequence:\n\n"
        "1. **Monitor UE Signal Strength:** Calls `monitor_ue_signal_strength()` to update the uplink signal strength measurements for all connected UEs. "
        "This uses the current positions of the cell and UEs, their transmit powers, and the configured path loss model.\n\n"
        "2. **Select UE MCS:** Calls `select_ue_mcs()` to determine the most suitable Modulation and Coding Scheme (MCS) for each UE based on its Channel Quality Indicator (CQI). "
        "This sets the UE's `downlink_mcs_index` and `downlink_mcs_data` attributes, which are used for throughput estimation and resource allocation.\n\n"
        "3. **Allocate PRBs:** Calls `allocate_prb()` to perform QoS-aware Proportional Fair Scheduling (PFS) and allocate Physical Resource Blocks (PRBs) among all connected UEs. "
        "The allocation is based on each UE's QoS profile (e.g., Guaranteed Bit Rate) and current channel conditions (MCS).\n\n"
        "4. **Estimate UE Throughput and Latency:** Calls `estimate_ue_throughput_and_latency()` to calculate the downlink bitrate for each UE, "
        "using the allocated PRBs and selected MCS. The computed bitrate is set on the UE. (Note: latency estimation is marked as TODO in the code.)\n\n"
        "By executing these steps in order, the `step` method ensures that the cell's resource allocation, link adaptation, and performance metrics are updated each simulation tick, "
        "reflecting the latest network and radio conditions."
    )
