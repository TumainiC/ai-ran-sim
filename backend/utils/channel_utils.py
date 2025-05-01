import math


def pass_loss_urban_macro(distance_m, frequency_in_ghz):
    if distance_m <= 0:
        return 0
    return 28 + 22 * math.log10(distance_m) + 20 * math.log10(frequency_in_ghz)
    
def get_pass_loss_model(model_name):
    if model_name == "urban_macro":
        return pass_loss_urban_macro
    else:
        raise ValueError(f"Unknown path loss model: {model_name}")