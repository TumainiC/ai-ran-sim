import random
import settings


class CoreNetwork:
    def __init__(self, simulation_engine=None):
        self.simulation_engine = simulation_engine
        self.active_ues = {}

    def authenticate_and_register(self, ue):
        print(f"CoreNetwork: Authenticating UE {ue.ue_imsi}...")
        slice_info = self.select_network_slice(ue)
        qos_profile = self.assign_qos(ue, slice_info)

        self.active_ues[ue.ue_imsi] = {"slice": slice_info, "qos": qos_profile}
        return slice_info, qos_profile

    def select_network_slice(self, ue):
        # Simple logic: random or capability-based
        selected_slice = random.choice(list(settings.NETWORK_SLICES.keys()))
        print(f"CoreNetwork: Assigned slice '{selected_slice}' to UE {ue.ue_imsi}")
        return selected_slice

    def assign_qos(self, ue, slice_info):
        qos_profile = settings.NETWORK_SLICES[slice_info]
        print(f"CoreNetwork: Assigned QoS for slice '{slice_info}' to UE {ue.ue_imsi}")
        return qos_profile

    def deregister_ue(self, ue):
        if ue.ue_imsi in self.active_ues:
            print(f"CoreNetwork: Deregistering UE {ue.ue_imsi}")
            del self.active_ues[ue.ue_imsi]
