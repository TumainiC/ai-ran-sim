from utils import dist_between, get_pass_loss_model
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

        # channel quality data
        self.bs_rsrp_list = {}

        self.slice_info = None
        self.qos_profile = None
        self.connected = False
        self.bitrate = {"downlink": 0, "uplink": 0}
        self.latency = 0

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

    def cell_search_and_synchronization(self):
        # cell search and synchronization
        # Synchronization Signal Block (SSB) detection
        SSBs_detected = []
        pass_loss_model = get_pass_loss_model(settings.CHANNEL_PASS_LOSS_MODEL)
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
                cell.transmit_power
                - pass_loss_model(
                    distance_m=distance, frequency_in_ghz=cell.carrier_frequency / 1000
                )
                + cell.cell_individual_offset
            )
            if (
                received_power > settings.UE_SSB_DETECTION_THRESHOLD
                and received_power >= cell.qrx_level_min
            ):
                SSBs_detected.append(
                    {
                        "cell": cell,
                        "received_power": received_power,
                        "frequency_priority": cell.frequency_priority,
                    }
                )

        # print(
        #     f"UE {self.ue_imsi}: Detected SSBs: {[cell['cell'].cell_id for cell in SSBs_detected]}"
        # )

        return SSBs_detected

    def cell_selection_and_camping(self, SSBs_detected):
        # Sort SSBs by received power
        # first sort by frequency priority, then by received power (both the higher the better)
        # SSBs_detected.sort(key=lambda x: x["received_power"], reverse=True)
        SSBs_detected.sort(
            key=lambda x: (
                x["frequency_priority"],
                x["received_power"],
            ),
            reverse=True,
        )
        # Print all the detected SSBs in a pretty table
        table_data = [
            [ssb["cell"].cell_id, ssb["received_power"], ssb["frequency_priority"]]
            for ssb in SSBs_detected
        ]
        print(f"UE {self.ue_imsi}: Detected SSBs:")
        print(
            tabulate(
                table_data,
                headers=["Cell ID", "Received Power (dBm)", "Frequency Priority"],
                tablefmt="grid",
            )
        )

        # Select the best SSB
        self.current_cell = SSBs_detected[0]["cell"]
        return True

    def random_access_procedure(self):
        random_access_preamble = {}
        random_access_response = self.current_bs.handle_random_access(
            self, random_access_preamble
        )
        return True

    def request_RRC_connection(self):
        rrc_connection_request = {
            "ue_imsi": self.ue_imsi,
            "establishment_cause": settings.RAN_RRC_CONNECTION_EST_CAUSE_MO_SIGNALLING,
        }
        rrc_connection_response = self.current_bs.handle_RRC_connection_request(
            self, rrc_connection_request
        )
        return True

    def complete_RRC_connection_and_register(self):
        rrc_message = {
            "rrc": "Connection Setup Complete",
            "nas": {
                "ue": self,
                "registration_type": settings.RAN_RRC_REGISTERATION_TYPE_INITIAL,
                "capabilities": {},
            },
        }
        amf_authentication_request = (
            self.current_bs.handle_RRC_connection_complete_and_register(
                self, rrc_message
            )
        )

        authentication_response = {}
        security_mode_command_msg = self.current_bs.handle_authentication_response(
            self, authentication_response
        )

        security_mode_complete_msg = {}
        registration_accept_msg = self.current_bs.handle_security_mode_complete_msg(
            self, security_mode_complete_msg
        )
        self.slice_info = registration_accept_msg["slice_info"]
        self.qos_profile = registration_accept_msg["qos_profile"]

        registration_complete_msg = {}
        self.current_bs.handle_registration_complete_msg(
            self, registration_complete_msg
        )

        return True

    def test_network_performance(self):
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

    def power_up(self):
        print(f"UE {self.ue_imsi} Powering up")
        SSBs_detected = self.cell_search_and_synchronization()
        if len(SSBs_detected) == 0:
            print(f"UE {self.ue_imsi}: No SSB detected. Powering down...")
            return False
        if not self.cell_selection_and_camping(SSBs_detected):
            print(f"UE {self.ue_imsi}: Cell selection and camping failed.")
            return False

        if not self.random_access_procedure():
            print(f"UE {self.ue_imsi}: Random access procedure failed.")
            return False

        if not self.request_RRC_connection():
            print(f"UE {self.ue_imsi}: RRC connection request failed.")
            return False

        if not self.complete_RRC_connection_and_register():
            print(
                f"UE {self.ue_imsi}: RRC connection complete and registration failed."
            )
            return False

        if not self.test_network_performance():
            print(f"UE {self.ue_imsi}: Network performance test failed.")
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
        # self.estimate_rsrp_from_all_bs()

        # update the time remaining for the UE
        self.time_ramaining -= delta_time

        if self.time_ramaining <= 0:
            self.deregister(self.current_cell)

    def to_json(self):
        return {
            "ue_imsi": self.ue_imsi,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "target_x": self.target_x,
            "target_y": self.target_y,
            "speed": self.speed,
            "slice_info": self.slice_info,
            "qos_profile": self.qos_profile,
            "bitrate": self.bitrate,
            "latency": self.latency,
            "current_cell": self.current_cell.cell_id if self.current_cell else None,
            "current_bs": self.current_bs.bs_id if self.current_bs else None,
            "connected": self.connected,
            "time_ramaining": self.time_ramaining,
            "serving_cell_history": [cell_id for cell_id in self.serving_cell_history],
        }
