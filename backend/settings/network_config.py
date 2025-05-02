# ---------------------------
# Network Operation Configuration
# ---------------------------
NETWORK_COVERAGE_WIDTH = 1000
NETWORK_COVERAGE_HEIGHT = 800
REAL_LIFE_DISTANCE_MULTIPLIER = 10


# ---------------------------
# Network Slice Configuration
# ---------------------------
NETWORK_SLICE_EMBB_NAME = "eMBB"
NETWORK_SLICE_URLLC_NAME = "URLLC"
NETWORK_SLICE_MTC_NAME = "mMTC"

NETWORK_SLICES = {
    NETWORK_SLICE_EMBB_NAME: {"5QI": 9, "GBR": 100e6, "latency": 20},
    NETWORK_SLICE_URLLC_NAME: {"5QI": 1, "GBR": 10e6, "latency": 1},
    NETWORK_SLICE_MTC_NAME: {"5QI": 5, "GBR": 1e6, "latency": 50},
}


# ---------------------------
# RIC Configuration
# ---------------------------
RIC_ENABLE_HANDOVER = True
RIC_BRUTAL_HANDOVER = False


# ---------------------------
# Simulation Configuration
# ---------------------------
SIM_STEP_TIME_DEFAULT = 1
SIM_HANDOVER_HISTORY_LENGTH = 3
SIM_MAX_STEP = 200
SIM_SPAWN_UE_AFTER_LOAD_HISTORY_STABLIZED = True


# ---------------------------
# Channel Configuration
# ---------------------------
CHANNEL_PATH_LOSS_EXPONENT = 3.5
CHANNEL_PASS_LOSS_REF_DISTANCE = 1
CHANNEL_REFERENCE_PASS_LOSS = 0
CHANNEL_PASS_LOSS_MODEL = "urban_macro"


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
            "transmit_power": 40,
            "cell_individual_offset": 0,
            "frequency_priority": 3,
            "qrx_level_min": -71
        },
        {
            "cell_id": f"{bs_id}_cell_mid_freq",
            "frequency_band": "n78",
            "carrier_frequency": 3500,
            "bandwidth": 100e6,
            "max_prb": 273,
            "cell_radius": 150,
            "transmit_power": 40,
            "cell_individual_offset": 5,
            "frequency_priority": 5,
            "qrx_level_min": -64
        },
        {
            "cell_id": f"{bs_id}_cell_high_freq",
            "frequency_band": "n258",
            "carrier_frequency": 26000,
            "bandwidth": 400e6,
            "max_prb": 264,
            "cell_radius": 50,
            "transmit_power": 40, # assuming this is achieved by beamforming
            "cell_individual_offset": 10,
            "frequency_priority": 7,
            "qrx_level_min": -66
        },
    ]


RAN_DEFAULT_BS_LIST = [
    {
        "bs_id": "bs_11",
        "position_x": 200,
        "position_y": 200,
        "cells": RAN_BS_DEFAULT_CELLS("bs_11"),
    },
    {
        "bs_id": "bs_12",
        "position_x": 400,
        "position_y": 200,
        "cells": RAN_BS_DEFAULT_CELLS("bs_12"),
    },
    {
        "bs_id": "bs_13",
        "position_x": 600,
        "position_y": 200,
        "cells": RAN_BS_DEFAULT_CELLS("bs_13"),
    },
    {
        "bs_id": "bs_14",
        "position_x": 800,
        "position_y": 200,
        "cells": RAN_BS_DEFAULT_CELLS("bs_14"),
    },
    {
        "bs_id": "bs_21",
        "position_x": 200,
        "position_y": 400,
        "cells": RAN_BS_DEFAULT_CELLS("bs_21"),
    },
    {
        "bs_id": "bs_22",
        "position_x": 400,
        "position_y": 400,
        "cells": RAN_BS_DEFAULT_CELLS("bs_22"),
    },
    {
        "bs_id": "bs_23",
        "position_x": 600,
        "position_y": 400,
        "cells": RAN_BS_DEFAULT_CELLS("bs_23"),
    },
    {
        "bs_id": "bs_24",
        "position_x": 800,
        "position_y": 400,
        "cells": RAN_BS_DEFAULT_CELLS("bs_24"),
    },
    {
        "bs_id": "bs_31",
        "position_x": 200,
        "position_y": 600,
        "cells": RAN_BS_DEFAULT_CELLS("bs_31"),
    },
    {
        "bs_id": "bs_32",
        "position_x": 400,
        "position_y": 600,
        "cells": RAN_BS_DEFAULT_CELLS("bs_32"),
    },
    {
        "bs_id": "bs_33",
        "position_x": 600,
        "position_y": 600,
        "cells": RAN_BS_DEFAULT_CELLS("bs_33"),
    },
    {
        "bs_id": "bs_34",
        "position_x": 800,
        "position_y": 600,
        "cells": RAN_BS_DEFAULT_CELLS("bs_34"),
    },
]
