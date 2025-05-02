import random
import settings


class CoreNetwork:
    def __init__(self, simulation_engine=None):
        self.simulation_engine = simulation_engine
        self.active_ues = {}

    def handle_initial_ue_message(self, ue, ngap_message):
        authentication_request = {}
        return authentication_request

    def handle_authentication_response(self, ue, nas_message):
        security_mode_command_msg = {}
        return security_mode_command_msg

    def handle_security_mode_complete_msg(self, ue, nas_message):
        slice_info = self.select_network_slice(ue)
        registeration_accept_msg = {
            "slice_info": slice_info,
            "qos_profile": self.assign_qos(ue, slice_info),
        }
        self.active_ues[ue.ue_imsi] = {**registeration_accept_msg}
        return registeration_accept_msg
    
    def handle_registration_complete_msg(self, ue, nas_message):
        return {}

    def handle_deregistration_request(self, ue):
        if ue.ue_imsi in self.active_ues:
            print(f"CoreNetwork: Deregistering UE {ue.ue_imsi}")
            del self.active_ues[ue.ue_imsi]
        else:
            print(f"CoreNetwork: UE {ue.ue_imsi} not found in active UEs.")
        deregistration_accept_msg = {}
        return deregistration_accept_msg

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
