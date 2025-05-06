import math


def dist_between(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


# Convert dBm to linear scale (Watts)
def dbm_to_watts(dbm):
    return 10 ** ((dbm - 30) / 10)


# Convert Watts to dBm
def watts_to_dbm(watts):
    return 10 * math.log10(watts) + 30

