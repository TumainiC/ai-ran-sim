from .xapp_base import xAppBase
from utils import xAppControlAction

class xAppA3HandoverWithFreqPriority(xAppBase):
    """
    xApp that performs handover only when 
        the target cell has a equal or higher frequency priority than the source cell.
    or
        the received signal strength of the current cell is at its minimum threshold 
        (which indicates that the UE is probably out of the current cell)
    """
    def __init__(self, ric=None):
        super().__init__(ric=ric)
        self.enabled = True
    
    def handle_rrc_meas_event_A3(self, event):
        if not event["triggered"]:
            print(f"{self.xapp_id}: RRC measurement event A3 not triggered for UE {ue.ue_imsi}")
            return None
        
        ue = event["triggering_ue"]
        current_cell = self.cell_list[event["current_cell_id"]]
        target_cell = self.cell_list[event["best_neighbour_cell_id"]]

        assert ue is not None, f"triggering_ue {event['triggering_ue']} not found"
        assert current_cell is not None, f"current_cell {event['current_cell_id']} not found"
        assert target_cell is not None, f"target_cell {event['best_neighbour_cell_id']} not found"
        assert current_cell.cell_id != target_cell.cell_id, f"current_cell {event['current_cell_id']} is the same as target_cell {event['best_neighbour_cell_id']}"
        
        print(f"{self.xapp_id}: Received RRC measurement event A3 for UE {ue.ue_imsi}")
        print(event)
        current_cell = ue.current_cell

        if event["current_cell_signal_power"] <= current_cell.qrx_level_min:
            # the received signal strength of the current cell is at its minimum threshold
            print(f"{self.xapp_id}: Received signal strength of the current cell is at its minimum threshold")
            # blindly perform handover
            return xAppControlAction(
                action_type=xAppControlAction.ACTION_TYPE_HANDOVER,
                action_data={
                    "ue": ue,
                    "source_cell_id": event["current_cell_id"],
                    "target_cell_id": event["best_neighbour_cell_id"],
                },
            )
        elif target_cell.frequency_priority >= current_cell.frequency_priority:
            # the target cell has a equal or higher frequency priority than the source cell
            print(f"{self.xapp_id}: Target cell has a equal or higher frequency priority than the source cell")
            # blindly perform handover
            return xAppControlAction(
                action_type=xAppControlAction.ACTION_TYPE_HANDOVER,
                action_data={
                    "ue": ue,
                    "source_cell_id": event["current_cell_id"],
                    "target_cell_id": event["best_neighbour_cell_id"],
                },
            )

        return None

    def start(self):
        if not self.enabled:
            print(f"{self.xapp_id}: xApp is not enabled")
            return
        # subcribe events from all base stations
        for bs in self.base_station_list.values():
            bs.init_rrc_measurement_event_handler("A3", self.handle_rrc_meas_event_A3)
