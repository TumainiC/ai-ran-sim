import json
import random
import settings


class BaseStation:
    def __init__(self, simulation_engine=None, bs_id=None, position_x=0, position_y=0):
        self.simulation_engine = simulation_engine
        self.core_network = simulation_engine.core_network
        self.bs_id = bs_id
        self.position_x = position_x
        self.position_y = position_y

        self.ru_radius = settings.RAN_DEFAULT_RU_RADIUS
        self.ref_signal_transmit_power = (
            settings.RAN_BS_REF_SIGNAL_DEFAULT_TRASNMIT_POWER
        )

        self.ue_registry = {}
        self.prb_ue_allocation_dict = {}
        self.neighbour_BS_list = set()
        self.max_prb = 100
        self.allocated_prb = 0
        self.current_load = 0

    def handle_registration(self, ue):
        print(f"gNB {self.bs_id}: Handling registration for UE {ue.ue_imsi}")
        self.ue_registry[ue.ue_imsi] = ue
        ue_slice_info, ue_qos_profile = self.core_network.authenticate_and_register(ue)
        ue_prb_allocation = self.allocate_prb(ue, ue_qos_profile)
        dl_bitrate, ul_bitrate, latency = self.estimate_bitrate_and_latency(
            ue_prb_allocation, ue_qos_profile
        )
        return ue_slice_info, ue_qos_profile, dl_bitrate, ul_bitrate, latency

    def update_allocated_prb_and_load(self):
        # calculate total allocated prb from ue allocation dict
        self.allocated_prb = sum(self.prb_ue_allocation_dict.values())
        self.current_load = self.allocated_prb / self.max_prb

    def allocate_prb(self, ue, ue_qos_profile):
        print(f"gNB {self.bs_id}: Configuring QoS for UE {ue.ue_imsi}")
        # prb should be calculated based on multiple factors.
        # for now, we are just assigning a random number of PRBs
        prb_allocation = random.randint(5, 10)
        prb_allocation = min(prb_allocation, self.max_prb - self.allocated_prb)
        self.prb_ue_allocation_dict[ue.ue_imsi] = prb_allocation
        self.update_allocated_prb_and_load()
        return prb_allocation

    def estimate_bitrate_and_latency(self, prbs, qos):
        mcs_efficiency = 5  # bits/symbol as example
        subcarriers = 12  # per PRB
        symbol_duration = 0.0005  # 0.5 ms
        bandwidth = prbs * subcarriers * mcs_efficiency
        dl_bitrate = bandwidth / symbol_duration  # simplistic estimation
        ul_bitrate = dl_bitrate * 0.8  # assume UL is a bit lower

        latency = qos.get("latency", 20) + random.uniform(1, 5)

        # ue.update_performance_metrics(dl_bitrate, ul_bitrate, latency)
        print(
            f"gNB {self.bs_id}: Estimated DL bitrate: {dl_bitrate:.2f} bps, "
            f"UL bitrate: {ul_bitrate:.2f} bps, Latency: {latency:.2f} ms"
        )

        return dl_bitrate, ul_bitrate, latency

    def handle_deregistration(self, ue):
        self.core_network.deregister_ue(ue)
        if ue.ue_imsi in self.ue_registry:
            del self.ue_registry[ue.ue_imsi]
        if ue.ue_imsi in self.prb_ue_allocation_dict:
            del self.prb_ue_allocation_dict[ue.ue_imsi]
        self.update_allocated_prb_and_load()
        print(f"gNB {self.bs_id}: UE {ue.ue_imsi} deregistered and resources released.")

    def save_load_history(self):
        self.load_history.append(self.current_load)
        if len(self.load_history) > settings.RAN_BS_LOAD_HISTORY_LENGTH:
            self.load_history.pop(0)

    def to_json(self):
        return {
            "bs_id": self.bs_id,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "ru_radius": self.ru_radius,
            "max_prb": self.max_prb,
            "allocated_prb": self.allocated_prb,
            "current_load": self.current_load,
            "ue_registry": list(self.ue_registry.keys()),
            "prb_ue_allocation_dict": self.prb_ue_allocation_dict,
            "neighbour_BS_list": [bs.bs_id for bs in self.neighbour_BS_list],
        }