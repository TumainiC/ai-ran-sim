import json
import settings


class BaseStation:
    def __init__(self, simulation_engine=None, bs_id=None, position_x=0, position_y=0):
        self.simulation_engine = simulation_engine
        self.bs_id = bs_id
        self.position_x = position_x
        self.position_y = position_y

        self.ru_radius = settings.RAN_DEFAULT_RU_RADIUS
        self.max_prb = 100
        self.allocable_prb = 30
        self.allocated_prb = 0
        self.current_load = 0
        self.demanded_prb = 0
        self.connected_UE_list = set()
        self.served_UE_list = set()
        self.neighbour_BS_list = set()
        self.load_history = []

    
    def save_load_history(self):
        self.load_history.append(self.current_load)
        if len(self.load_history) > settings.RAN_BS_LOAD_HISTORY_LENGTH:
            self.load_history.pop(0)

    def update_current_load(self):
        self.demanded_prb = sum([ue.min_prb for ue in self.served_UE_list])
        self.current_load = self.allocated_prb / self.allocable_prb

    def serve_UE(self, ue):
        assert ue in self.connected_UE_list
        assert ue not in self.served_UE_list
        assert ue.allocated_prb == 0

        ue.served_by_BS = self
        ue.served_by_BS_history.append(self.bs_id)
        self.served_UE_list.add(ue)
        self.update_current_load()

    def to_json(self):
        return {
            "bs_id": self.bs_id,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "ru_radius": self.ru_radius,
            "max_prb": self.max_prb,
            "allocable_prb": self.allocable_prb,
            "allocated_prb": self.allocated_prb,
            "demanded_prb": self.demanded_prb,
            "current_load": self.current_load,
            "connected_UE_list": [ue.ue_id for ue in self.connected_UE_list],
            "served_UE_list": [ue.ue_id for ue in self.served_UE_list],
            "neighbour_BS_list": [bs.bs_id for bs in self.neighbour_BS_list],
        }

    def unserve_UE(self, ue):
        if ue in self.served_UE_list:
            self.served_UE_list.remove(ue)
            try:
                assert self.allocated_prb >= ue.allocated_prb
            except AssertionError as e:
                print(e)
                print(f"BS: {self.bs_id}, UE: {ue.ue_id}")
                print(
                    f"BS allocated prb: {self.allocated_prb}, UE allocated prb: {ue.allocated_prb}"
                )
                print(json.dumps(self.to_json(), indent=4))
                print(json.dumps(ue.to_json(), indent=4))
            # self.simulation_engine.logs.append(f"UE {ue.ue_id} is removed from RU {self.ru_id}")
            self.allocated_prb -= ue.allocated_prb
            self.update_current_load()

    def disconnect_UE(self, ue):
        if ue in self.connected_UE_list:
            self.connected_UE_list.remove(ue)

    def hand_over_policy(self):
        pass

    def prb_control_policy(self):
        pass

    def remove_UE(self, ue):
        self.unserve_UE(ue)
        self.disconnect_UE(ue)
