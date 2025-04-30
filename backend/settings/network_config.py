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
# RAN Configuration
# ---------------------------
RAN_BS_DEFAULT_MIN_ALLOCABLE_PRB = 20
RAN_DEFAULT_RU_RADIUS = 180
RAN_BS_LOAD_HISTORY_LENGTH = 3
RAN_BS_REF_SIGNAL_DEFAULT_TRASNMIT_POWER = 40
RAN_DEFAULT_BS_LIST = [
    ("bs_11", 200, 200),
    ("bs_12", 400, 200),
    ("bs_13", 600, 200),
    ("bs_14", 800, 200),
    ("bs_21", 200, 400),
    ("bs_22", 400, 400),
    ("bs_23", 600, 400),
    ("bs_24", 800, 400),
    ("bs_31", 200, 600),
    ("bs_32", 400, 600),
    ("bs_33", 600, 600),
    ("bs_34", 800, 600),
]


# ---------------------------
# Channel Configuration
# ---------------------------
CHANNEL_PATH_LOSS_EXPONENT = 3.5