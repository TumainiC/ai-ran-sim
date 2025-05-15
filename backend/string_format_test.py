pattern = "/net/ue/attribute/{ue_imsi}/{attribute_name}"
pattern = "/net/ue/attribute/{ue_imsi}"

params = {
    "ue_imsi": "123456789012345",
    "attribute_name": "downlink_bitrate",
}

print(pattern.format(**params))