# ---------------------------
# Network Operation Configuration
# ---------------------------
NETWORK_COVERAGE_WIDTH = 1000
NETWORK_COVERAGE_HEIGHT = 800


# ---------------------------
# User Equipment (UE) Configuration
# ---------------------------
UE_BOUNDARY_BUFFER = 50
UE_BOUNDARY_X_MIN = UE_BOUNDARY_BUFFER
UE_BOUNDARY_X_MAX = NETWORK_COVERAGE_WIDTH - UE_BOUNDARY_BUFFER
UE_BOUNDARY_Y_MIN = UE_BOUNDARY_BUFFER
UE_BOUNDARY_Y_MAX = NETWORK_COVERAGE_HEIGHT - UE_BOUNDARY_BUFFER
UE_DEFAULT_TIMEOUT = 1000
UE_DEFAULT_SPAWN_RATE_MIN = 1
UE_DEFAULT_SPAWN_RATE_MAX = 5
UE_MIN_PRB_RANGE_MIN = 5
UE_MIN_PRB_RANGE_MAX = 15
UE_FIXED_COUNT = 100
UE_REFRESH_PORTION = 0.8


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
