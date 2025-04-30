import asyncio
import json
import random
from core_network import CoreNetwork
from ran import BaseStation
from ric import RanIntelligentController
from ue import UE
import settings
import utils


class SimulationEngine:
    def __init__(self, websocket=None):
        self.websocket = websocket
        self.core_network = None
        self.ric = None
        self.base_station_list = {}
        self.sim_started = False
        self.sim_step = 0

        self.ue_list = {}
        self.global_UE_counter = 0
        self.logs = []

        self.handover_event_history = []
        self.handover_action_list = []

    def try_add_base_station(self, bs):
        assert isinstance(bs, BaseStation)
        assert bs.simulation_engine == self
        assert bs.bs_id is not None
        assert bs.bs_id not in self.base_station_list
        self.base_station_list[bs.bs_id] = bs

    def network_setup(self):
        self.core_network = CoreNetwork(self)
        self.ric = RanIntelligentController(self)

        # init base station list
        for bs_data in settings.RAN_DEFAULT_BS_LIST:
            assert (
                bs_data[0] not in self.base_station_list
            ), f"Base station ID {bs_data[0]} already exists"
            bs = BaseStation(
                simulation_engine=self,
                bs_id=bs_data[0],
                position_x=bs_data[1],
                position_y=bs_data[2],
            )
            for other_bs in self.base_station_list.values():
                if (
                    utils.dist_between(
                        bs.position_x,
                        bs.position_y,
                        other_bs.position_x,
                        other_bs.position_y,
                    )
                    < 2 * bs.ru_radius
                ):
                    bs.neighbour_BS_list.add(other_bs)
                    other_bs.neighbour_BS_list.add(bs)
            self.try_add_base_station(bs)

    def is_handover_stablized(self):
        if len(self.handover_event_history) < settings.SIM_HANDOVER_HISTORY_LENGTH:
            return False
        return all([count == 0 for count in self.handover_event_history])

    def save_handover_count_history(self, handover_count):
        self.handover_event_history.append(handover_count)
        if len(self.handover_event_history) > settings.SIM_HANDOVER_HISTORY_LENGTH:
            self.handover_event_history.pop(0)

    def is_RU_load_history_all_stablized(self):
        for ru in self.base_station.RU_list:
            if len(ru.load_history) < settings.RAN_BS_LOAD_HISTORY_LENGTH:
                print("RU load history not stabilized")
                return False
            for i in range(1, settings.RAN_BS_LOAD_HISTORY_LENGTH):
                if ru.load_history[i] != ru.load_history[i - 1]:
                    print("RU load history not stabilized")
                    return False
        print("RU load history stabilized")
        return True

    def spawn_random_ue(self):
        position_x = random.randint(
            settings.UE_BOUNDARY_X_MIN, settings.UE_BOUNDARY_X_MAX
        )
        position_y = random.randint(
            settings.UE_BOUNDARY_Y_MIN, settings.UE_BOUNDARY_Y_MAX
        )
        target_x = random.randint(
            settings.UE_BOUNDARY_X_MIN, settings.UE_BOUNDARY_X_MAX
        )
        target_y = random.randint(
            settings.UE_BOUNDARY_Y_MIN, settings.UE_BOUNDARY_Y_MAX
        )
        speed = random.randint(settings.UE_SPEED_MIN, settings.UE_SPEED_MAX)

        ue = UE(
            ue_imsi=f"IMSI_{self.global_UE_counter}",
            position_x=position_x,
            position_y=position_y,
            target_x=target_x,
            target_y=target_y,
            speed=speed,
        )
        best_base_station = ue.select_best_bs(self.base_station_list.values())
        if best_base_station is None:
            print(f"UE {ue.ue_imsi} could not find a suitable base station.")
            return None
        ue.register(best_base_station)
        if not ue.connected:
            print(f"UE {ue.ue_imsi} failed to register to BS {best_base_station.bs_id}")
            return None

        print(f"UE {ue.ue_imsi} registered to BS {best_base_station.bs_id}")
        self.ue_list[ue.ue_imsi] = ue
        self.global_UE_counter += 1
        return ue

    def spawn_UEs(self):
        print(f"Current UE count: {len(self.ue_list.keys())}")
        if len(self.ue_list.keys()) == settings.UE_MAX_COUNT:
            print("UE count reached the maximum limit. No more UEs will be spawned.")
            return

        number_of_UEs_to_spawn = random.randint(
            settings.UE_DEFAULT_SPAWN_RATE_MIN,
            settings.UE_DEFAULT_SPAWN_RATE_MAX,
        )
        number_of_UEs_to_spawn = min(
            number_of_UEs_to_spawn, settings.UE_MAX_COUNT - len(self.ue_list)
        )
        print(f"Spawning {number_of_UEs_to_spawn} UEs:")
        num_us_spawned = 0
        while num_us_spawned < number_of_UEs_to_spawn:
            ue = self.spawn_random_ue()
            if ue is None:
                continue
            num_us_spawned += 1

    def step_UEs(self, delta_time):
        ue_to_remove = []
        for ue in self.ue_list.values():
            ue.step(delta_time)
            if not ue.connected:
                ue_to_remove.append(ue)

        for ue in ue_to_remove:
            del self.ue_list[ue.ue_imsi]
            print(f"UE {ue.ue_imsi} deregistered and removed from simulation.")

    def update_BSs(self, delta_time):
        pass

    def step(self, delta_time):
        self.logs = []
        # self.update_BSs(delta_time)

        self.spawn_UEs()
        self.step_UEs(delta_time)
        # print("***")
        # for ru in self.base_station.RU_list:
        #     ru.update_current_load()
        #     ru.save_load_history()

    async def start_simulation(self):
        assert not self.sim_started
        self.sim_step = 0
        self.sim_started = True

        while self.sim_started and self.sim_step < settings.SIM_MAX_STEP:
            print(f"\n========= TIME STEP: {self.sim_step} ==========\n")
            self.sim_step += 1
            self.step(settings.SIM_STEP_TIME_DEFAULT)
            await self.websocket.send(
                json.dumps(
                    {"type": "simulation_state", "data": self.to_json()}
                )
            )
            await asyncio.sleep(settings.SIM_STEP_TIME_DEFAULT)
        
        print("simulation ended")

    def stop(self):
        self.sim_started = False
        self.logs.append("Simulation stopped")
        print("Simulation stopped")

    def to_json(self):
        return {
            "time_step": self.sim_step,
            "base_stations": [bs.to_json() for bs in self.base_station_list.values()],
            "UE_list": [ue.to_json() for ue in self.ue_list.values()],
            "logs": self.logs,
        }
