import math
import settings
from utils import dist_between, estimate_throughput


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

        self.prb_ue_allocation_dict = {}  # { "ue_imsi": {"downlink": 30, "uplink": 5}}
        self.connected_ue_list = {}
        self.ue_uplink_signal_strength_dict = {}

    def __repr__(self):
        return f"Cell({self.cell_id}, base_station={self.base_station.bs_id}, frequency_band={self.frequency_band}, carrier_frequency_MHz={self.carrier_frequency_MHz})"

    @property
    def allocated_dl_prb(self):
        return sum(
            [
                self.prb_ue_allocation_dict[ue_imsi]["downlink"]
                for ue_imsi in self.connected_ue_list.keys()
            ]
        )

    @property
    def allocated_ul_prb(self):
        return sum(
            [
                self.prb_ue_allocation_dict[ue_imsi]["uplink"]
                for ue_imsi in self.connected_ue_list.keys()
            ]
        )

    @property
    def allocated_prb(self):
        return sum(
            [
                self.prb_ue_allocation_dict[ue_imsi]["uplink"]
                + self.prb_ue_allocation_dict[ue_imsi]["downlink"]
                for ue_imsi in self.connected_ue_list.keys()
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
            ue.set_downlink_mcs_index(-1)
            ue.set_downlink_mcs_data(None)
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
            # print(
            #     f"Cell {self.cell_id}: UE {ue.ue_imsi} selected MCS index {max_mcs_index} based on CQI {ue.downlink_cqi}"
            # )
            ue.set_downlink_mcs_index(max_mcs_index)
            ue.set_downlink_mcs_data(
                settings.RAN_MCS_SPECTRAL_EFFICIENCY_TABLE.get(max_mcs_index, None).copy()
            )

    def step(self, delta_time):
        self.monitor_ue_signal_strength()

        # select modulation and coding scheme (MCS) for each UE based on CQI
        self.select_ue_mcs()

        # allocate PRBs dynamically based on each UE's QoS profile and channel conditions
        self.allocate_prb()

        # for each UE, estimate the downlink, uplink bitrate and latency
        self.estimate_ue_bitrate_and_latency()

    def allocate_prb(self):
        # QoS-aware Proportional Fair Scheduling (PFS)

        # reset PRB allocation for all UEs
        for ue in self.connected_ue_list.values():
            self.prb_ue_allocation_dict[ue.ue_imsi]["downlink"] = 0
            self.prb_ue_allocation_dict[ue.ue_imsi]["uplink"] = 0

        # sample QoS and channel condition-aware PRB allocation
        ue_prb_requirements = {}

        # Step 1: Calculate required PRBs for GBR
        for ue in self.connected_ue_list.values():
            dl_gbr = ue.qos_profile["GBR_DL"]
            dl_mcs = ue.downlink_mcs_data  # Assume this attribute exists
            if dl_mcs is None:
                print(
                    f"Cell {self.cell_id}: UE {ue.ue_imsi} has no downlink MCS data. Skipping."
                )
                continue
            dl_throughput_per_prb = estimate_throughput(
                dl_mcs["modulation_order"], dl_mcs["target_code_rate"], 1
            )
            dl_required_prbs = math.ceil(dl_gbr / dl_throughput_per_prb)
            ue_prb_requirements[ue.ue_imsi] = {
                "dl_required_prbs": dl_required_prbs,
                "dl_throughput_per_prb": dl_throughput_per_prb,
            }

        # Step 2: Allocate PRBs to meet GBR
        dl_total_prb_demand = sum(
            req["dl_required_prbs"] for req in ue_prb_requirements.values()
        )

        if dl_total_prb_demand <= self.max_dl_prb:
            # allocate PRBs based on the required PRBs
            for ue_imsi, req in ue_prb_requirements.items():
                self.prb_ue_allocation_dict[ue_imsi]["downlink"] = req[
                    "dl_required_prbs"
                ]
        else:
            # allocate PRBs based on the proportion
            # first allocate at least one PRB to each UE to ensure minimum service
            dl_remaining_prbs = self.max_dl_prb
            for ue in self.connected_ue_list.values():
                prb = min(1, dl_remaining_prbs)
                self.prb_ue_allocation_dict[ue.ue_imsi]["downlink"] = prb
                dl_remaining_prbs -= prb

            # then allocate the remaining PRBs based on the proportion
            if dl_remaining_prbs > 0:
                for ue_imsi, req in ue_prb_requirements.items():
                    share = req["dl_required_prbs"] / dl_total_prb_demand
                    additional_prbs = int(share * dl_remaining_prbs)
                    self.prb_ue_allocation_dict[ue_imsi]["downlink"] += additional_prbs

        # # Logging
        # for ue_imsi, allocation in self.prb_ue_allocation_dict.items():
        #     print(
        #         f"Cell: {self.cell_id} allocated {allocation['downlink']} DL PRBs for UE {ue_imsi}"
        #     )

    def estimate_ue_bitrate_and_latency(self):
        for ue in self.connected_ue_list.values():
            if ue.downlink_mcs_data is None:
                print(
                    f"Cell {self.cell_id}: UE {ue.ue_imsi} has no downlink MCS data. Skipping."
                )
                continue
            ue_modulation_order = ue.downlink_mcs_data["modulation_order"]
            ue_code_rate = ue.downlink_mcs_data["target_code_rate"]
            ue_dl_prb = self.prb_ue_allocation_dict[ue.ue_imsi]["downlink"]
            # TODO: uplink bitrate
            dl_bitrate = estimate_throughput(
                ue_modulation_order, ue_code_rate, ue_dl_prb
            )
            ue.set_downlink_bitrate(dl_bitrate)
            # TODO: downlink and uplink latency

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
            "vis_cell_radius": self.cell_radius
            * settings.REAL_LIFE_DISTANCE_MULTIPLIER,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "vis_position_x": self.position_x * settings.REAL_LIFE_DISTANCE_MULTIPLIER,
            "vis_position_y": self.position_y * settings.REAL_LIFE_DISTANCE_MULTIPLIER,
            "prb_ue_allocation_dict": self.prb_ue_allocation_dict,
            "max_dl_prb": self.max_dl_prb,
            "max_ul_prb": self.max_ul_prb,
            "allocated_dl_prb": self.allocated_dl_prb,
            "allocated_ul_prb": self.allocated_ul_prb,
            "current_dl_load": self.allocated_dl_prb / self.max_dl_prb,
            "current_ul_load": self.allocated_ul_prb / self.max_ul_prb,
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
        self.cell_list = {}
        for cell_init_data in bs_init_data["cell_list"]:
            new_cell = Cell(
                base_station=self,
                cell_init_data=cell_init_data,
            )
            self.cell_list[cell_init_data["cell_id"]] = new_cell
        self.rrc_measurement_events = bs_init_data["rrc_measurement_events"]

        self.ue_registry = {}
        self.ue_rrc_meas_events = []
        self.ue_rrc_meas_event_handers = {}

        self.ric_control_actions = []

    def __repr__(self):
        return f"BS {self.bs_id}"

    def receive_ue_rrc_meas_events(self, event):
        # sanity check
        ue = event["triggering_ue"]
        current_cell = self.cell_list.get(event["current_cell_id"], None)
        assert ue is not None, "UE cannot be None"
        assert current_cell is not None, "Current cell cannot be None"
        assert ue.current_cell.cell_id == current_cell.cell_id, (
            f"UE {ue.ue_imsi} (current cell: {ue.current_cell.cell_id}) is not in the current cell ({current_cell.cell_id})"
        )
        print(f"{self} received UE reported RRC measurement event:")
        print(event)
        self.ue_rrc_meas_events.append(event)

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
        
        # remove rrc measurement events for the UE
        events_to_remove = []
        for event in self.ue_rrc_meas_events:
            if event["triggering_ue"] == ue:
                events_to_remove.append(event)
        for event in events_to_remove:
            self.ue_rrc_meas_events.remove(event)

        print(f"gNB {self.bs_id}: UE {ue.ue_imsi} deregistered and resources released.")
        return True


    def to_json(self):
        return {
            "bs_id": self.bs_id,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "vis_position_x": self.position_x * settings.REAL_LIFE_DISTANCE_MULTIPLIER,
            "vis_position_y": self.position_y * settings.REAL_LIFE_DISTANCE_MULTIPLIER,
            "ue_registry": list(self.ue_registry.keys()),
            "cell_list": [cell.to_json() for cell in self.cell_list.values()],
        }

    def init_rrc_measurement_event_handler(self, event_id, handler):
        assert event_id is not None, "Event ID cannot be None"
        assert handler is not None, "Handler cannot be None"
        assert (
            event_id not in self.ue_rrc_meas_event_handers
        ), f"Handler for event ID {event_id} already registered"
        self.ue_rrc_meas_event_handers[event_id] = handler

    def process_ric_control_actions(self):
        # only handover actions are supported for now

        # check if there are multiple handover actions for the same UE,
        # reject or merge wherever necessary
        ue_handover_actions = {}
        for action in self.ric_control_actions:
            if action.action_type != action.ACTION_TYPE_HANDOVER:
                print(
                    f"gNB {self.bs_id}: Ignoring non-handover action: {action.action_type}"
                )
                continue

            ue = action.action_data["ue"]
            if ue.ue_imsi not in ue_handover_actions:
                ue_handover_actions[ue.ue_imsi] = []
            ue_handover_actions[ue.ue_imsi].append(action)

        # process each UE's handover actions
        for ue_imsi, actions in ue_handover_actions.items():
            # for now perform the first handover action only.
            action = actions[0]
            ue = action.action_data["ue"]
            source_cell_id = action.action_data["source_cell_id"]
            target_cell_id = action.action_data["target_cell_id"]
            source_cell = self.simulation_engine.cell_list[source_cell_id]
            target_cell = self.simulation_engine.cell_list[target_cell_id]
            self.execute_handover(ue, source_cell, target_cell)
            break

    def execute_handover(self, ue, source_cell, target_cell):
        assert ue is not None, "UE cannot be None"
        assert (
            source_cell is not None and target_cell is not None
        ), "Source or target cell cannot be None"
        assert source_cell != target_cell, "Source and target cell cannot be the same"
        assert ue.current_cell.cell_id == source_cell.cell_id, f"UE {ue.ue_imsi} (current cell: {ue.current_cell.cell_id})is not in the source cell ({source_cell.cell_id})"
        assert (
            ue.ue_imsi in source_cell.connected_ue_list
        ), "UE is not connected to the source cell"
        assert (
            ue.ue_imsi not in target_cell.connected_ue_list
        ), "UE is already connected to the target cell"

        source_bs = source_cell.base_station
        target_bs = target_cell.base_station

        if source_bs.bs_id == target_bs.bs_id:
            # same base station, just change the cell
            target_cell.register_ue(ue)
            ue.execute_handover(target_cell)
            self.ue_registry[ue.ue_imsi]["cell"] = target_cell
            source_cell.deregister_ue(ue)
            print(
                f"gNB {self.bs_id}: Handover UE {ue.ue_imsi} from cell {source_cell.cell_id} to cell {target_cell.cell_id}"
            )
        else:
            ue_reg_data = source_bs.ue_registry[ue.ue_imsi].copy()
            ue_reg_data["cell"] = target_cell
            ue_reg_data["rrc_meas_events"] = target_bs.rrc_measurement_events.copy()
            target_bs.ue_registry[ue.ue_imsi] = ue_reg_data
            target_cell.register_ue(ue)
            ue.execute_handover(target_cell)
            source_cell.deregister_ue(ue)
            del source_bs.ue_registry[ue.ue_imsi]
            print(
                f"gNB {self.bs_id} Handover UE {ue.ue_imsi} from cell {source_cell.cell_id} to BS: {target_bs.bs_id} cell {target_cell.cell_id} (different BS)"
            )

    def step(self, delta_time):
        # first update cell first
        for cell in self.cell_list.values():
            cell.step(delta_time)

        # reset RIC control actions
        self.ric_control_actions = []

        # process RRC measurement events
        while len(self.ue_rrc_meas_events) > 0:
            event = self.ue_rrc_meas_events.pop(0)
            event_id = event["event_id"]
            if event_id not in self.ue_rrc_meas_event_handers:
                print(
                    f"gNB {self.bs_id}: No handler for event ID {event_id}. Skipping."
                )
                continue
            handler = self.ue_rrc_meas_event_handers[event_id]
            action = handler(event)

            if action is not None:
                # add the action to the RIC control actions list
                self.ric_control_actions.append(action)

            print(
                f"gNB {self.bs_id}: Processed RRC measurement event {event_id} for UE {event["triggering_ue"].ue_imsi}"
            )

        # process (reject, merge or execute) all the RIC control actions
        self.process_ric_control_actions()
