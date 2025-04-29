import math
import settings


class UE:
    def __init__(
        self,
        ue_id="UE_1",
        position_x=0,
        position_y=0,
        min_prb=10,
        connection_time=settings.UE_DEFAULT_TIMEOUT,
    ):
        self.ue_id = ue_id
        self.position_x = position_x
        self.position_y = position_y
        self.velocity_x = 0
        self.velocity_y = 0
        self.connected_RU_list = set()
        self.served_by_RU = None
        self.min_prb = min_prb
        self.allocated_prb = 0
        self.connected = False
        self.time_ramaining = connection_time
        self.dist_to_connected_RU_dict = {}
        self.served_by_RU_history = []

    def to_json(self):
        return {
            "ue_id": self.ue_id,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "velocity_x": self.velocity_x,
            "velocity_y": self.velocity_y,
            "connected_RU_list": [ru.ru_id for ru in self.connected_RU_list],
            "served_by_RU": self.served_by_RU.ru_id if self.served_by_RU else None,
            "min_prb": self.min_prb,
            "allocated_prb": self.allocated_prb,
            "connected": self.connected,
            "time_ramaining": self.time_ramaining,
            "dist_to_connected_RU_dict": self.dist_to_connected_RU_dict,
            "served_by_RU_history": [ru_id for ru_id in self.served_by_RU_history],
        }

    def dist_to(self, obj):
        return math.sqrt(
            (self.position_x - obj.position_x) ** 2
            + (self.position_y - obj.position_y) ** 2
        )
