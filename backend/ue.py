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

        self.slice = None
        self.qos_profile = None
        self.connected = False
        self.bitrate = {"downlink": 0, "uplink": 0}
        self.latency = 0

        self.reachable_BS_list = set()
        self.served_by_BS = None

        self.dist_to_reachable_BS_dict = {}
        self.history_of_serving_BS = []

    @property
    def target_reached(self):
        return self.dist_to_target == 0

    def register(self, base_station):
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
                base_station.bs_id != self.history_of_serving_BS[-1]
            ), f"UE {self.ue_imsi} is already served by BS {self.history_of_serving_BS[-1]}."
        self.history_of_serving_BS.append(base_station.bs_id)
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
            return (
                base_station.ref_signal_transmit_power
            )  # No path loss at the same location
        path_loss_db = 10 * path_loss_exponent * math.log10(distance)
        rsrp = base_station.ref_signal_transmit_power - path_loss_db  # in dBm
        return rsrp

    def select_best_bs(self, base_station_list):
        candidates = []
        for bs in base_station_list:
            rsrp = self.calculate_rsrp(bs)
            print("UE {}: RSRP from BS {}: {} dB".format(self.ue_imsi, bs.bs_id, rsrp))
            if rsrp > -110:  # Acceptable signal strength
                candidates.append((bs, rsrp))
        if not candidates:
            return None
        # Sort by RSRP only.
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]  # Best gNB

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
            "served_by_BS": self.served_by_BS.bs_id if self.served_by_BS else None,
            "connected": self.connected,
            "time_ramaining": self.time_ramaining,
            "history_of_serving_BS": [bs_id for bs_id in self.history_of_serving_BS],
        }
