from .xapp_base import xAppBase
from utils import xAppControlAction

class xAppHandoverControl(xAppBase):
    """
    xApp for Handover Control
    """
    def __init__(self, ric=None):
        super().__init__(ric=ric)
    
    def handle_rrc_meas_event_A3(self, event):
        # Handle the RRC measurement event A3
        # This is where you would implement the logic for handover control
        if "triggering_ue" not in event:
            print(f"{self.xapp_id}: RRC measurement event A3 does not contain triggering_ue")
            return None
        ue = event["triggering_ue"]
        if ue is None:
            print(f"{self.xapp_id}: RRC measurement event A3 does not contain triggering_ue")
            return None
        if not event["triggered"]:
            print(f"{self.xapp_id}: RRC measurement event A3 not triggered for UE {ue.ue_imsi}")
            return None
        
        print(f"{self.xapp_id}: Received RRC measurement event A3 for UE {ue.ue_imsi}")
        print(event)
        
        # blindly perform handover
        return xAppControlAction(
            action_type=xAppControlAction.ACTION_TYPE_HANDOVER,
            action_data={
                "ue": ue,
                "source_cell_id": event["current_cell_id"],
                "target_cell_id": event["best_neighbour_cell_id"],
            },
        )

    def start(self):
        # subcribe events from all base stations
        for bs in self.base_station_list.values():
            bs.init_rrc_measurement_event_handler("A3", self.handle_rrc_meas_event_A3)
