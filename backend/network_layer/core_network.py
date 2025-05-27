import settings
import random


class CoreNetwork:
    def __init__(self, simulation_engine=None):
        self.simulation_engine = simulation_engine
        self.ue_subscription_data = settings.CORE_UE_SUBSCRIPTION_DATA.copy()
        self.active_ues = {}

    def handle_ue_authentication_and_registration(self, ue):
        slice_type, qos_profile = self.select_ue_slice_and_qos_profile(ue)
        ue_reg_res = {"ue": ue, "slice_type": slice_type, "qos_profile": qos_profile}
        self.active_ues[ue.ue_imsi] = ue_reg_res
        return ue_reg_res.copy()

    def select_ue_slice_and_qos_profile(self, ue):
        if ue.ue_imsi not in self.ue_subscription_data:
            return None, None

        subscribed_slice_types = self.ue_subscription_data[ue.ue_imsi]
        slice_type = random.choice(subscribed_slice_types)
        qos_profile = settings.NETWORK_SLICES[slice_type].copy()

        return slice_type, qos_profile

    def handle_deregistration_request(self, ue):
        if ue.ue_imsi in self.active_ues:
            print(f"CoreNetwork: Deregistering UE {ue.ue_imsi}")
            del self.active_ues[ue.ue_imsi]
        else:
            print(f"CoreNetwork: UE {ue.ue_imsi} not found in active UEs.")
