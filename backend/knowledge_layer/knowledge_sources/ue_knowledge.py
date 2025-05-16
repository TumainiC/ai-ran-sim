import json
from ..knowledge_getter import knowledge_getter
from ..knowledge_explainer import knowledge_explainer
from ..tags import KnowledgeTag
from ..relationships import KnowledgeRelationship
from settings import (
    NETWORK_SLICES,
    NETWORK_SLICE_EMBB_NAME,
    NETWORK_SLICE_URLLC_NAME,
    NETWORK_SLICE_MTC_NAME,
)
import inspect

SUPPORTED_UE_ATTRIBUTES = [
    "ue_imsi",
    "position_x",
    "position_y",
    "target_x",
    "target_y",
    "speed_mps",
    "time_remaining",
    "slice_type",
    "qos_profile",
    "connected",
    "downlink_bitrate",
    "downlink_latency",
    "downlink_sinr",
    "downlink_cqi",
    "downlink_mcs_index",
    "downlink_mcs_data",
    # "uplink_bitrate",
    # "uplink_latency",
    # "uplink_transmit_power_dBm",
    "current_cell",
]

SUPPORTED_UE_METHODS = [
    "power_up",
    "monitor_signal_strength",
    "cell_selection_and_camping",
    "authenticate_and_register",
]


@knowledge_getter(
    key="/net/ue/attribute/{ue_imsi}/{attribute_name}",
)
def ue_attribute_getter(sim, knowledge_router, query_key, params):
    ue = sim.ue_list.get(params["ue_imsi"], None)
    if not ue:
        return f"UE {params['ue_imsi']} not found. Note that ue_imsi is case-sensitive."
    attribute_name = params["attribute_name"]
    if hasattr(ue, attribute_name):
        attribute = getattr(ue, attribute_name)
        # check the attribute is not a function
        if callable(attribute):
            return f"{attribute_name} is a function, query it via /net/ue/{params["ue_imsi"]}/method/{attribute_name} instead."
        if isinstance(attribute, dict):
            return json.dumps(attribute)
        elif isinstance(attribute, list):
            return json.dumps(attribute)
        return str(attribute)
    else:
        # raise ValueError(f"Attribute {attribute_name} not found in UE object.")
        return f"""Attribute {attribute_name} not found in UE class. Supported attributes: {", ".join(SUPPORTED_UE_ATTRIBUTES)}"""


@knowledge_getter(
    key="/net/ue/method/{method_name}",
)
def ue_method_getter(sim, knowledge_router, query_key, params):
    method_name = params["method_name"]
    if len(sim.ue_list.keys()) == 0:
        return f"No UE are available. Please start the simulation and try again."
    ue = list(sim.ue_list.values())[0]
    if hasattr(ue, method_name):
        method = getattr(ue, method_name)
        if callable(method):
            return inspect.getsource(method)
        else:
            return f"{method_name} is not a method. Something is wrong :)"
    return f"""Method {method_name} not found in UE class. Supported methods: {", ".join(SUPPORTED_UE_METHODS)}"""


@knowledge_explainer(
    "/net/ue/attribute/{ue_imsi}/ue_imsi",
    tags=[KnowledgeTag.UE, KnowledgeTag.ID],
    related=[],
)
def ue_imsi_explainer(sim, knowledge_router, query_key, params):
    ue = sim.ue_list.get(params["ue_imsi"], None)
    if not ue:
        return f"UE {params['ue_imsi']} not found. Note that ue_imsi is case-sensitive."
    return f"The UE's unique IMSI string is {ue.ue_imsi}."


@knowledge_explainer(
    "/net/ue/attribute/{ue_imsi}/position_x",
    tags=[KnowledgeTag.UE, KnowledgeTag.LOCATION],
    related=[],
)
def ue_position_x_explainer(sim, knowledge_router, query_key, params):
    ue = sim.ue_list.get(params["ue_imsi"], None)
    if not ue:
        return f"UE {params['ue_imsi']} not found. Note that ue_imsi is case-sensitive."
    return f"The UE's x-coordinate is {ue.position_x} (unit: m)."


@knowledge_explainer(
    "/net/ue/attribute/{ue_imsi}/position_y",
    tags=[KnowledgeTag.UE, KnowledgeTag.LOCATION],
    related=[],
)
def ue_position_y_explainer(sim, knowledge_router, query_key, params):
    ue = sim.ue_list.get(params["ue_imsi"], None)
    if not ue:
        return f"UE {params['ue_imsi']} not found. Note that ue_imsi is case-sensitive."
    return f"The UE's y-coordinate is {ue.position_y} (unit: m)."


@knowledge_explainer(
    "/net/ue/attribute/{ue_imsi}/target_x",
    tags=[KnowledgeTag.UE, KnowledgeTag.MOBILITY],
    related=[],
)
def ue_target_x_explainer(sim, knowledge_router, query_key, params):
    ue = sim.ue_list.get(params["ue_imsi"], None)
    if not ue:
        return f"UE {params['ue_imsi']} not found. Note that ue_imsi is case-sensitive."
    return f"The UE's target x-coordinate is {ue.target_x} (unit: m)."


@knowledge_explainer(
    "/net/ue/attribute/{ue_imsi}/target_y",
    tags=[KnowledgeTag.UE, KnowledgeTag.MOBILITY],
    related=[],
)
def ue_target_y_explainer(sim, knowledge_router, query_key, params):
    ue = sim.ue_list.get(params["ue_imsi"], None)
    if not ue:
        return f"UE {params['ue_imsi']} not found. Note that ue_imsi is case-sensitive."
    return f"The UE's target y-coordinate is {ue.target_y} (unit: m)."


@knowledge_explainer(
    "/net/ue/attribute/{ue_imsi}/speed_mps",
    tags=[KnowledgeTag.UE, KnowledgeTag.MOBILITY],
    related=[],
)
def ue_speed_mps_explainer(sim, knowledge_router, query_key, params):
    ue = sim.ue_list.get(params["ue_imsi"], None)
    if not ue:
        return f"UE {params['ue_imsi']} not found. Note that ue_imsi is case-sensitive."
    return f"The UE's speed is {ue.speed_mps} (unit: m/s)."


@knowledge_explainer(
    "/net/ue/attribute/{ue_imsi}/time_remaining",
    tags=[KnowledgeTag.UE, KnowledgeTag.SIMULATION],
    related=[],
)
def ue_time_remaining_explainer(sim, knowledge_router, query_key, params):
    ue = sim.ue_list.get(params["ue_imsi"], None)
    if not ue:
        return f"UE {params['ue_imsi']} not found. Note that ue_imsi is case-sensitive."
    return f"The UE has {ue.time_remaining} (unit: simulation step) time left. When it becomes 0, the UE will be deregister itself from the network and removed from simulation."


@knowledge_explainer(
    "/net/ue/attribute/{ue_imsi}/slice_type",
    tags=[KnowledgeTag.UE, KnowledgeTag.SIMULATION],
    related=[
        (KnowledgeRelationship.AFFECTS, "/net/ue/attribute/{ue_imsi}/qos_profile")
    ],
)
def ue_slice_type_explainer(sim, knowledge_router, query_key, params):
    ue = sim.ue_list.get(params["ue_imsi"], None)
    if not ue:
        return f"UE {params['ue_imsi']} not found. Note that ue_imsi is case-sensitive."
    slice_type = getattr(ue, "slice_type", None)
    if not slice_type:
        return f"UE {params['ue_imsi']} does not have a slice type defined yet. Note that slice type is assigned during the authentication and registration process."
    slice_qos_profile = NETWORK_SLICES.get(slice_type)
    if slice_type == NETWORK_SLICE_EMBB_NAME:
        slice_type_explanation = "eMBB (Enhanced Mobile Broadband) slice is designed to provide high data rates and capacity for applications like video streaming."
    elif slice_type == NETWORK_SLICE_URLLC_NAME:
        slice_type_explanation = "URLLC (Ultra-Reliable Low Latency Communication) slice is designed for applications requiring ultra-reliable and low-latency communication, such as autonomous driving."
    elif slice_type == NETWORK_SLICE_MTC_NAME:
        slice_type_explanation = "mMTC (Massive Machine Type Communication) slice is designed for applications with a large number of low-power devices, such as IoT sensors."
    else:
        slice_type_explanation = "Unknown slice type."

    return f"The UE's (randomly selected) slice is {ue.slice_type}. {slice_type_explanation} The corresponding QoS profile of this slice type is {json.dumps(slice_qos_profile)} (query /net/ue/attribute/{params['ue_imsi']}/qos_profile for more details)."


@knowledge_explainer(
    "/net/ue/attribute/{ue_imsi}/qos_profile",
    tags=[KnowledgeTag.UE, KnowledgeTag.SIMULATION],
    related=[
        (KnowledgeRelationship.DEPENDS_ON, "/net/ue/attribute/{ue_imsi}/slice_type")
    ],
)
def ue_qos_profile_explainer(sim, knowledge_router, query_key, params):
    ue = sim.ue_list.get(params["ue_imsi"], None)
    if not ue:
        return f"UE {params['ue_imsi']} not found. Note that ue_imsi is case-sensitive."
    slice_type = getattr(ue, "slice_type", None)
    if not slice_type:
        return f"UE {params['ue_imsi']} does not have a slice type defined yet. Cannot proceed with slice QoS Profile explanation. Note that slice type is assigned during the authentication and registration process."
    slice_qos_profile = NETWORK_SLICES.get(slice_type)

    v_5qi = f"5QI: {slice_qos_profile.get("5QI")}"
    v_gbr_dl = f"GBR_DL: {slice_qos_profile.get("GBR_DL")}"
    v_gbr_ul = f"GBR_UL: {slice_qos_profile.get("GBR_UL")}"
    v_latency_dl = f"latency_dl: {slice_qos_profile.get("latency_dl")}"
    v_latency_ul = f"latency_ul: {slice_qos_profile.get("latency_ul")}"

    attr_expanations = """
    * 5QI is a numerical identifier (e.g., 1, 9, 66, etc.) that maps to a specific QoS profile — a predefined set of parameters that define how the network should treat a particular type of traffic. It simplifies QoS management by bundling parameters under a single value.
    * GBR_DL (Guaranteed Bit Rate Downlink) is the minimum guaranteed data rate for downlink traffic. It ensures that the user equipment (UE) receives a certain amount of bandwidth for its downlink communication. 
    * GBR_UL (Guaranteed Bit Rate Uplink) is the minimum guaranteed data rate for uplink traffic. It ensures that the UE can send a certain amount of data to the network without being throttled.
    * latency_ul (Uplink Latency) is the maximum time it takes for a packet to travel from the UE to the network. 
    * latency_dl (Downlink Latency) is the maximum time it takes for a packet to travel from the network to the UE. 

    Note that the actual bitrate (queried via /net/ue/attribute/{ue_imsi}/downlink_bitrate, /net/ue/attribute/{ue_imsi}/uplink_bitrate) and latency (queried via /net/ue/attribute/{ue_imsi}/uplink_latency, /net/ue/attribute/{ue_imsi}/downlink_latency) may vary based on network conditions and other factors.
    The values provided in the QoS profile are guarantees that the network aims to meet, but they are not absolute limits.
"""
    return f"The UE's QoS profile: {v_5qi}, {v_gbr_dl}, {v_gbr_ul}, {v_latency_dl}, {v_latency_ul}. {attr_expanations}"


@knowledge_explainer(
    "/net/ue/attribute/{ue_imsi}/connected",
    tags=[KnowledgeTag.UE, KnowledgeTag.SIMULATION],
    related=[],
)
def ue_connected_explainer(sim, knowledge_router, query_key, params):
    ue = sim.ue_list.get(params["ue_imsi"], None)
    if not ue:
        return f"UE {params['ue_imsi']} not found. Note that ue_imsi is case-sensitive."
    return f"The UE is {'connected' if ue.connected else 'not connected'} to the network (served by a cell and registered with the core)."


@knowledge_explainer(
    "/net/ue/attribute/{ue_imsi}/downlink_bitrate",
    tags=[KnowledgeTag.UE, KnowledgeTag.QoS],
    related=[
        (
            KnowledgeRelationship.CONSTRAINED_BY,
            "/net/ue/attribute/{ue_imsi}/qos_profile",
        ),
        (
            KnowledgeRelationship.DEPENDS_ON,
            "/net/ue/attribute/{ue_imsi}/downlink_mcs_index",
        ),
    ],
)
def ue_downlink_bitrate_explainer(sim, knowledge_router, query_key, params):
    ue = sim.ue_list.get(params["ue_imsi"], None)
    qos_profile = ue.qos_profile
    gbr_dl = qos_profile.get("GBR_DL")
    if not ue:
        return f"UE {params["ue_imsi"]} not found."
    explanation_text = (
        f"The UE's actual downlink bitrate is {ue.downlink_bitrate} (unit: bps)"
    )
    if ue.downlink_bitrate >= gbr_dl:
        explanation_text += f", which satisfies the guaranteed bitrate ({gbr_dl} bps) defined in the QoS profile."
    else:
        explanation_text += f", which does not satisfy the guaranteed bitrate ({gbr_dl} bps) defined in the QoS profile."
    return explanation_text


@knowledge_explainer(
    "/net/ue/attribute/{ue_imsi}/downlink_latency",
    tags=[KnowledgeTag.UE, KnowledgeTag.QoS],
    related=[
        (
            KnowledgeRelationship.CONSTRAINED_BY,
            "/net/ue/attribute/{ue_imsi}/qos_profile",
        ),
    ],
)
def ue_downlink_latency_explainer(sim, knowledge_router, query_key, params):
    ue = sim.ue_list.get(params["ue_imsi"], None)
    qos_profile = ue.qos_profile
    if not ue:
        return f"UE {params["ue_imsi"]} not found."
    explanation_text = (
        f"The UE's actual downlink latency is {ue.downlink_latency} (unit: ms)."
    )

    if ue.downlink_latency <= qos_profile.get("latency_dl"):
        explanation_text += f", which satisfies the guaranteed latency ({qos_profile.get("latency_dl")} ms) defined in the QoS profile."
    else:
        explanation_text += f", which does not satisfy the guaranteed latency ({qos_profile.get("latency_dl")} ms) defined in the QoS profile."
    return explanation_text


# skip ue/attribute/rrc_measurement_event_monitors
# skip ue/attribute/downlink_received_power_dBm_dict


# "/net/ue/attribute/{ue_imsi}/downlink_sinr",
@knowledge_explainer(
    "/net/ue/attribute/{ue_imsi}/downlink_sinr",
    tags=[KnowledgeTag.UE, KnowledgeTag.QoS],
    related=[
        (
            KnowledgeRelationship.DEPENDS_ON,
            "/net/ue/attribute/{ue_imsi}/downlink_received_power_dBm_dict",
        ),
        (
            KnowledgeRelationship.DEPENDS_ON,
            "/net/cell/{cell_id}/attribute/transmit_power_dBm",
        ),
        (
            KnowledgeRelationship.AFFECTS,
            "/net/ue/attribute/{ue_imsi}/downlink_cqi",
        ),
        (
            KnowledgeRelationship.DETERMINED_IN_METHOD,
            "/net/ue/method/calculate_SINR_and_CQI",
        ),
    ],
)
def ue_downlink_sinr_explainer(sim, knowledge_router, query_key, params):
    ue = sim.ue_list.get(params["ue_imsi"], None)
    if not ue:
        return f"UE {params['ue_imsi']} not found. Note that ue_imsi is case-sensitive."

    if ue.current_cell is None:
        return "The UE is not connected to any cell, so SINR cannot be calculated."

    explanation_text = f"The UE's downlink SINR (Signal-to-Interference-plus-Noise Ratio) is {ue.downlink_sinr:.2f} dB. "

    # Explain SINR calculation
    explanation_text += (
        "SINR is calculated as the ratio of the received power from the serving cell "
        "to the sum of interference power from other cells operating on the same frequency "
        "and thermal noise power. (query /net/ue/method/calculate_SINR_and_CQI for more details)"
    )

    # Add details about interference and noise
    explanation_text += (
        "Interference power is the total received power from other cells on the same frequency, "
        "while thermal noise power is determined by the Boltzmann constant, the UE's temperature, "
        "and the bandwidth of the serving cell."
    )

    # Add SINR value range interpretation
    if ue.downlink_sinr > 20:
        explanation_text += (
            "This SINR value is considered **very good**, indicating excellent signal quality. "
            "The UE is likely to experience high data rates and reliable communication."
        )
    elif 13 <= ue.downlink_sinr <= 20:
        explanation_text += (
            "This SINR value is considered **good**, indicating decent signal quality. "
            "The UE should experience stable communication with moderate to high data rates."
        )
    elif 0 <= ue.downlink_sinr < 13:
        explanation_text += (
            "This SINR value is considered **acceptable**, indicating average signal quality. "
            "The UE may experience moderate data rates, but performance could degrade in challenging conditions."
        )
    elif -10 <= ue.downlink_sinr < 0:
        explanation_text += (
            "This SINR value is considered **bad**, indicating poor signal quality. "
            "The UE is likely to experience low data rates and unreliable communication."
        )
    else:
        explanation_text += (
            "This SINR value is considered **very bad**, indicating extremely poor signal quality. "
            "The UE may struggle to maintain a connection or experience significant performance issues."
        )

    return explanation_text


@knowledge_explainer(
    "/net/ue/attribute/{ue_imsi}/downlink_cqi",
    tags=[KnowledgeTag.UE, KnowledgeTag.QoS],
    related=[
        (
            KnowledgeRelationship.DERIVED_FROM,
            "/net/ue/attribute/{ue_imsi}/downlink_sinr",
        ),
        (
            KnowledgeRelationship.AFFECTS,
            "/net/ue/attribute/{ue_imsi}/mcs_index",
        ),
        (
            KnowledgeRelationship.DETERMINED_IN_METHOD,
            "/net/ue/method/calculate_SINR_and_CQI",
        ),
    ],
)
def ue_downlink_cqi_explainer(sim, knowledge_router, query_key, params):
    ue = sim.ue_list.get(params["ue_imsi"], None)
    if not ue:
        return f"UE {params['ue_imsi']} not found. Note that ue_imsi is case-sensitive."

    explanation_text = (
        f"The UE's downlink CQI (Channel Quality Indicator) is {ue.downlink_cqi}. "
    )

    # Explain what CQI represents
    explanation_text += (
        "CQI is a measure of the channel quality as perceived by the UE. "
        "It is used by the network to determine the most suitable modulation and coding scheme (MCS) (queried via /net/ue/attribute/{ue_imsi}/downlink_mcs_index and /net/ue/attribute/{ue_imsi}/downlink_mcs_data) "
        "to maximize data throughput while maintaining reliable communication."
    )

    # Explain the relationship with downlink SINR
    explanation_text += (
        " The CQI value is derived from the UE's downlink SINR (Signal-to-Interference-plus-Noise Ratio), "
        "which reflects the signal quality. Higher SINR typically results in higher CQI values, "
        "enabling the use of more efficient MCS for data transmission."
    )

    # Explain the relationship with MCS index
    explanation_text += (
        " The CQI value directly influences the selection of the MCS index, "
        "which determines the modulation order and coding rate used for data transmission. "
        "Higher CQI values allow for higher MCS indices, enabling faster data rates."
    )

    # Add interpretation of CQI values
    if ue.downlink_cqi >= 10:
        explanation_text += " This CQI value indicates excellent channel conditions, allowing for high data rates."
    elif 7 <= ue.downlink_cqi < 10:
        explanation_text += " This CQI value indicates good channel conditions, supporting moderate to high data rates."
    elif 4 <= ue.downlink_cqi < 7:
        explanation_text += " This CQI value indicates average channel conditions, supporting moderate data rates."
    else:
        explanation_text += " This CQI value indicates poor channel conditions, resulting in low data rates."

    return explanation_text


# ue.downlink_mcs_index = -1
@knowledge_explainer(
    "/net/ue/attribute/{ue_imsi}/downlink_mcs_index",
    tags=[KnowledgeTag.UE, KnowledgeTag.QoS],
    related=[
        (
            KnowledgeRelationship.DERIVED_FROM,
            "/net/ue/attribute/{ue_imsi}/downlink_cqi",
        ),
        (
            KnowledgeRelationship.ASSOCIATED_WITH,
            "/net/ue/attribute/{ue_imsi}/downlink_mcs_data",
        ),
        (
            KnowledgeRelationship.DETERMINED_IN_METHOD,
            "/net/cells/{cell_id}/method/select_ue_mcs",
        ),
    ],
)
def ue_downlink_mcs_index_explainer(sim, knowledge_router, query_key, params):
    ue = sim.ue_list.get(params["ue_imsi"], None)
    if not ue:
        return f"UE {params['ue_imsi']} not found. Note that ue_imsi is case-sensitive."

    explanation_text = f"The UE's downlink MCS (Modulation and Coding Scheme) index is {ue.downlink_mcs_index}. "

    # Explain what MCS index represents
    explanation_text += (
        "The MCS index determines the modulation order and coding rate used for data transmission. "
        "It directly impacts the data rate and reliability of the communication link. "
        "Higher MCS indices correspond to higher data rates but require better channel conditions."
    )

    # Explain the relationship with downlink CQI
    explanation_text += (
        " The MCS index is derived from the UE's downlink CQI (Channel Quality Indicator, queried via /net/ue/attribute/{ue_imsi}/downlink_cqi), "
        "which reflects the channel quality. Higher CQI values allow for higher MCS indices, "
        "enabling faster data rates."
    )

    # Explain the relationship with downlink MCS data
    explanation_text += (
        " The MCS index is associated with specific modulation and coding parameters, "
        "which are stored in the downlink MCS data attribute (queried via /net/ue/attribute/{ue_imsi}/downlink_mcs_data). These parameters include the modulation order, "
        "target code rate, and spectral efficiency."
    )

    # Add interpretation of MCS index values
    if ue.downlink_mcs_index == -1:
        explanation_text += (
            " This MCS index indicates that the UE is not currently assigned a valid MCS, "
            "possibly due to poor channel conditions or lack of resource allocation."
        )
    else:
        mcs_data = ue.downlink_mcs_data
        explanation_text += (
            f" For this MCS index, the modulation order is {mcs_data['modulation_order']}, "
            f"the target code rate is {mcs_data['target_code_rate']}, and the spectral efficiency is {mcs_data['spectral_efficiency']}."
        )

    return explanation_text


# ue.downlink_mcs_data = None
@knowledge_explainer(
    "/net/ue/attribute/{ue_imsi}/downlink_mcs_data",
    tags=[KnowledgeTag.UE, KnowledgeTag.QoS],
    related=[
        (
            KnowledgeRelationship.ASSOCIATED_WITH,
            "/net/ue/attribute/{ue_imsi}/downlink_mcs_index",
        ),
        (
            KnowledgeRelationship.DETERMINED_IN_METHOD,
            "/net/cells/{cell_id}/method/select_ue_mcs",
        ),
        (
            KnowledgeRelationship.DERIVED_FROM,
            "/net/ue/attribute/{ue_imsi}/downlink_cqi",
        ),
    ],
)
def ue_downlink_mcs_data_explainer(sim, knowledge_router, query_key, params):
    ue = sim.ue_list.get(params["ue_imsi"], None)
    if not ue:
        return f"UE {params['ue_imsi']} not found. Note that ue_imsi is case-sensitive."

    if ue.downlink_mcs_data is None:
        return (
            "The UE's downlink MCS (Modulation and Coding Scheme) data is not available. "
            "This may be due to poor channel conditions or the UE not being assigned a valid MCS."
        )

    mcs_data = ue.downlink_mcs_data
    explanation_text = (
        f"The UE's downlink MCS data includes the following parameters: "
        f"modulation order: {mcs_data['modulation_order']}, "
        f"target code rate: {mcs_data['target_code_rate']}, "
        f"and spectral efficiency: {mcs_data['spectral_efficiency']}."
    )

    # Explain what each parameter represents
    explanation_text += (
        " The modulation order determines the number of bits transmitted per symbol, "
        "with higher orders enabling higher data rates but requiring better channel conditions. "
        "The target code rate specifies the fraction of useful data in the transmitted bits, "
        "with higher rates improving efficiency but reducing error correction capability. "
        "Spectral efficiency represents the data rate achieved per unit of bandwidth, "
        "indicating how efficiently the spectrum is utilized."
    )

    # Explain the relationship with MCS index
    explanation_text += (
        " This MCS data is associated with the UE's downlink MCS index (queried via /net/ue/attribute/{ue_imsi}/downlink_mcs_index), "
        "which is selected based on the UE's downlink CQI (Channel Quality Indicator) (queried via /net/ue/attribute/{ue_imsi}/downlink_cqi) "
        "and the network's modulation and coding scheme table."
    )

    return explanation_text


# skip uplink direction for now
# skip ue.uplink_bitrate = 0
# skip ue.uplink_latency = 0
# skip ue.uplink_transmit_power_dBm = settings.UE_TRANSMIT_POWER

# skip ue.serving_cell_history = []


# ue.current_cell = None
@knowledge_explainer(
    "/net/ue/attribute/{ue_imsi}/current_cell",
    tags=[KnowledgeTag.UE],
    related=[
        (
            KnowledgeRelationship.DETERMINED_IN_METHOD,
            "/net/ue/method/cell_selection_and_camping",
        ),
        (
            KnowledgeRelationship.ASSOCIATED_WITH,
            "/net/cell/{cell_id}",
        ),
    ],
)
def ue_current_cell_explainer(sim, knowledge_router, query_key, params):
    ue = sim.ue_list.get(params["ue_imsi"], None)
    if not ue:
        return f"UE {params['ue_imsi']} not found. Note that ue_imsi is case-sensitive."

    if ue.current_cell is None:
        return "The UE is not currently connected to any cell."

    explanation_text = (
        f"The UE is currently connected to cell {ue.current_cell.cell_id}. "
    )

    explanation_text += (
        " During the power up procedure (queried via /net/ue/method/power_up), the UE scans the cells and selects the cell with the highest received power, "
        "adjusted by the cell's individual offset (CIO) and frequency priority."
        "This process is part of the cell selection and camping procedure queried via /net/ue/method/cell_selection_and_camping."
    )

    explanation_text += " The UE's current cell can also be adjusted by handover controls from the network."

    return explanation_text


# ue.power_up()
@knowledge_explainer(
    "/net/ue/method/power_up",
    tags=[KnowledgeTag.UE],
    related=[
        (
            KnowledgeRelationship.CALL_METHOD,
            "/net/ue/method/monitor_signal_strength",
        ),
        (
            KnowledgeRelationship.CALL_METHOD,
            "/net/ue/method/cell_selection_and_camping",
        ),
        (
            KnowledgeRelationship.CALL_METHOD,
            "/net/ue/method/authenticate_and_register",
        ),
    ],
)
def ue_power_up_explainer(sim, knowledge_router, query_key, params):
    explanation_text = (
        "The `power_up` method is responsible for initializing the UE's connection to the network. "
        "This process involves several steps:\n\n"
        "1. **Signal Strength Monitoring**: The UE scans for available cells and measures their signal strength. "
        "Cells are ranked based on their received power and frequency priority. (method query key: /net/ue/method/monitor_signal_strength).\n\n"
        "2. **Cell Selection and Camping**: The UE selects the most suitable cell based on the measured signal strength "
        "and camps on it. This step ensures that the UE is connected to the cell with the best signal quality. (method query key: /net/ue/method/cell_selection_and_camping)\n\n"
        "3. **Authentication and Registration**: The UE performs authentication and registration with the selected cell's base station. "
        "During this step, the UE is assigned a network slice type (e.g., eMBB, URLLC, or mMTC) and a corresponding QoS profile. (method query key: /net/ue/method/authenticate_and_register).\n\n"
        "\nOnce the above steps are successfully completed, the UE is marked as connected to the network."
    )

    explanation_text += (
        " If any of these steps fail (e.g., no cells are detected, or authentication fails), "
        "the UE will not be added to the simulation."
    )

    return explanation_text


@knowledge_explainer(
    key="/net/ue/method/monitor_signal_strength",
    tags=[KnowledgeTag.UE],
    related=[
        (
            KnowledgeRelationship.DETERMINE_ATTRIBUTE,
            "/net/ue/attribute/{ue_imsi}/downlink_received_power_dBm_dict",
        ),
        (
            KnowledgeRelationship.CALL_METHOD,
            "/net/ue/method/calculate_SINR_and_CQI",
        ),
    ],
)
def ue_monitor_signal_strength_explainer(sim, knowledge_router, query_key, params):
    explanation_text = (
        "The `monitor_signal_strength` method allows the UE to scan for available cells "
        "and measure their downlink signal strength. This process involves:\n\n"
        "1. **Path Loss Calculation**: The UE calculates the received power from each cell "
        "based on the cell's transmit power, distance, and the path loss model.\n\n"
        "2. **Filtering Detected Cells**: Only cells with received power above the detection threshold "
        "and meeting the minimum quality requirements are considered.\n\n"
        "3. **SINR and CQI Calculation**: calls another method `/net/ue/method/calculate_SINR_and_CQi` where "
        "the UE calculates the Signal-to-Interference-plus-Noise Ratio (SINR) "
        "and derives the Channel Quality Indicator (CQI) for the current serving cell (/net/ue/attribute/{ue_imsi}/current_cell) if applicable."
    )

    explanation_text += (
        " This method is critical for determining the UE's connectivity and channel quality, "
        "which influence procedures such as cell selection, resource allocation and RRC event monitoring."
    )

    return explanation_text


@knowledge_explainer(
    key="/net/ue/method/cell_selection_and_camping",
    tags=[KnowledgeTag.UE],
    related=[
        (
            KnowledgeRelationship.DEPENDS_ON,
            "/net/ue/attribute/{ue_imsi}/downlink_received_power_dBm_dict",
        ),
        (
            KnowledgeRelationship.DETERMINE_ATTRIBUTE,
            "/net/ue/attribute/{ue_imsi}/current_cell",
        ),
    ],
)
def ue_cell_selection_and_camping_explainer(sim, knowledge_router, query_key, params):
    explanation_text = (
        "The `cell_selection_and_camping` method enables the UE to select the most suitable cell "
        "to connect to. This process involves:\n\n"
        "1. **Cell Ranking**: The UE ranks detected cells based on their received power, "
        "frequency priority, and cell-specific offsets (CIO).\n\n"
        "2. **Cell Selection**: The UE selects the cell with the highest rank that meets the minimum quality requirements.\n\n"
        "3. **Camping**: The UE camps on the selected cell, marking it as the current serving cell."
    )

    explanation_text += (
        " This method ensures that the UE connects to the best available cell, "
        "which is essential for reliable communication and efficient resource utilization."
    )

    return explanation_text


@knowledge_explainer(
    key="/net/ue/method/authenticate_and_register",
    tags=[KnowledgeTag.UE],
    related=[
        (
            KnowledgeRelationship.DETERMINE_ATTRIBUTE,
            "/net/ue/attribute/{ue_imsi}/slice_type",
        ),
        (
            KnowledgeRelationship.DETERMINE_ATTRIBUTE,
            "/net/ue/attribute/{ue_imsi}/qos_profile",
        ),
        (
            KnowledgeRelationship.CALL_METHOD,
            "/net/cell/{cell_id}/method/setup_rrc_measurement_event_monitors",
        ),
    ],
)
def ue_authenticate_and_register_explainer(sim, knowledge_router, query_key, params):
    explanation_text = (
        "The `authenticate_and_register` method allows the UE to authenticate with the network "
        "and register with its serving cell. This process involves:\n\n"
        f"1. **Slice Type Assignment**: The UE randomly selects one of the slide types ({", ".join(NETWORK_SLICES.keys())})\n\n"
        "2. **QoS Profile Assignment**: based on the selected slice type, the UE gets the associated QoS Profile, "
        "defining parameters like 5QI, guaranteed uplink/donwlink bit rate (GBR) and uplink/downlink latency.\n\n"
        "3. **Setup RRC Event Monitor**: calls method `/net/ue/method/setup_rrc_measurement_event_monitors` to set up RRC (Radio Resource Control) event monitors to track signal quality and other parameters. "
    )

    explanation_text += (
        " This method is crucial for establishing the UE's identity and ensuring it receives "
        "the appropriate network resources and quality of service."
    )

    return explanation_text


@knowledge_getter(
    key="/net/ue",
)
def ue_knowledge_getter(sim, knowledge_router, query_key, params):
    return json.dumps(
        {
            "description": "UE-related knowledge base",
            "available_queries": [
                "/net/ue/attribute/{ue_imsi}/{attribute_name}",
                "/net/ue/method/{method_name}",
            ],
            "supported_attributes": SUPPORTED_UE_ATTRIBUTES,
            "supported_methods": SUPPORTED_UE_METHODS,
        },
        indent=4,
    )


@knowledge_explainer(
    key="/net/ue",
    tags=[KnowledgeTag.UE, KnowledgeTag.KNOWLEDGE_GUIDE],
    related=[],
)
def ue_knowledge_explainer(sim, knowledge_router, query_key, params):
    return f"""Welcome to the UE knowledge base!
This knowledge base provides access to the knowledge of all the connected UE.
You can retrieve information about UE attributes and methods using the following query keys:
* `/net/ue/attribute/{{ue_imsi}}/{{attribute_name}}`: Retrieve a specific attribute of a UE.
* `/net/ue/method/{{method_name}}`: Access a specific method of the UE class.
For example, you can query `/net/ue/attribute/{{ue_imsi}}/position_x` to get the x-coordinate of a UE.
or `/net/ue/method/power_up` to get the source code or explanation of the `power_up` method.

supported attributes include:
{", ".join(SUPPORTED_UE_ATTRIBUTES)}

supported methods include: 
{", ".join(SUPPORTED_UE_METHODS)}"""
