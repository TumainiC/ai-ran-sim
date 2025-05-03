import random
from utils import dist_between, get_rrc_measurement_event_trigger
from tabulate import tabulate

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

        self.slice_type = None
        self.qos_profile = None
        self.connected = False
        self.bitrate = {"downlink": 0, "uplink": 0}
        self.latency = 0
        self.rrc_measurement_event_triggers = []
        self.live_signal_strength_dict = {}

        self.reachable_BS_list = set()
        self.current_cell = None

        self.dist_to_reachable_BS_dict = {}
        self.serving_cell_history = []

    @property
    def current_bs(self):
        if self.current_cell is None:
            return None
        return self.current_cell.base_station

    @property
    def target_reached(self):
        return self.dist_to_target == 0

    def cell_selection_and_camping(self):
        # Sort SSBs by received power
        # first sort by frequency priority, then by received power (both the higher the better)
        # SSBs_detected.sort(key=lambda x: x["received_power"], reverse=True)
        cells_detected = list(self.live_signal_strength_dict.values())

        cells_detected.sort(
            key=lambda x: (
                x["frequency_priority"],
                x["received_power"],
            ),
            reverse=True,
        )
        # Print all the detected SSBs in a pretty table
        table_data = [
            [v["cell"].cell_id, v["received_power"], v["frequency_priority"]]
            for v in cells_detected
        ]
        print(f"UE {self.ue_imsi}: Detected SSBs:")
        print(
            tabulate(
                table_data,
                headers=["Cell ID", "Received Power (dBm)", "Frequency Priority"],
                tablefmt="grid",
            )
        )

        self.current_cell = cells_detected[0]["cell"]
        return True

    def setup_rrc_measurement_event_triggers(self, rrc_measurement_events=[]):
        self.rrc_measurement_event_triggers = [
            get_rrc_measurement_event_trigger(event["event_id"], event_params=event)
            for event in rrc_measurement_events
        ]

    def monitor_network_performance(self):
        dl_bitrate, ul_bitrate, latency = (
            self.current_cell.estimate_bitrate_and_latency(
                self.current_cell.get_ue_prb_allocation(self), self.qos_profile
            )
        )
        self.bitrate["downlink"] = dl_bitrate
        self.bitrate["uplink"] = ul_bitrate
        self.latency = latency
        print(
            f"UE {self.ue_imsi}: Network performance - Downlink: {dl_bitrate} bps, Uplink: {ul_bitrate} bps, Latency: {latency} ms"
        )
        return True

    def authenticate_and_register(self):
        # simplified one step authentication and registration implementation
        random_slice_type = random.choice(list(settings.NETWORK_SLICES.keys()))
        registration_msg = {
            "ue": self,
            "slice_type": random_slice_type,
            "qos_profile": settings.NETWORK_SLICES[random_slice_type].copy(),
        }
        ue_reg_res = self.current_bs.handle_ue_authentication_and_registration(
            self, registration_msg
        )
        self.slice_type = ue_reg_res["slice_type"]
        self.qos_profile = ue_reg_res["qos_profile"]
        self.setup_rrc_measurement_event_triggers(ue_reg_res["rrc_meas_events"])
        return True

    def power_up(self):
        print(f"UE {self.ue_imsi} Powering up")
        self.monitor_signal_strength()

        if len(list(self.live_signal_strength_dict.values())) == 0:
            print(f"UE {self.ue_imsi}: No cells detected. Powering down...")
            return False
        
        if not self.cell_selection_and_camping():
            print(f"UE {self.ue_imsi}: Cell selection and camping failed.")
            return False

        if not self.authenticate_and_register():
            print(f"UE {self.ue_imsi}: Authentication and registration failed.")
            return False

        self.connected = True
        self.update_cell_history()

        return True

    def update_cell_history(self):
        if self.current_cell is None:
            print(f"UE {self.ue_imsi}: No current cell to update history.")
            return
        if len(self.serving_cell_history) > 0:
            assert (
                self.current_cell.cell_id != self.serving_cell_history[-1]
            ), f"UE {self.ue_imsi} is already served by cell {self.serving_cell_history[-1]}."
        self.serving_cell_history.append(self.current_cell.cell_id)
        if len(self.serving_cell_history) > settings.UE_SERVING_CELL_HISTORY_LENGTH:
            self.serving_cell_history.pop(0)

    def deregister(self):
        print(f"UE {self.ue_imsi}: Sending deregistration request.")
        self.current_bs.handle_deregistration_request(self)
        self.current_cell = None
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

    def monitor_signal_strength(self):
        self.live_signal_strength_dict = {}
        pass_loss_model = settings.CHANNEL_PASS_LOSS_MODEL_MAP[
            settings.CHANNEL_PASS_LOSS_MODEL_URBAN_MACRO_NLOS
        ]
        for cell in self.simulation_engine.cell_list.values():
            # Check if the cell is within the UE's range
            distance = dist_between(
                self.position_x,
                self.position_y,
                cell.position_x,
                cell.position_y,
            )

            distance *= settings.REAL_LIFE_DISTANCE_MULTIPLIER

            received_power = (
                cell.transmit_power_dBm
                - pass_loss_model(
                    distance_m=distance, frequency_ghz=cell.carrier_frequency / 1000
                )
                + cell.cell_individual_offset_dBm
            )
            if (
                received_power > settings.UE_SSB_DETECTION_THRESHOLD
                and received_power >= cell.qrx_level_min
            ):
                self.live_signal_strength_dict[cell.cell_id] = {
                    "cell": cell,
                    "received_power": received_power,
                    "frequency_priority": cell.frequency_priority,
                }

        return True

    def check_rrc_measurement_events(self):
        cell_signal_map = {
            v["cell"].cell_id: v["received_power"]
            for v in self.live_signal_strength_dict.values()
        }
        for rrc_meas_event_trigger in self.rrc_measurement_event_triggers:
            rrc_meas_event_trigger.check(self, cell_signal_map.copy())
            if rrc_meas_event_trigger.is_triggered:
                print(
                    f"UE {self.ue_imsi}: RRC measurement event {rrc_meas_event_trigger.event_id} triggered."
                )
                self.current_bs.receive_ue_rrc_meas_events(
                    self, rrc_meas_event_trigger.gen_event_report()
                )

    def step(self, delta_time):
        self.move_towards_target(delta_time)
        self.monitor_signal_strength()
        self.check_rrc_measurement_events()
        self.time_ramaining -= delta_time
        if self.time_ramaining <= 0:
            self.deregister()

    def to_json(self):
        return {
            "ue_imsi": self.ue_imsi,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "target_x": self.target_x,
            "target_y": self.target_y,
            "speed": self.speed,
            "slice_type": self.slice_type,
            "qos_profile": self.qos_profile,
            "bitrate": self.bitrate,
            "latency": self.latency,
            "current_cell": self.current_cell.cell_id if self.current_cell else None,
            "current_bs": self.current_bs.bs_id if self.current_bs else None,
            "connected": self.connected,
            "time_ramaining": self.time_ramaining,
            "serving_cell_history": [cell_id for cell_id in self.serving_cell_history],
        }
