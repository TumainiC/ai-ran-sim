import random
import settings


class CoreNetwork:
    def __init__(self, simulation_engine=None):
        self.simulation_engine = simulation_engine
        self.active_ues = {}

    def handle_ue_authentication_and_registration(self, ue, ue_auth_reg_msg):
        self.active_ues[ue.ue_imsi] = ue_auth_reg_msg.copy()
        return ue_auth_reg_msg.copy()

    def handle_deregistration_request(self, ue):
        if ue.ue_imsi in self.active_ues:
            print(f"CoreNetwork: Deregistering UE {ue.ue_imsi}")
            del self.active_ues[ue.ue_imsi]
        else:
            print(f"CoreNetwork: UE {ue.ue_imsi} not found in active UEs.")
