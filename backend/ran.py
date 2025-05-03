import random
import settings
from utils import normalize


class Cell:
    def __init__(self, base_station, cell_init_data):
        assert base_station is not None, "Base station cannot be None"
        assert cell_init_data is not None, "Cell init data cannot be None"
        self.base_station = base_station

        self.cell_id = cell_init_data["cell_id"]
        self.frequency_band = cell_init_data["frequency_band"]
        self.carrier_frequency = cell_init_data["carrier_frequency"]
        self.bandwidth = cell_init_data["bandwidth"]
        self.max_prb = cell_init_data["max_prb"]
        self.cell_radius = cell_init_data["cell_radius"]
        self.transmit_power_dBm = cell_init_data["transmit_power_dBm"]
        self.cell_individual_offset_dBm = cell_init_data["cell_individual_offset_dBm"]
        self.frequency_priority = cell_init_data["frequency_priority"]
        self.qrx_level_min = cell_init_data["qrx_level_min"]

        self.prb_ue_allocation_dict = {}
        self.connected_ue_list = {}
    
    @property
    def allocated_prb(self):
        return sum(self.prb_ue_allocation_dict.values())

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
        self.prb_ue_allocation_dict[ue.ue_imsi] = 0

    def get_ue_prb_allocation(self, ue):
        if ue.ue_imsi in self.prb_ue_allocation_dict:
            return self.prb_ue_allocation_dict[ue.ue_imsi]
        else:
            return 0
    
    def step(self, delta_time):
        # allocate PRBs dynamically based on each UE's QoS profile and channel conditions
        self.allocate_prb()

    def allocate_prb(self):
        # sample QoS and channel condition-aware PRB allocation
       
        # Step 2: Calculate a score for each UE
        ue_scores = {}
        for ue in self.connected_ue_list.values():
            # Better RSSI = lower dBm = higher score (invert it)
            if self.cell_id in ue.live_signal_strength_dict:
                rssi_score = 100 + ue.live_signal_strength_dict[self.cell_id]["received_power"]  # e.g., -70 -> 30
            else:
                rssi_score = 100 + self.qrx_level_min  # Default to min level if not detected
            qos_weight = ue.qos_profile["GBR"] / 1e6  # Normalize for simplicity
            ue_scores[ue.ue_imsi] = rssi_score * qos_weight + 0.1  # Add a small constant to avoid zero allocation

        # print(f"Cell {self.cell_id}: UE scores: {ue_scores}")

        # Step 3: Normalize scores to allocate PRBs proportionally
        ue_ids = list(ue_scores.keys())
        normalized_scores = normalize(list(ue_scores.values()))
        self.prb_ue_allocation_dict = {
            ue_id: int(score * self.max_prb) for ue_id, score in zip(ue_ids, normalized_scores)
        }

    def estimate_bitrate_and_latency(self, prbs, qos):
        mcs_efficiency = 5  # bits/symbol as example
        subcarriers = 12  # per PRB
        symbol_duration = 0.0005  # 0.5 ms
        bandwidth = prbs * subcarriers * mcs_efficiency
        dl_bitrate = bandwidth / symbol_duration  # simplistic estimation
        ul_bitrate = dl_bitrate * 0.8  # assume UL is a bit lower
        latency = qos.get("latency", 20) + random.uniform(1, 5)

        print(
            f"Cell {self.cell_id}: Estimated DL bitrate: {dl_bitrate:.2f} bps, "
            f"UL bitrate: {ul_bitrate:.2f} bps, Latency: {latency:.2f} ms"
        )

        return dl_bitrate, ul_bitrate, latency

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
            "carrier_frequency": self.carrier_frequency,
            "bandwidth": self.bandwidth,
            "max_prb": self.max_prb,
            "cell_radius": self.cell_radius,
            "position_x": self.position_x,
            "position_y": self.position_y,
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
        core_response = self.core_network.handle_ue_authentication_and_registration(ue, ue_auth_reg_msg)
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
        print(
            f"gNB {self.bs_id}: UE {ue.ue_imsi} deregistered and resources released."
        )
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
            "ue_registry": list(self.ue_registry.keys()),
            "cell_list": [cell.to_json() for cell in self.cell_list],
        }

    def init_rrc_measurement_event_handler(self, event_id, handler):
        assert event_id is not None, "Event ID cannot be None"
        assert handler is not None, "Handler cannot be None"
        assert event_id not in self.ue_rrc_meas_event_handers, (
            f"Handler for event ID {event_id} already registered"
        )
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
                print(f"gNB {self.bs_id}: No handler for event ID {event_id}. Skipping.")
                continue
            handler = self.ue_rrc_meas_event_handers[event_id]
            handler(ue, event)
            print(f"gNB {self.bs_id}: Processed RRC measurement event {event_id} for UE {ue.ue_imsi}")