# ---------------------------
# RAN Configuration
# ---------------------------
RAN_BS_LOAD_HISTORY_LENGTH = 3
RAN_BS_REF_SIGNAL_DEFAULT_TRASNMIT_POWER = 40

# Indicates that the UE is initiating signaling procedures such as Attach, Detach, or Tracking Area Update (TAU).
RAN_RRC_CONNECTION_EST_CAUSE_MO_SIGNALLING = "mo-Signalling"
# Used when the UE wants to transmit user data, such as initiating a data session.
RAN_RRC_CONNECTION_EST_CAUSE_MO_DATA = "mo-Data"
# Signifies that the UE is responding to a paging message, typically for mobile-terminated services like incoming calls or messages.
RAN_RRC_CONNECTION_EST_CAUSE_MT_ACCESS = "mt-Access"
# Used when the UE is attempting to establish a connection for an emergency call.
RAN_RRC_CONNECTION_EST_CAUSE_EMERGENCY = "emergency"


# Initial Registration
# Purpose: Occurs when the UE connects to the 5G network for the first time or after being deregistered.
# Triggers: UE power-on, SIM card change, or network re-entry after being out of coverage.
# Outcome: The network assigns a 5G-GUTI (Globally Unique Temporary UE Identity) and establishes necessary contexts for the UE.​
RAN_RRC_REGISTERATION_TYPE_INITIAL = "initial_registration"

# Mobility Registration Update
# Purpose: Updates the UE's registration when it moves to a new Tracking Area (TA) not covered by its current registration.
# Triggers: UE movement across different TAs.
# Outcome: The network updates the UE's location information to ensure continued service delivery.​
RAN_RRC_REGISTERATION_TYPE_MOBILITY = "mobility_registration_update"

# Periodic Registration Update
# Purpose: Confirms the UE's presence in the network at regular intervals.
# Triggers: Expiration of a network-defined timer (e.g., T3512).
# Outcome: Maintains the UE's active status and updates any necessary information.​
RAN_RRC_REGISTERATION_TYPE_PERIODIC = "periodic_registration_update"

# Emergency Registration
# Purpose: Allows the UE to register for emergency services without prior registration.
# Triggers: Initiation of an emergency call or service.
# Outcome: The network permits access to emergency services even if the UE lacks valid credentials.​
RAN_RRC_REGISTERATION_TYPE_EMERGENCY = "emergency_registration"


def RAN_BS_DEFAULT_CELLS(bs_id):
    return [
        {
            "cell_id": f"{bs_id}_cell_low_freq",
            "frequency_band": "n1",
            "carrier_frequency": 2100,
            "bandwidth": 20e6,
            "max_prb": 106,
            "cell_radius": 300,
            "transmit_power_dBm": 40,
            "cell_individual_offset_dBm": 0,
            "frequency_priority": 3,
            "qrx_level_min": -100,
        },
        {
            "cell_id": f"{bs_id}_cell_mid_freq",
            "frequency_band": "n78",
            "carrier_frequency": 3500,
            "bandwidth": 100e6,
            "max_prb": 273,
            "cell_radius": 150,
            "transmit_power_dBm": 40,
            "cell_individual_offset_dBm": 5,
            "frequency_priority": 5,
            "qrx_level_min": -100,
        },
        {
            "cell_id": f"{bs_id}_cell_high_freq",
            "frequency_band": "n258",
            "carrier_frequency": 26000,
            "bandwidth": 400e6,
            "max_prb": 264,
            "cell_radius": 50,
            "transmit_power_dBm": 40,  # assuming this is achieved by beamforming
            "cell_individual_offset_dBm": 10,
            "frequency_priority": 7,
            "qrx_level_min": -100,
        },
    ]


# Event	Description	Condition
# A1	Serving becomes better than threshold	Serving > threshold
# A2	Serving becomes worse than threshold	Serving < threshold
# A3	Neighbor becomes offset better than serving	Neighbor > Serving + offset
# A4	Neighbor becomes better than threshold	Neighbor > threshold
# A5	Serving becomes worse than threshold1 AND neighbor becomes better than threshold2	Serving < threshold1 AND Neighbor > threshold2
# B1	Inter-RAT neighbor becomes better than threshold	Used for LTE/other RATs
# B2	Serving becomes worse than threshold1 AND Inter-RAT neighbor becomes better than threshold2	Also for Inter-RAT
def RAN_BS_DEFAULT_RRC_MEASUREMENT_EVENTS():
    return [
        {
            "event_id": "A3",
            "power_threshold": 3,
            "time_to_trigger_in_sim_steps": 3,  # normally time-t-trigger or TTT is in time, but since we are in simulation, we can use simulation steps
        }
    ]


RAN_DEFAULT_BS_LIST = [
    {
        "bs_id": "bs_11",
        "position_x": 200,
        "position_y": 200,
        "cell_list": RAN_BS_DEFAULT_CELLS("bs_11"),
        "rrc_measurement_events": RAN_BS_DEFAULT_RRC_MEASUREMENT_EVENTS(),
    },
    {
        "bs_id": "bs_12",
        "position_x": 400,
        "position_y": 200,
        "cell_list": RAN_BS_DEFAULT_CELLS("bs_12"),
        "rrc_measurement_events": RAN_BS_DEFAULT_RRC_MEASUREMENT_EVENTS(),
    },
    {
        "bs_id": "bs_13",
        "position_x": 600,
        "position_y": 200,
        "cell_list": RAN_BS_DEFAULT_CELLS("bs_13"),
        "rrc_measurement_events": RAN_BS_DEFAULT_RRC_MEASUREMENT_EVENTS(),
    },
    {
        "bs_id": "bs_14",
        "position_x": 800,
        "position_y": 200,
        "cell_list": RAN_BS_DEFAULT_CELLS("bs_14"),
        "rrc_measurement_events": RAN_BS_DEFAULT_RRC_MEASUREMENT_EVENTS(),
    },
    {
        "bs_id": "bs_21",
        "position_x": 200,
        "position_y": 400,
        "cell_list": RAN_BS_DEFAULT_CELLS("bs_21"),
        "rrc_measurement_events": RAN_BS_DEFAULT_RRC_MEASUREMENT_EVENTS(),
    },
    {
        "bs_id": "bs_22",
        "position_x": 400,
        "position_y": 400,
        "cell_list": RAN_BS_DEFAULT_CELLS("bs_22"),
        "rrc_measurement_events": RAN_BS_DEFAULT_RRC_MEASUREMENT_EVENTS(),
    },
    {
        "bs_id": "bs_23",
        "position_x": 600,
        "position_y": 400,
        "cell_list": RAN_BS_DEFAULT_CELLS("bs_23"),
        "rrc_measurement_events": RAN_BS_DEFAULT_RRC_MEASUREMENT_EVENTS(),
    },
    {
        "bs_id": "bs_24",
        "position_x": 800,
        "position_y": 400,
        "cell_list": RAN_BS_DEFAULT_CELLS("bs_24"),
        "rrc_measurement_events": RAN_BS_DEFAULT_RRC_MEASUREMENT_EVENTS(),
    },
    {
        "bs_id": "bs_31",
        "position_x": 200,
        "position_y": 600,
        "cell_list": RAN_BS_DEFAULT_CELLS("bs_31"),
        "rrc_measurement_events": RAN_BS_DEFAULT_RRC_MEASUREMENT_EVENTS(),
    },
    {
        "bs_id": "bs_32",
        "position_x": 400,
        "position_y": 600,
        "cell_list": RAN_BS_DEFAULT_CELLS("bs_32"),
        "rrc_measurement_events": RAN_BS_DEFAULT_RRC_MEASUREMENT_EVENTS(),
    },
    {
        "bs_id": "bs_33",
        "position_x": 600,
        "position_y": 600,
        "cell_list": RAN_BS_DEFAULT_CELLS("bs_33"),
        "rrc_measurement_events": RAN_BS_DEFAULT_RRC_MEASUREMENT_EVENTS(),
    },
    {
        "bs_id": "bs_34",
        "position_x": 800,
        "position_y": 600,
        "cell_list": RAN_BS_DEFAULT_CELLS("bs_34"),
        "rrc_measurement_events": RAN_BS_DEFAULT_RRC_MEASUREMENT_EVENTS(),
    },
]
