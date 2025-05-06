import settings
from utils import dist_between


class Cell:
    def __init__(self, base_station, cell_init_data):
        assert base_station is not None, "Base station cannot be None"
        assert cell_init_data is not None, "Cell init data cannot be None"
        self.base_station = base_station

        self.cell_id = cell_init_data["cell_id"]
        self.frequency_band = cell_init_data["frequency_band"]
        self.carrier_frequency_MHz = cell_init_data["carrier_frequency_MHz"]
        self.bandwidth_Hz = cell_init_data["bandwidth_Hz"]
        self.max_prb = cell_init_data["max_prb"]
        self.max_dl_prb = cell_init_data["max_dl_prb"]
        self.max_ul_prb = cell_init_data["max_ul_prb"]
        self.cell_radius = cell_init_data["cell_radius"]
        self.transmit_power_dBm = cell_init_data["transmit_power_dBm"]
        self.cell_individual_offset_dBm = cell_init_data["cell_individual_offset_dBm"]
        self.frequency_priority = cell_init_data["frequency_priority"]
        self.qrx_level_min = cell_init_data["qrx_level_min"]

        self.prb_ue_allocation_dict = {}  # { "ue_ismi": {"downlink": 30, "uplink": 5}}
        self.connected_ue_list = {}
        self.ue_uplink_signal_strength_dict = {}

    @property
    def allocated_dl_prb(self):
        return sum(
            [
                self.prb_ue_allocation_dict[ue_ismi]["downlink"]
                for ue_ismi in self.connected_ue_list.keys()
            ]
        )

    @property
    def allocated_ul_prb(self):
        return sum(
            [
                self.prb_ue_allocation_dict[ue_ismi]["uplink"]
                for ue_ismi in self.connected_ue_list.keys()
            ]
        )

    @property
    def allocated_prb(self):
        return sum(
            [
                self.prb_ue_allocation_dict[ue_ismi]["uplink"]
                + self.prb_ue_allocation_dict[ue_ismi]["downlink"]
                for ue_ismi in self.connected_ue_list.keys()
            ]
        )

    @property
    def current_load(self):
        return self.allocated_prb / self.max_prb

    @property
    def position_x(self):
        return self.base_station.position_x

    @property
    def position_y(self):
        return self.base_station.position_y

    def register_ue(self, ue):
        self.connected_ue_list[ue.ue_imsi] = ue
        self.prb_ue_allocation_dict[ue.ue_imsi] = {
            "downlink": 0,
            "uplink": 0,
        }

    def get_ue_prb_allocation(self, ue):
        if ue.ue_imsi in self.prb_ue_allocation_dict:
            return (
                self.prb_ue_allocation_dict[ue.ue_imsi]["downlink"],
                self.prb_ue_allocation_dict[ue.ue_imsi]["uplink"],
            )
        else:
            return 0, 0

    def monitor_ue_signal_strength(self):
        self.ue_uplink_signal_strength_dict = {}
        pass_loss_model = settings.CHANNEL_PASS_LOSS_MODEL_MAP[
            settings.CHANNEL_PASS_LOSS_MODEL_URBAN_MACRO_NLOS
        ]
        # monitor the ue uplink signal strength
        for ue in self.connected_ue_list.values():
            # calculate the received power based on distance and transmit power
            distance = dist_between(
                self.position_x,
                self.position_y,
                ue.position_x,
                ue.position_y,
            )
            received_power = ue.uplink_transmit_power_dBm - pass_loss_model(
                distance_m=distance, frequency_ghz=self.carrier_frequency_MHz / 1000
            )
            self.ue_uplink_signal_strength_dict[ue.ue_imsi] = received_power

    def select_ue_mcs(self):
        for ue in self.connected_ue_list.values():
            ue.downlink_mcs_index = -1
            ue.downlink_mcs_data = None
            ue_cqi_mcs_data = settings.UE_CQI_MCS_SPECTRAL_EFFICIENCY_TABLE.get(
                ue.downlink_cqi, None
            )
            if ue.downlink_cqi == 0 or ue_cqi_mcs_data is None:
                continue

            ue_cqi_eff = ue_cqi_mcs_data["spectral_efficiency"]
            max_mcs_index = 0
            for (
                mcs_index,
                mcs_eff,
            ) in settings.RAN_MCS_SPECTRAL_EFFICIENCY_TABLE.items():
                if mcs_eff["spectral_efficiency"] <= ue_cqi_eff:
                    max_mcs_index = mcs_index
                else:
                    break
            print(
                f"Cell {self.cell_id}: UE {ue.ue_imsi} selected MCS index {max_mcs_index} based on CQI {ue.downlink_cqi}"
            )
            ue.downlink_mcs_index = max_mcs_index
            ue.downlink_mcs_data = settings.RAN_MCS_SPECTRAL_EFFICIENCY_TABLE.get(
                max_mcs_index, None
            ).copy()

    def step(self, delta_time):
        self.monitor_ue_signal_strength()

        # select modulation and coding scheme (MCS) for each UE based on CQI
        self.select_ue_mcs()

        # allocate PRBs dynamically based on each UE's QoS profile and channel conditions
        self.allocate_prb()

        # for each UE, estimate the downlink, uplink bitrate and latency
        self.estimate_ue_throughput_and_latency()

    def allocate_prb(self):
        # sample QoS and channel condition-aware PRB allocation
        self.prb_ue_allocation_dict = {}

        # Calculate a score for each UE
        dl_ue_scores = {}
        ul_ue_scores = {}
        dl_score_sum = 0
        ul_score_sum = 0
        for ue in self.connected_ue_list.values():
            # Better RSSI = lower dBm = higher score (invert it)
            if self.cell_id in ue.downlink_received_power_dBm_dict:
                dl_rssi_score = (
                    100
                    + ue.downlink_received_power_dBm_dict[self.cell_id][
                        "received_power_dBm"
                    ]
                )  # e.g., -70 -> 30
            else:
                dl_rssi_score = (
                    100 + self.qrx_level_min
                )  # Default to min level if not detected

            if ue.ue_imsi in self.ue_uplink_signal_strength_dict:
                ul_rssi_score = 100 + self.ue_uplink_signal_strength_dict[ue.ue_imsi]
            else:
                ul_rssi_score = 100 + self.qrx_level_min

            dl_qos_weight = ue.qos_profile["GBR_DL"] / 1e6  # Normalize for simplicity
            ul_qos_weight = ue.qos_profile["GBR_UL"] / 1e6

            # Add a small constant to avoid zero allocation
            dl_ue_scores[ue.ue_imsi] = dl_rssi_score * dl_qos_weight + 0.1
            ul_ue_scores[ue.ue_imsi] = ul_rssi_score * ul_qos_weight + 0.1

            dl_score_sum += dl_ue_scores[ue.ue_imsi]
            ul_score_sum += ul_ue_scores[ue.ue_imsi]

        # Normalize scores to allocate PRBs proportionally
        for ue_imsi in self.connected_ue_list.keys():
            self.prb_ue_allocation_dict[ue_imsi] = {
                "downlink": int(dl_ue_scores[ue_imsi] / dl_score_sum * self.max_dl_prb),
                "uplink": int(ul_ue_scores[ue_imsi] / ul_score_sum * self.max_ul_prb),
            }
            print(
                f"Cell {self.cell_id}: Allocated {self.prb_ue_allocation_dict[ue_imsi]['downlink']} DL PRBs and {self.prb_ue_allocation_dict[ue_imsi]['uplink']} UL PRBs to UE {ue_imsi}"
            )

    def estimate_ue_throughput_and_latency(self):
        # only downlink bitrate is supported for now.
        for ue in self.connected_ue_list.values():
            if ue.downlink_mcs_data is None:
                print(
                    f"Cell {self.cell_id}: UE {ue.ue_imsi} has no downlink MCS data. Skipping."
                )
                continue

            # Bits per RE (Resource Element)
            bits_per_symbol = (
                ue.downlink_mcs_data["modulation_order"]
                * ue.downlink_mcs_data["target_code_rate"]
                / 1024
            )

            # Bits per PRB per slot
            bits_per_prb_per_slot = (
                bits_per_symbol * settings.RAN_RESOURCE_ELEMENTS_PER_PRB_PER_SLOT
            )

            # DL & UL TBS estimates (bits per slot)
            estimated_tbs_dl = (
                self.prb_ue_allocation_dict[ue.ue_imsi]["downlink"]
                * bits_per_prb_per_slot
            )
            # estimated_tbs_ul = self.prb_ue_allocation_dict[ue.ue_ismi]["uplink"] * bits_per_prb_per_slot

            # If real TBS provided, use it
            tbs_dl = (
                ue.tbs_dl if hasattr(ue, "tbs_dl") and ue.tbs_dl else estimated_tbs_dl
            )
            # tbs_ul = (
            #     ue.tbs_ul if hasattr(ue, "tbs_ul") and ue.tbs_ul else estimated_tbs_ul
            # )

            # Throughput = bits per second
            ue.downlink_bitrate = tbs_dl / settings.RAN_SLOT_DURATION
            # ul_throughput = tbs_ul / settings.RAN_SLOT_DURATION

            # Latency = transmission time of one transport block (simplified)
            # dl_latency = settings.RAN_SLOT_DURATION * (
            #     1
            #     if self.prb_ue_allocation_dict[ue.ue_imsi]["downlink"] > 0
            #     else float("inf")
            # )
            # ul_latency = slot_duration * (1 if ue.ul_prb > 0 else float("inf"))

            print(f"Cell {self.cell_id}: UE {ue.ue_imsi} estimated downlink bitrate: {ue.downlink_bitrate:.2f} bps")

    def deregister_ue(self, ue):
        if ue.ue_imsi in self.prb_ue_allocation_dict:
            del self.prb_ue_allocation_dict[ue.ue_imsi]
            print(f"Cell {self.cell_id}: Released resources for UE {ue.ue_imsi}")
        else:
            print(f"Cell {self.cell_id}: No resources to release for UE {ue.ue_imsi}")

        if ue.ue_imsi in self.connected_ue_list:
            del self.connected_ue_list[ue.ue_imsi]
            print(f"Cell {self.cell_id}: Deregistered UE {ue.ue_imsi}")
        else:
            print(f"Cell {self.cell_id}: No UE {ue.ue_imsi} to deregister")

    def to_json(self):
        return {
            "cell_id": self.cell_id,
            "frequency_band": self.frequency_band,
            "carrier_frequency_MHz": self.carrier_frequency_MHz,
            "bandwidth_Hz": self.bandwidth_Hz,
            "max_prb": self.max_prb,
            "cell_radius": self.cell_radius,
            "vis_cell_radius": self.cell_radius * settings.REAL_LIFE_DISTANCE_MULTIPLIER,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "vis_position_x": self.position_x * settings.REAL_LIFE_DISTANCE_MULTIPLIER,
            "vis_position_y": self.position_y * settings.REAL_LIFE_DISTANCE_MULTIPLIER,
            "prb_ue_allocation_dict": self.prb_ue_allocation_dict,
            "allocated_prb": self.allocated_prb,
            "current_load": self.current_load,
            "connected_ue_list": list(self.connected_ue_list.keys()),
        }


class BaseStation:
    def __init__(self, simulation_engine, bs_init_data):
        assert simulation_engine is not None, "Simulation engine cannot be None"
        assert bs_init_data is not None, "Base station init data cannot be None"

        self.simulation_engine = simulation_engine
        self.core_network = simulation_engine.core_network

        self.bs_id = bs_init_data["bs_id"]
        self.position_x = bs_init_data["position_x"]
        self.position_y = bs_init_data["position_y"]
        self.cell_list = [
            Cell(
                base_station=self,
                cell_init_data=cell_init_data,
            )
            for cell_init_data in bs_init_data["cell_list"]
        ]
        self.rrc_measurement_events = bs_init_data["rrc_measurement_events"]

        self.ue_registry = {}
        self.ue_rrc_meas_events = []
        self.ue_rrc_meas_event_handers = {}

    def receive_ue_rrc_meas_events(self, ue, event):
        self.ue_rrc_meas_events.append((ue, event))

    def handle_ue_authentication_and_registration(self, ue, ue_auth_reg_msg):
        core_response = self.core_network.handle_ue_authentication_and_registration(
            ue, ue_auth_reg_msg
        )
        ue_reg_data = {
            "ue": ue,
            "slice_type": core_response["slice_type"],
            "qos_profile": core_response["qos_profile"],
            "cell": ue.current_cell,
            "rrc_meas_events": self.rrc_measurement_events.copy(),
        }
        self.ue_registry[ue.ue_imsi] = ue_reg_data
        ue.current_cell.register_ue(ue)
        return ue_reg_data.copy()

    def handle_deregistration_request(self, ue):
        self.core_network.handle_deregistration_request(ue)
        # for simplicity, gNB directly releases resources instead of having AMF to initiate the release
        ue.current_cell.deregister_ue(ue)
        if ue.ue_imsi in self.ue_registry:
            del self.ue_registry[ue.ue_imsi]
        print(f"gNB {self.bs_id}: UE {ue.ue_imsi} deregistered and resources released.")
        return True

    def save_load_history(self):
        self.load_history.append(self.current_load)
        if len(self.load_history) > settings.RAN_BS_LOAD_HISTORY_LENGTH:
            self.load_history.pop(0)

    def to_json(self):
        return {
            "bs_id": self.bs_id,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "vis_position_x": self.position_x * settings.REAL_LIFE_DISTANCE_MULTIPLIER,
            "vis_position_y": self.position_y * settings.REAL_LIFE_DISTANCE_MULTIPLIER,
            "ue_registry": list(self.ue_registry.keys()),
            "cell_list": [cell.to_json() for cell in self.cell_list],
        }

    def init_rrc_measurement_event_handler(self, event_id, handler):
        assert event_id is not None, "Event ID cannot be None"
        assert handler is not None, "Handler cannot be None"
        assert (
            event_id not in self.ue_rrc_meas_event_handers
        ), f"Handler for event ID {event_id} already registered"
        self.ue_rrc_meas_event_handers[event_id] = handler

    def step(self, delta_time):
        # first update cell first
        for cell in self.cell_list:
            cell.step(delta_time)

        # process RRC measurement events
        while len(self.ue_rrc_meas_events) > 0:
            ue, event = self.ue_rrc_meas_events.pop(0)
            event_id = event["event_id"]
            if event_id not in self.ue_rrc_meas_event_handers:
                print(
                    f"gNB {self.bs_id}: No handler for event ID {event_id}. Skipping."
                )
                continue
            handler = self.ue_rrc_meas_event_handers[event_id]
            handler(ue, event)
            print(
                f"gNB {self.bs_id}: Processed RRC measurement event {event_id} for UE {ue.ue_imsi}"
            )
