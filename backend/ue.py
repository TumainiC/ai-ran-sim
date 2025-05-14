import random

import numpy as np
from utils import (
    dist_between,
    get_rrc_measurement_event_monitor,
    dbm_to_watts,
    sinr_to_cqi,
)
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
        speed_mps=0,
        simulation_engine=None,
        connection_time=settings.UE_DEFAULT_TIMEOUT,
    ):
        self.ue_imsi = ue_imsi
        self.position_x = position_x
        self.position_y = position_y
        self.target_x = target_x
        self.target_y = target_y
        self.speed_mps = speed_mps
        self.time_ramaining = connection_time
        self.simulation_engine = simulation_engine

        self.slice_type = None
        self.qos_profile = None
        self.connected = False

        self.downlink_bitrate = 0
        self.downlink_latency = 0
        self.rrc_measurement_event_monitors = []
        self.downlink_received_power_dBm_dict = {}
        self.downlink_sinr = 0
        self.downlink_cqi = 0
        self.downlink_mcs_index = -1
        self.downlink_mcs_data = None

        self.uplink_bitrate = 0
        self.uplink_latency = 0
        self.uplink_transmit_power_dBm = settings.UE_TRANSMIT_POWER

        self.current_cell = None
        self.serving_cell_history = []

    def __repr__(self):
        return f"UE(ue_imsi={self.ue_imsi}, position=({self.position_x}, {self.position_y}), target=({self.target_x}, {self.target_y}), speed_mps={self.speed_mps}, current_cell={self.current_cell.cell_id if self.current_cell else None})"

    @property
    def dist_to_target(self):
        return dist_between(
            self.position_x,
            self.position_y,
            self.target_x,
            self.target_y,
        )

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
        cells_detected = list(self.downlink_received_power_dBm_dict.values())
        cells_detected.sort(
            key=lambda x: (
                x["frequency_priority"],
                x["received_power_with_cio_dBm"],
            ),
            reverse=True,
        )
        # Print all the detected SSBs in a pretty table
        table_data = [
            [
                v["cell"].cell_id,
                v["received_power_with_cio_dBm"],
                v["frequency_priority"],
            ]
            for v in cells_detected
        ]
        print(f"UE {self.ue_imsi}: Detected SSBs:")
        print(
            tabulate(
                table_data,
                headers=[
                    "Cell ID",
                    "Received Power With CIO (dBm)",
                    "Frequency Priority",
                ],
                tablefmt="grid",
            )
        )

        self.set_current_cell(cells_detected[0]["cell"])
        return True

    def setup_rrc_measurement_event_monitors(self, rrc_meas_events_to_monitor=[]):
        self.rrc_measurement_event_monitors = [
            get_rrc_measurement_event_monitor(event["event_id"], event_params=event)
            for event in rrc_meas_events_to_monitor
        ]

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
        self.setup_rrc_measurement_event_monitors(ue_reg_res["rrc_meas_events"])
        return True

    def power_up(self):
        print(f"UE {self.ue_imsi} Powering up")
        self.monitor_signal_strength()

        if len(list(self.downlink_received_power_dBm_dict.values())) == 0:
            print(f"UE {self.ue_imsi}: No cells detected. Powering down...")
            return False

        if not self.cell_selection_and_camping():
            print(f"UE {self.ue_imsi}: Cell selection and camping failed.")
            return False

        if not self.authenticate_and_register():
            print(f"UE {self.ue_imsi}: Authentication and registration failed.")
            return False

        self.connected = True

        return True

    def execute_handover(self, target_cell):
        # reset current cell data
        self.downlink_received_power_dBm_dict = {}
        self.downlink_sinr = 0
        self.downlink_cqi = 0
        self.downlink_mcs_index = -1
        self.downlink_mcs_data = None
        self.downlink_bitrate = 0
        self.downlink_latency = 0
        self.uplink_bitrate = 0
        self.uplink_latency = 0
        self.uplink_transmit_power_dBm = settings.UE_TRANSMIT_POWER
        self.set_current_cell(target_cell)

        for event_monitor in self.rrc_measurement_event_monitors:
            event_monitor.reset_trigger_history()

    def set_current_cell(self, cell):
        self.current_cell = cell

        if cell is None:
            if len(self.serving_cell_history) > 0:
                assert (
                    self.serving_cell_history[-1] is not None
                ), f"UE {self.ue_imsi} is not served by any cell."
            self.serving_cell_history.append(None)
        else:
            if len(self.serving_cell_history) > 0:
                assert (
                    self.serving_cell_history[-1] != cell.cell_id
                ), f"UE {self.ue_imsi} is already served by cell {cell.cell_id}."
            self.serving_cell_history.append(cell.cell_id)

        if len(self.serving_cell_history) > settings.UE_SERVING_CELL_HISTORY_LENGTH:
            self.serving_cell_history.pop(0)

    def deregister(self):
        print(f"UE {self.ue_imsi}: Sending deregistration request.")
        self.current_bs.handle_deregistration_request(self)
        self.set_current_cell(None)
        self.connected = False

    def move_towards_target(self, delta_time):
        if self.target_x is not None and self.target_y is not None:
            dist_to_target = self.dist_to_target
            max_move_dist = self.speed_mps * delta_time
            if dist_to_target <= max_move_dist:
                self.position_x = self.target_x
                self.position_y = self.target_y
            else:
                # move towards the target for the distance of max_move_dist, but round to nearest integer
                ratio = max_move_dist / dist_to_target
                self.position_x += (self.target_x - self.position_x) * ratio
                self.position_y += (self.target_y - self.position_y) * ratio
                self.position_x = round(self.position_x)
                self.position_y = round(self.position_y)

    def monitor_signal_strength(self):
        # monitors the downlink signal strength from the cells

        self.downlink_received_power_dBm_dict = {}
        self.downlink_sinr = 0
        self.downlink_cqi = 0

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

            received_power_dBm = cell.transmit_power_dBm - pass_loss_model(
                distance_m=distance, frequency_ghz=cell.carrier_frequency_MHz / 1000
            )
            received_power_with_cio_dBm = (
                received_power_dBm + cell.cell_individual_offset_dBm
            )
            if (
                received_power_dBm > settings.UE_SSB_DETECTION_THRESHOLD
                and received_power_dBm >= cell.qrx_level_min
            ):
                self.downlink_received_power_dBm_dict[cell.cell_id] = {
                    "cell": cell,
                    "received_power_dBm": received_power_dBm,
                    "frequency_priority": cell.frequency_priority,
                    "received_power_with_cio_dBm": received_power_with_cio_dBm,
                }
            elif self.current_cell and cell.cell_id == self.current_cell.cell_id:
                # make sure the current cell is in the list of detecte cells
                self.downlink_received_power_dBm_dict[cell.cell_id] = {
                    "cell": cell,
                    "received_power_dBm": settings.UE_SSB_DETECTION_THRESHOLD,
                    "frequency_priority": cell.frequency_priority,
                    "received_power_with_cio_dBm": settings.UE_SSB_DETECTION_THRESHOLD
                    + cell.cell_individual_offset_dBm,
                }

        self.calculate_SINR_and_CQI()

        return True

    def calculate_SINR_and_CQI(self):
        if self.current_cell is None:
            return False

        # make sure the current cell is in the list of detected cells
        power_data = self.downlink_received_power_dBm_dict.get(
            self.current_cell.cell_id, None
        )
        if power_data is None:
            current_cell_power_dBm = self.current_cell.qrx_level_min
        else:
            current_cell_power_dBm = power_data["received_power_dBm"]

        # calculate the SINR
        received_powers_w = np.array(
            [
                dbm_to_watts(cell_power_data["received_power_dBm"])
                for cell_power_data in self.downlink_received_power_dBm_dict.values()
                if cell_power_data["cell"].carrier_frequency_MHz
                == self.current_cell.carrier_frequency_MHz
            ]
        )

        # Serving cell is the one with max received power
        current_cell_power_w = dbm_to_watts(current_cell_power_dBm)
        interference_power_w = np.sum(received_powers_w) - current_cell_power_w

        # Thermal noise
        k = 1.38e-23  # Boltzmann constant
        noise_power_w = k * settings.UE_TEMPERATURE_K * self.current_cell.bandwidth_Hz

        # print(f"UE {self.ue_imsi}: Interference power (W):", interference_power_w)
        # print(f"UE {self.ue_imsi}: Noise power (W):", noise_power_w)
        # print(
        #     f"UE {self.ue_imsi}: Current cell received power: {current_cell_received_power} (dBm) = {current_cell_power_w} (W):"
        # )

        self.downlink_sinr = 10 * np.log10(
            current_cell_power_w / (interference_power_w + noise_power_w)
        )
        self.downlink_cqi = sinr_to_cqi(self.downlink_sinr)
        # print(
        #     f"UE {self.ue_imsi}: Downlink SINR: {self.downlink_sinr:.2f} dB, CQI: {self.downlink_cqi}"
        # )

    def check_rrc_meas_events_to_monitor(self):
        cell_signal_map = {
            v["cell"].cell_id: v["received_power_with_cio_dBm"]
            for v in self.downlink_received_power_dBm_dict.values()
        }
        for rrc_meas_event_trigger in self.rrc_measurement_event_monitors:
            rrc_meas_event_trigger.check(self, cell_signal_map.copy())
            if rrc_meas_event_trigger.is_triggered:
                print(
                    f"UE {self.ue_imsi}: RRC measurement event {rrc_meas_event_trigger.event_id} triggered."
                )
                event_report = rrc_meas_event_trigger.gen_event_report()
                print(f"{self} Reporting event: {event_report}")
                self.current_bs.receive_ue_rrc_meas_events(event_report)

    def step(self, delta_time):
        self.move_towards_target(delta_time)
        self.monitor_signal_strength()
        self.check_rrc_meas_events_to_monitor()
        self.time_ramaining -= delta_time
        if self.time_ramaining <= 0:
            self.deregister()

    def to_json(self):
        return {
            "ue_imsi": self.ue_imsi,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "vis_position_x": self.position_x * settings.REAL_LIFE_DISTANCE_MULTIPLIER,
            "vis_position_y": self.position_y * settings.REAL_LIFE_DISTANCE_MULTIPLIER,
            "target_x": self.target_x,
            "target_y": self.target_y,
            "vis_target_x": self.target_x * settings.REAL_LIFE_DISTANCE_MULTIPLIER,
            "vis_target_y": self.target_y * settings.REAL_LIFE_DISTANCE_MULTIPLIER,
            "speed_mps": self.speed_mps,
            "slice_type": self.slice_type,
            "qos_profile": self.qos_profile,
            "current_cell": self.current_cell.cell_id if self.current_cell else None,
            "current_bs": self.current_bs.bs_id if self.current_bs else None,
            "connected": self.connected,
            "time_ramaining": self.time_ramaining,
            "serving_cell_history": [cell_id for cell_id in self.serving_cell_history],
            "downlink_bitrate": self.downlink_bitrate,
            "downlink_latency": self.downlink_latency,
            "uplink_bitrate": self.uplink_bitrate,
            "uplink_latency": self.uplink_latency,
            "downlink_received_power_dBm_dict": {
                cell_id: {
                    "received_power_dBm": cell_data["received_power_dBm"],
                    "received_power_with_cio_dBm": cell_data[
                        "received_power_with_cio_dBm"
                    ],
                    "frequency_priority": cell_data["frequency_priority"],
                }
                for cell_id, cell_data in self.downlink_received_power_dBm_dict.items()
            },
            "downlink_sinr": self.downlink_sinr,
            "downlink_cqi": self.downlink_cqi,
            "downlink_mcs_index": self.downlink_mcs_index,
            "downlink_mcs_data": self.downlink_mcs_data,
        }
