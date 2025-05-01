import math
from utils import dist_between
import settings


class UE:
    def __init__(
        self,
        ue_imsi="IMSI_1",
        position_x=0,
        position_y=0,
        target_x=0,
        target_y=0,
        speed=0,
        simulation_engine=None,
        connection_time=settings.UE_DEFAULT_TIMEOUT,
    ):
        self.ue_imsi = ue_imsi
        self.position_x = position_x
        self.position_y = position_y
        self.target_x = target_x
        self.target_y = target_y
        self.dist_to_target = dist_between(
            self.position_x,
            self.position_y,
            self.target_x,
            self.target_y,
        )
        self.speed = speed
        self.time_ramaining = connection_time
        self.simulation_engine = simulation_engine

        # channel quality data
        self.bs_rsrp_list = {}

        self.slice = None
        self.qos_profile = None
        self.connected = False
        self.bitrate = {"downlink": 0, "uplink": 0}
        self.latency = 0

        self.reachable_BS_list = set()
        self.served_by_BS = None

        self.dist_to_reachable_BS_dict = {}
        self.history_of_serving_BS = []

        self.estimate_rsrp_from_all_bs()

    @property
    def target_reached(self):
        return self.dist_to_target == 0
    
    @property
    def need_handover(self):
        # check if the rsrp by the current serving BS is less than the rsrp by the other BSs
        # if the UE is not connected to any BS, return False
        if self.served_by_BS is None:
            return False
        if len(self.bs_rsrp_list) == 0:
            return False
        if self.served_by_BS.cell_id not in self.bs_rsrp_list:
            return False
        current_rsrp = self.bs_rsrp_list[self.served_by_BS.cell_id]
        for cell_id, rsrp in self.bs_rsrp_list.items():
            if cell_id != self.served_by_BS.cell_id and rsrp > current_rsrp:
                return True
        return False
        

    def register(self, base_station = None):
        if base_station is None:
            # select the best base station based on RSRP
            cell_id = self.select_best_bs()
            if cell_id is None:
                print(f"UE {self.ue_imsi}: No base station available for registration.")
                return None
            base_station = self.simulation_engine.base_station_list[cell_id]
            if base_station is None:
                print(f"UE {self.ue_imsi}: Base station {cell_id} not found.")
                return None

        print(f"UE {self.ue_imsi}: Initiating registration...")
        slice_info, ue_qos_profile, dl_bitrate, ul_bitrate, latency = (
            base_station.handle_registration(self)
        )
        self.slice = slice_info
        self.qos_profile = ue_qos_profile
        self.bitrate["downlink"] = dl_bitrate
        self.bitrate["uplink"] = ul_bitrate
        self.latency = latency
        self.connected = True
        self.served_by_BS = base_station
        self.update_BS_history(base_station)

    def update_BS_history(self, base_station):
        if len(self.history_of_serving_BS) > 0:
            assert (
                base_station.cell_id != self.history_of_serving_BS[-1]
            ), f"UE {self.ue_imsi} is already served by BS {self.history_of_serving_BS[-1]}."
        self.history_of_serving_BS.append(base_station.cell_id)
        if len(self.history_of_serving_BS) > settings.UE_SERVING_BS_HISTORY_LENGTH:
            self.history_of_serving_BS.pop(0)

    def calculate_rsrq(self, base_station):
        # **RSRQ** (Reference Signal Received Quality)
        # not implemented yet
        pass

    def calculate_sinr(self, base_station):
        # **SINR** (Signal-to-Interference-plus-Noise Ratio)
        # not implemented yet
        pass

    def calculate_rsrp(
        self, base_station, path_loss_exponent=settings.CHANNEL_PATH_LOSS_EXPONENT
    ):
        # **RSRP** (Reference Signal Received Power)
        distance = dist_between(
            self.position_x,
            self.position_y,
            base_station.position_x,
            base_station.position_y,
        )
        if distance == 0:
            path_loss_db = settings.CHANNEL_REFERENCE_PASS_LOSS
        else:
            path_loss_db = (
                settings.CHANNEL_REFERENCE_PASS_LOSS
                + 10
                * path_loss_exponent
                * math.log10(distance / settings.CHANNEL_PASS_LOSS_REF_DISTANCE)
            )
        rsrp = settings.RAN_BS_REF_SIGNAL_DEFAULT_TRASNMIT_POWER - path_loss_db  # in dBm
        return rsrp

    def estimate_rsrp_from_all_bs(self):
        for bs in self.simulation_engine.base_station_list.values():
            rsrp = self.calculate_rsrp(bs)
            self.bs_rsrp_list[bs.cell_id] = rsrp
            # print("UE {}: RSRP from BS {}: {} dB".format(self.ue_imsi, bs.cell_id, rsrp))

    def select_best_bs(self):
        cell_id_selected = None
        max_rsrp = -math.inf
        for cell_id, rsrp in self.bs_rsrp_list.items():
            if rsrp > max_rsrp:
                max_rsrp = rsrp
                cell_id_selected = cell_id
        return cell_id_selected


    def deregister(self, base_station):
        print(f"UE {self.ue_imsi}: Sending deregistration request.")
        base_station.handle_deregistration(self)
        self.connected = False

    def move_towards_target(self, delta_time):
        if self.target_x is not None and self.target_y is not None:
            self.dist_to_target = dist_between(
                self.position_x,
                self.position_y,
                self.target_x,
                self.target_y,
            )
            max_move_dist = self.speed * delta_time
            if self.dist_to_target <= max_move_dist:
                self.position_x = self.target_x
                self.position_y = self.target_y
            else:
                # move towards the target for the distance of max_move_dist, but round to nearest integer
                ratio = max_move_dist / self.dist_to_target
                self.position_x += (self.target_x - self.position_x) * ratio
                self.position_y += (self.target_y - self.position_y) * ratio
                self.position_x = round(self.position_x)
                self.position_y = round(self.position_y)

            self.dist_to_target = dist_between(
                self.position_x,
                self.position_y,
                self.target_x,
                self.target_y,
            )

    def step(self, delta_time):
        # move the UE towards the target position
        self.move_towards_target(delta_time)
        
        # update the rsrp in every step
        self.estimate_rsrp_from_all_bs()

        # update the time remaining for the UE
        self.time_ramaining -= delta_time

        if self.time_ramaining <= 0:
            self.deregister(self.served_by_BS)

    def to_json(self):
        return {
            "ue_imsi": self.ue_imsi,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "target_x": self.target_x,
            "target_y": self.target_y,
            "speed": self.speed,
            "slice": self.slice,
            "qos_profile": self.qos_profile,
            "bitrate": self.bitrate,
            "latency": self.latency,
            "served_by_BS": self.served_by_BS.cell_id if self.served_by_BS else None,
            "connected": self.connected,
            "need_handover": self.need_handover,
            "time_ramaining": self.time_ramaining,
            "history_of_serving_BS": [cell_id for cell_id in self.history_of_serving_BS],
        }
