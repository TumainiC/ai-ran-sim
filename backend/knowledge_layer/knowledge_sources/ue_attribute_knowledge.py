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
    # "downlink_latency",
    "downlink_sinr",
    "downlink_cqi",
    "downlink_mcs_index",
    "downlink_mcs_data",
    # "uplink_bitrate",
    # "uplink_latency",
    # "uplink_transmit_power_dBm",
    # "serving_cell_history",
    "current_cell",
]


@knowledge_getter(
    key="/net/user_equipments/attribute/{ue_imsi}/{attribute_name}",
)
def ue_attribute_getter(sim, knowledge_router, query_key, params):
    ue = sim.ue_list.get(params["ue_imsi"], None)
    if not ue:
        return f"UE {params['ue_imsi']} not found. Note that ue_imsi is case-sensitive."
    attribute_name = params["attribute_name"]

    if attribute_name not in SUPPORTED_UE_ATTRIBUTES:
        return f"""Attribute {attribute_name} not supported. 
Supported attributes: {', '.join(SUPPORTED_UE_ATTRIBUTES)}"""

    if hasattr(ue, attribute_name):
        attribute = getattr(ue, attribute_name)
        # check the attribute is not a function
        if callable(attribute):
            return f"{attribute_name} is a function, query it via /net/user_equipments/method/{attribute_name} instead."
        if isinstance(attribute, dict):
            return json.dumps(attribute)
        elif isinstance(attribute, list):
            return json.dumps(attribute)
        return str(attribute)
    else:
        # raise ValueError(f"Attribute {attribute_name} not found in UE object.")
        return f"""Attribute {attribute_name} not found in UE class. 
Supported attributes: {", ".join(SUPPORTED_UE_ATTRIBUTES)}"""


@knowledge_explainer(
    "/net/user_equipments/attribute/ue_imsi",
    tags=[KnowledgeTag.UE, KnowledgeTag.ID],
    related=[],
)
def ue_imsi_explainer(sim, knowledge_router, query_key, params):
    return (
        "The UE's IMSI (International Mobile Subscriber Identity) is a unique identifier "
        "assigned to the UE. Examples in this simulated network are IMSI_1, IMSI_32, etc."
    )


@knowledge_explainer(
    "/net/user_equipments/attribute/position_x",
    tags=[KnowledgeTag.UE, KnowledgeTag.LOCATION],
    related=[
        (
            KnowledgeRelationship.SET_BY_METHOD,
            "/net/user_equipments/method/move_towards_target",
        )
    ],
)
def ue_position_x_explainer(sim, knowledge_router, query_key, params):
    return f"The UE's x-coordinate (unit: m) in the simulated area."


@knowledge_explainer(
    "/net/user_equipments/attribute/position_y",
    tags=[KnowledgeTag.UE, KnowledgeTag.LOCATION],
    related=[
        (
            KnowledgeRelationship.SET_BY_METHOD,
            "/net/user_equipments/method/move_towards_target",
        )
    ],
)
def ue_position_y_explainer(sim, knowledge_router, query_key, params):
    return f"The UE's y-coordinate (unit: m) in the simulated area."


@knowledge_explainer(
    "/net/user_equipments/attribute/target_x",
    tags=[KnowledgeTag.UE, KnowledgeTag.MOBILITY],
    related=[
        (
            KnowledgeRelationship.USED_BY_METHOD,
            "/net/user_equipments/method/move_towards_target",
        )
    ],
)
def ue_target_x_explainer(sim, knowledge_router, query_key, params):
    return f"The UE's target x-coordinate (unit: m) in the simulated area."


@knowledge_explainer(
    "/net/user_equipments/attribute/target_y",
    tags=[KnowledgeTag.UE, KnowledgeTag.MOBILITY],
    related=[
        (
            KnowledgeRelationship.USED_BY_METHOD,
            "/net/user_equipments/method/move_towards_target",
        )
    ],
)
def ue_target_y_explainer(sim, knowledge_router, query_key, params):
    return f"The UE's target y-coordinate (unit: m) in the simulated area."


@knowledge_explainer(
    "/net/user_equipments/attribute/speed_mps",
    tags=[KnowledgeTag.UE, KnowledgeTag.MOBILITY],
    related=[
        (
            KnowledgeRelationship.USED_BY_METHOD,
            "/net/user_equipments/method/move_towards_target",
        )
    ],
)
def ue_speed_mps_explainer(sim, knowledge_router, query_key, params):
    return """The UE's speed (unit: m/s) in the simulated area. 
The UE will move towards its target position at this speed."""


@knowledge_explainer(
    "/net/user_equipments/attribute/time_remaining",
    tags=[KnowledgeTag.UE, KnowledgeTag.SIMULATION],
    related=[
        (
            KnowledgeRelationship.USED_BY_METHOD,
            "/net/user_equipments/method/step",
        ),
        (
            KnowledgeRelationship.SET_BY_METHOD,
            "/net/user_equipments/method/step",
        ),
    ],
)
def ue_time_remaining_explainer(sim, knowledge_router, query_key, params):
    return (
        "The number of simulation steps remaining for the UE, "
        "which is decremented by 1 every simulation step. "
        "When it reaches 0, the UE will deregister itself from the newtork "
        "and removed from the simulation."
    )


@knowledge_explainer(
    "/net/user_equipments/attribute/slice_type",
    tags=[KnowledgeTag.UE, KnowledgeTag.SIMULATION],
    related=[
        (
            KnowledgeRelationship.SET_BY_METHOD,
            "/net/user_equipments/method/authenticate_and_register",
        ),
        (
            KnowledgeRelationship.ASSOCIATED_WITH,
            "/net/user_equipments/attribute/qos_profile",
        ),
    ],
)
def ue_slice_type_explainer(sim, knowledge_router, query_key, params):
    return f"""
The UE's slice type is randomly selected during the authentication and registration process, 
which can be one of the following:
* eMBB (Enhanced Mobile Broadband): Designed to provide high data rates and capacity for applications like video streaming.
    corresponding QoS profile: {json.dumps(NETWORK_SLICES[NETWORK_SLICE_EMBB_NAME])}
* URLLC (Ultra-Reliable Low Latency Communication): Designed for applications requiring ultra-reliable and low-latency communication, such as autonomous driving.
    corresponding QoS profile: {json.dumps(NETWORK_SLICES[NETWORK_SLICE_URLLC_NAME])}
* mMTC (Massive Machine Type Communication): Designed for applications with a large number of low-power devices, such as IoT sensors.
    corresponding QoS profile: {json.dumps(NETWORK_SLICES[NETWORK_SLICE_MTC_NAME])}

When the UE picks up a slice type, it will also get the corresponding QoS profile 
(query /net/user_equipments/attribute/qos_profile for more details).
"""


@knowledge_explainer(
    "/net/user_equipments/attribute/qos_profile",
    tags=[KnowledgeTag.UE, KnowledgeTag.SIMULATION],
    related=[
        (
            KnowledgeRelationship.SET_BY_METHOD,
            "/net/user_equipments/method/authenticate_and_register",
        ),
        (
            KnowledgeRelationship.ASSOCIATED_WITH,
            "/net/user_equipments/attribute/slice_type",
        ),
    ],
)
def ue_qos_profile_explainer(sim, knowledge_router, query_key, params):
    # v_5qi = f"5QI: {slice_qos_profile.get("5QI")}"
    # v_gbr_dl = f"GBR_DL: {slice_qos_profile.get("GBR_DL")}"
    # v_gbr_ul = f"GBR_UL: {slice_qos_profile.get("GBR_UL")}"
    # v_latency_dl = f"latency_dl: {slice_qos_profile.get("latency_dl")}"
    # v_latency_ul = f"latency_ul: {slice_qos_profile.get("latency_ul")}"

    return """The UE's QoS (Quality of Service) profile is a set of parameters that define how the network should treat the UE's traffic:
    * 5QI is a numerical identifier (e.g., 1, 9, 66, etc.) that maps to a specific QoS profile — a predefined set of parameters that define how the network should treat a particular type of traffic. It simplifies QoS management by bundling parameters under a single value.
    * GBR_DL (Guaranteed Bit Rate Downlink) is the minimum guaranteed data rate for downlink traffic. It ensures that the user equipment (UE) receives a certain amount of bandwidth for its downlink communication. 
    * GBR_UL (Guaranteed Bit Rate Uplink) is the minimum guaranteed data rate for uplink traffic. It ensures that the UE can send a certain amount of data to the network without being throttled.
    * latency_ul (Uplink Latency) is the maximum time it takes for a packet to travel from the UE to the network. 
    * latency_dl (Downlink Latency) is the maximum time it takes for a packet to travel from the network to the UE. 

Note that the actual bitrate and latency (get_knowledge_value: /net/user_equipments/attribute/{ue_imsi}/downlink_bitrate, /net/user_equipments/attribute/{ue_imsi}/uplink_bitrate, /net/user_equipments/attribute/{ue_imsi}/uplink_latency, /net/user_equipments/attribute/{ue_imsi}/downlink_latency) may vary based on network conditions and other factors.
The values provided in the QoS profile are guarantees that the network aims to meet, but they are not absolute limits."""


@knowledge_explainer(
    "/net/user_equipments/attribute/connected",
    tags=[KnowledgeTag.UE, KnowledgeTag.SIMULATION],
    related=[
        (
            KnowledgeRelationship.SET_BY_METHOD,
            "/net/user_equipments/method/authenticate_and_register",
        ),
        (
            KnowledgeRelationship.SET_BY_METHOD,
            "/net/user_equipments/method/deregister",
        ),
    ],
)
def ue_connected_explainer(sim, knowledge_router, query_key, params):
    return "A boolean representing whether the UE is connected or not to the network (served by a cell and registered with the core)."


@knowledge_explainer(
    "/net/user_equipments/attribute/downlink_bitrate",
    tags=[KnowledgeTag.UE, KnowledgeTag.QoS],
    related=[
        (
            KnowledgeRelationship.SET_BY_METHOD,
            "/net/user_equipments/method/set_downlink_bitrate",
        ),
    ],
)
def ue_downlink_bitrate_explainer(sim, knowledge_router, query_key, params):
    return (
        "The UE's actual downlink bitrate (unit: bps), calculated by the serving cell."
        " Comparing this value to the UE's QoS profile (get_knowledge_value: /net/user_equipments/attribute/{ue_imsi}/qos_profile) "
        "can help determine if the UE is receiving the expected service quality."
    )


# @knowledge_explainer(
#     "/net/user_equipments/attribute/downlink_latency",
#     tags=[KnowledgeTag.UE, KnowledgeTag.QoS],
#     related=[
#         (
#             KnowledgeRelationship.CONSTRAINED_BY,
#             "/net/user_equipments/attribute/qos_profile",
#         ),
#     ],
# )
# def ue_downlink_latency_explainer(sim, knowledge_router, query_key, params):
#     return (
#         "The downlink latency attribute represents the time (in milliseconds) it takes for a data packet to travel from the network to the user equipment (UE). "
#         "This latency is influenced by factors such as radio access network scheduling, propagation delay, and network congestion. "
#         "The downlink latency is typically compared against the guaranteed latency defined in the UE's QoS profile to assess whether the network is meeting service expectations. "
#         "Lower downlink latency is critical for applications requiring real-time responsiveness, such as online gaming, voice/video calls, and industrial automation."
#     )


# skip ue/attribute/rrc_measurement_event_monitors
# skip ue/attribute/downlink_received_power_dBm_dict


@knowledge_explainer(
    "/net/user_equipments/attribute/downlink_sinr",
    tags=[KnowledgeTag.UE, KnowledgeTag.QoS],
    related=[
        (
            KnowledgeRelationship.DEPENDS_ON,
            "/net/user_equipments/attribute/downlink_received_power_dBm_dict",
        ),
        (
            KnowledgeRelationship.DEPENDS_ON,
            "/net/cell/attribute/transmit_power_dBm",
        ),
        (
            KnowledgeRelationship.AFFECTS,
            "/net/user_equipments/attribute/downlink_cqi",
        ),
        (
            KnowledgeRelationship.SET_BY_METHOD,
            "/net/user_equipments/method/calculate_SINR_and_CQI",
        ),
    ],
)
def ue_downlink_sinr_explainer(sim, knowledge_router, query_key, params):
    return (
        "The downlink SINR (Signal-to-Interference-plus-Noise Ratio) attribute quantifies the quality of the radio signal received by the UE from its serving cell. "
        "A higher SINR indicates better signal quality, which enables higher data rates and more reliable communication. "
        "Typical SINR value ranges are interpreted as follows: values above 20 dB are considered excellent, 13–20 dB are good, 0–13 dB are acceptable, -10–0 dB are poor, and values below -10 dB indicate very poor signal quality. "
        "SINR directly impacts the selection of modulation and coding schemes and is a key factor in link adaptation and handover decisions."
    )


@knowledge_explainer(
    "/net/user_equipments/attribute/downlink_cqi",
    tags=[KnowledgeTag.UE, KnowledgeTag.QoS],
    related=[
        (
            KnowledgeRelationship.DERIVED_FROM,
            "/net/user_equipments/attribute/downlink_sinr",
        ),
        (
            KnowledgeRelationship.AFFECTS,
            "/net/user_equipments/attribute/downlink_mcs_index",
        ),
        (
            KnowledgeRelationship.SET_BY_METHOD,
            "/net/user_equipments/method/calculate_SINR_and_CQI",
        ),
        (
            KnowledgeRelationship.USED_BY_METHOD,
            "/net/cell/method/select_ue_mcs",
        ),
    ],
)
def ue_downlink_cqi_explainer(sim, knowledge_router, query_key, params):
    return (
        "The downlink CQI (Channel Quality Indicator) attribute is a metric reported by the UE to indicate the perceived quality of the downlink channel. "
        "CQI is derived from the measured SINR and is used by the network to select the most appropriate modulation and coding scheme (MCS) for data transmission. "
        "Higher CQI values correspond to better channel conditions, allowing the network to use more efficient (higher-rate) MCS settings, which increases throughput. "
        "Lower CQI values indicate poorer channel conditions, prompting the network to use more robust but less efficient MCS settings to maintain reliable communication. "
    )


@knowledge_explainer(
    "/net/user_equipments/attribute/downlink_mcs_index",
    tags=[KnowledgeTag.UE, KnowledgeTag.QoS],
    related=[
        (
            KnowledgeRelationship.DERIVED_FROM,
            "/net/user_equipments/attribute/downlink_cqi",
        ),
        (
            KnowledgeRelationship.ASSOCIATED_WITH,
            "/net/user_equipments/attribute/downlink_mcs_data",
        ),
        (
            KnowledgeRelationship.SET_BY_METHOD,
            "/net/cell/method/select_ue_mcs",
        ),
    ],
)
def ue_downlink_mcs_index_explainer(sim, knowledge_router, query_key, params):
    return (
        "The downlink MCS (Modulation and Coding Scheme) index attribute specifies which modulation and coding scheme is currently assigned to the UE for downlink data transmission. "
        "The MCS index determines both the modulation order (e.g., QPSK, 16QAM, 64QAM) and the coding rate, directly impacting the data rate and reliability of the communication link. "
        "Higher MCS indices correspond to higher data rates but require better channel conditions, as indicated by the UE's CQI. "
        "If the MCS index is set to -1, it typically means that the UE is not currently assigned a valid MCS, possibly due to poor channel conditions or lack of resource allocation."
    )


@knowledge_explainer(
    "/net/user_equipments/attribute/downlink_mcs_data",
    tags=[KnowledgeTag.UE, KnowledgeTag.QoS],
    related=[
        (
            KnowledgeRelationship.ASSOCIATED_WITH,
            "/net/user_equipments/attribute/downlink_mcs_index",
        ),
        (
            KnowledgeRelationship.SET_BY_METHOD,
            "/net/cell/method/select_ue_mcs",
        ),
        (
            KnowledgeRelationship.DERIVED_FROM,
            "/net/user_equipments/attribute/downlink_cqi",
        ),
        (
            KnowledgeRelationship.USED_BY_METHOD,
            "/net/cell/method/estimate_ue_bitrate_and_latency",
        ),
    ],
)
def ue_downlink_mcs_data_explainer(sim, knowledge_router, query_key, params):
    return (
        "The downlink MCS (Modulation and Coding Scheme) data attribute contains detailed parameters associated with the currently assigned MCS index. "
        "These parameters typically include the modulation order (number of bits per symbol), the target code rate (fraction of useful data in the transmitted bits), and the spectral efficiency (data rate per unit bandwidth). "
        "Higher modulation orders and code rates enable higher data rates but require better channel conditions. "
        "The MCS data is selected based on the UE's reported CQI and is essential for determining the actual throughput achievable by the UE."
    )


@knowledge_explainer(
    "/net/user_equipments/attribute/current_cell",
    tags=[KnowledgeTag.UE],
    related=[
        (
            KnowledgeRelationship.SET_BY_METHOD,
            "/net/user_equipments/method/cell_selection_and_camping",
        )
    ],
)
def ue_current_cell_explainer(sim, knowledge_router, query_key, params):
    return (
        "The `current_cell` attribute indicates which cell the UE (User Equipment) is currently connected to in the network. "
        "The `current_cell` can change over time due to handover procedures, "
        "ensuring the UE maintains optimal connectivity as it moves or as radio conditions change. "
    )
