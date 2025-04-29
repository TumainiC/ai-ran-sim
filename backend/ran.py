import json
import math
import settings

class RU:
    def __init__(
        self,
        simulation_engine=None,
        ru_id="RU_1",
        position_x=0,
        position_y=0,
        radius=settings.RAN_DEFAULT_RU_RADIUS,
    ):
        self.simulation_engine = simulation_engine
        self.ru_id = ru_id
        self.position_x = position_x
        self.position_y = position_y
        self.radius = radius
        self.max_prb = 100
        self.allocable_prb = 30
        self.allocated_prb = 0
        self.current_load = 0
        self.demanded_prb = 0
        self.connected_UE_list = set()
        self.served_UE_list = set()
        self.neighbour_RU_list = set()
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

        ue.served_by_RU = self
        ue.served_by_RU_history.append(self.ru_id)
        self.served_UE_list.add(ue)
        self.update_current_load()

    def to_json(self):
        return {
            "ru_id": self.ru_id,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "radius": self.radius,
            "max_prb": self.max_prb,
            "allocable_prb": self.allocable_prb,
            "allocated_prb": self.allocated_prb,
            "demanded_prb": self.demanded_prb,
            "current_load": self.current_load,
            "connected_UE_list": [ue.ue_id for ue in self.connected_UE_list],
            "served_UE_list": [ue.ue_id for ue in self.served_UE_list],
            "neighbour_RU_list": [ru.ru_id for ru in self.neighbour_RU_list],
        }

    def unserve_UE(self, ue):
        if ue in self.served_UE_list:
            self.served_UE_list.remove(ue)
            try:
                assert self.allocated_prb >= ue.allocated_prb
            except AssertionError as e:
                print(e)
                print(f"RU: {self.ru_id}, UE: {ue.ue_id}")
                print(
                    f"RU allocated prb: {self.allocated_prb}, UE allocated prb: {ue.allocated_prb}"
                )
                print(json.dumps(self.to_json(), indent=4))
                print(json.dumps(ue.to_json(), indent=4))
            # self.simulation_engine.logs.append(f"UE {ue.ue_id} is removed from RU {self.ru_id}")
            self.allocated_prb -= ue.allocated_prb
            self.update_current_load()

    def disconnect_UE(self, ue):
        if ue in self.connected_UE_list:
            self.connected_UE_list.remove(ue)

    def dist_to(self, obj):
        return math.sqrt(
            (self.position_x - obj.position_x) ** 2
            + (self.position_y - obj.position_y) ** 2
        )


class BaseStation:
    def __init__(self, simulation_engine=None):
        self.simulation_engine = simulation_engine
        self.RU_list = set()

    def hand_over_policy(self):
        pass

    def prb_control_policy(self):
        pass

    def to_json(self):
        return {
            "RU_list": [ru.to_json() for ru in self.RU_list],
        }

    def init_RU_list(self, ru_data_list):
        for i, ru_data in enumerate(ru_data_list):
            ru = RU(
                simulation_engine=self.simulation_engine,
                ru_id=ru_data[0],
                position_x=ru_data[1],
                position_y=ru_data[2],
            )
            self.RU_list.add(ru)

        # update neighbour RU list
        for i, ru in enumerate(self.RU_list):
            for j, neighbour_ru in enumerate(self.RU_list):
                if i != j:
                    dist = ru.dist_to(neighbour_ru)
                    if dist <= 2 * ru.radius:
                        ru.neighbour_RU_list.add(neighbour_ru)
                        neighbour_ru.neighbour_RU_list.add(ru)

    def remove_UE(self, ue):
        for ru in self.RU_list:
            ru.unserve_UE(ue)
            ru.disconnect_UE(ue)
