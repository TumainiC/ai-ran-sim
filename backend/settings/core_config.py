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