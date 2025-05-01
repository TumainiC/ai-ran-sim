# ---------------------------
# Network Operation Configuration
# ---------------------------
NETWORK_COVERAGE_WIDTH = 1000
NETWORK_COVERAGE_HEIGHT = 800


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


# ---------------------------
# RAN Configuration
# ---------------------------
RAN_BS_LOAD_HISTORY_LENGTH = 3
RAN_BS_REF_SIGNAL_DEFAULT_TRASNMIT_POWER = 40


def RAN_BS_DEFAULT_CELLS(bs_id):
    return [
        {
            "cell_id": f"{bs_id}_cell_low_freq",
            "frequency_band": "n1",
            "carrier_frequency": 2100,
            "bandwidth": 20e6,
            "max_prbs": 106,
            "cell_radius": 300,
        },
        {
            "cell_id": f"{bs_id}_cell_mid_freq",
            "frequency_band": "n78",
            "carrier_frequency": 3500,
            "bandwidth": 100e6,
            "max_prbs": 273,
            "cell_radius": 150,
        },
        {
            "cell_id": f"{bs_id}_cell_high_freq",
            "frequency_band": "n258",
            "carrier_frequency": 26000,
            "bandwidth": 400e6,
            "max_prbs": 264,
            "cell_radius": 50,
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
