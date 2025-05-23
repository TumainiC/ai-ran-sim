import json
import random
from agents import function_tool

class UEDetails:
    def __init__(self, imsi: str, network_slices: list[str]):
        self.IMSI = imsi
        self.NETWORK_SLICES = network_slices

    def __repr__(self):
        return f"UEDetails(imsi={self.IMSI}, NETWORK_SLICE={self.NETWORK_SLICES})"
    
    def to_dict(self):
        return {
            'IMSI': self.IMSI,
            'NETWORK_SLICES': self.NETWORK_SLICES
        }

available_ues: dict[str, UEDetails] = {}

first_ue = None
last_ue = None

#this is the internal functionality as add_ue is not callable directly
def add_to_available_ues(imsi: str, network_slice: list[str]):
    global first_ue, last_ue
    available_ues[imsi] = UEDetails(imsi, network_slice)
    if first_ue is None:
        first_ue = imsi
    last_ue = imsi

@function_tool
def add_ue(imsi: str, network_slice: list[str]):
    print(f"Log: adding ue : {imsi}")
    """
    This tool adds the UE to the available_ues dictionary.

    Args:
        imsi (str): The IMSI of the UE, it should be like IMSI_<number>.
        network_slice (list[str]): A list of network slices that the UE is allowed to use.
                                     It can be at least one of [eMBB, urLLC, mMTC].
    """
    return add_to_available_ues(imsi, network_slice)

@function_tool
def get_available_ue_description() -> str:
    """
    This tool provides a description of the available UEs, including the first and last UE added.

    Returns:
        str: A description of the available UEs, including the first and last UE IMSIs.
             Returns "No UEs available." if the available_ues dictionary is empty.
    """
    global first_ue, last_ue
    if not available_ues:
        return "No UEs available."
    elif first_ue == last_ue:
        return f"Available UEs: There is only one UE with imsi: {first_ue}"
    else:
        return f"Available UEs: First UE imsi is {first_ue}, Last UE imsi is {last_ue}."

def get_ues():
    """
        gets all the ue details that are saved in available ues
    """
    ues = list(available_ues.values())
    return [ue.to_dict() for ue in ues]
    
    

network_slices = ["eMBB", "urLLC", "mMTC"]
for i in range(50):
    imsi = f"IMSI_{i + 1}"
    num_slices = random.randint(1, len(network_slices))
    ue_slices = random.sample(network_slices, num_slices)
    add_to_available_ues(imsi, ue_slices)