import asyncio
import json
import math
import random
from core_network import CoreNetwork
from ran import BaseStation
from ric import RanIntelligentController
import settings
import utils


class SimulationEngine:
    def __init__(self, websocket=None):
        self.websocket = websocket
        self.core_network = None
        self.ric = None
        self.base_stations = {}

        self.UE_list = set()
        self.global_UE_counter = 0
        self.logs = []
        self.timestep = 0
        self.handover_event_history = []
        self.handover_action_list = []

    def try_add_base_station(self, bs):
        assert isinstance(bs, BaseStation)
        assert bs.simulation_engine == self
        assert bs.bs_id is not None
        assert bs.bs_id not in self.base_stations
        self.base_stations[bs.bs_id] = bs

    def network_setup(self):
        self.core_network = CoreNetwork(self)
        self.ric = RanIntelligentController(self)

        # init base station list
        for bs_data in settings.RAN_DEFAULT_BS_LIST:
            assert (
                bs_data[0] not in self.base_stations
            ), f"Base station ID {bs_data[0]} already exists"
            bs = BaseStation(
                simulation_engine=self,
                bs_id=bs_data[0],
                position_x=bs_data[1],
                position_y=bs_data[2],
            )
            for other_bs in self.base_stations.values():
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
        min_prb = random.randint(
            settings.UE_MIN_PRB_RANGE_MIN, settings.UE_MIN_PRB_RANGE_MAX
        )
        ue_id = f"UE_{self.global_UE_counter}"
        ue = UE(
            ue_id=ue_id,
            position_x=position_x,
            position_y=position_y,
            min_prb=min_prb,
        )
        self.UE_list.add(ue)
        self.global_UE_counter += 1

    def spawn_UEs(self, fixed_count=settings.UE_FIXED_COUNT):
        if not fixed_count:
            ue_to_spawn = math.floor(
                random.randint(
                    settings.UE_DEFAULT_SPAWN_RATE_MIN,
                    settings.UE_DEFAULT_SPAWN_RATE_MAX,
                )
            )

            # print("spawning new UEs: ", ue_count)
            for _ in range(ue_to_spawn):
                self.spawn_random_ue()
        else:
            if len(self.UE_list) < fixed_count:
                for _ in range(fixed_count - len(self.UE_list)):
                    self.spawn_random_ue()
                return

            number_of_ue_to_refresh = math.floor(
                len(self.UE_list) * settings.UE_REFRESH_PORTION
            )
            print(
                "number of UEs " + str(len(self.UE_list)),
                "number of UEs to refresh " + str(number_of_ue_to_refresh),
            )

            if number_of_ue_to_refresh > 0:
                # remove some UEs
                UE_to_remove_list = random.sample(
                    list(self.UE_list), number_of_ue_to_refresh
                )
                for ue in UE_to_remove_list:
                    self.base_station.remove_UE(ue)
                    self.UE_list.remove(ue)

                # add new UEs
                for _ in range(number_of_ue_to_refresh):
                    self.spawn_random_ue()

    def update_UEs(self, delta_time):
        if not settings.SIM_SPAWN_UE_AFTER_LOAD_HISTORY_STABLIZED:
            self.spawn_UEs()
        elif self.is_RU_load_history_all_stablized() and self.is_handover_stablized():
            self.spawn_UEs()

        # update UE position and time
        for ue in self.UE_list:
            ue.position_x += ue.velocity_x * delta_time
            ue.position_y += ue.velocity_y * delta_time
            ue.time_ramaining -= delta_time

        # update the connection status of UEs to the RUs
        for ue in self.UE_list:
            ue.connected = False
            for ru in self.base_station.RU_list:
                dist_to_RU = ue.dist_to(ru)
                connected_to_RU = dist_to_RU <= ru.radius
                if connected_to_RU:
                    ue.connected = True
                    ue.dist_to_connected_RU_dict[ru.ru_id] = dist_to_RU
                    if ue not in ru.connected_UE_list:
                        ru.connected_UE_list.add(ue)
                    if ru not in ue.connected_RU_list:
                        ue.connected_RU_list.add(ru)

        # remove the UE if the UE removes out of boundary or connection time is over
        UE_to_remove_list = []
        for ue in self.UE_list:
            if (
                ue.position_x < settings.UE_BOUNDARY_X_MIN
                or ue.position_x > settings.UE_BOUNDARY_X_MAX
                or ue.position_y < settings.UE_BOUNDARY_Y_MIN
                or ue.position_y > settings.UE_BOUNDARY_Y_MAX
                or ue.time_ramaining <= 0
                or not ue.connected
            ):
                UE_to_remove_list.append(ue)

        for ue in UE_to_remove_list:
            # print("removing UE: ", ue.ue_id)
            self.base_station.remove_UE(ue)
            self.UE_list.remove(ue)

        # from here onwards, all the UEs are connected to at least one RU

        # serve the UE with the nearest RU at the beginning
        for ue in self.UE_list:
            if ue.served_by_BS is None:
                min_dist = float("inf")
                min_dist_ru = None
                for ru in ue.connected_RU_list:
                    if ue.dist_to_connected_RU_dict[ru.ru_id] < min_dist:
                        min_dist = ue.dist_to_connected_RU_dict[ru.ru_id]
                        min_dist_ru = ru

                if min_dist_ru is not None:
                    if min_dist_ru.ru_id == "ru_11":
                        print("serving UE: ", ue.ue_id, "by RU: ", min_dist_ru.ru_id)
                    min_dist_ru.serve_UE(ue)

    def update_RUs(self, delta_time):
        # perform the handover actions from the last step
        for handover_action in self.handover_action_list:
            ue, ru, neighbour_ru = handover_action
            # perform the handover
            # mark the ue to be removed later
            # ue_to_handover_list.append(ue)
            # empty the allocated prb by the RU
            ru.unserve_UE(ue)
            ue.allocated_prb = 0
            # let the neighbour RU serve the UE
            neighbour_ru.serve_UE(ue)
            # log the handover event
            self.logs.append(
                f"UE {ue.ue_id} is handed over from RU {ru.ru_id} to RU {neighbour_ru.ru_id}"
            )

        self.handover_action_list = []

        # execute the prb control policy and handover policy for each RU
        for ru in self.base_station.RU_list:
            # assume now the connection and serving status of RU and UE is updated.

            # -------------------------
            # prb control policy
            # -------------------------
            ru.update_current_load()
            # check if the RU needs to activate more prbs
            if ru.demanded_prb > ru.allocable_prb:
                # check if the RU can allocate more prb
                if ru.max_prb > ru.allocable_prb:
                    # allocate more prb first to the RU
                    # to better visuzlie the prb control, we change maximum 10 prb at a time
                    prb_to_allocate = min(ru.max_prb - ru.allocable_prb, 10)
                    ru.allocable_prb += prb_to_allocate
            elif ru.demanded_prb < ru.allocable_prb:
                # deactivate some prbs if the RU is not fully utilized
                max_prb_to_deactivate = min(10, ru.allocable_prb - ru.demanded_prb)
                ru.allocable_prb -= max_prb_to_deactivate
                ru.allocable_prb = max(
                    settings.RAN_BS_DEFAULT_MIN_ALLOCABLE_PRB, ru.allocable_prb
                )

            # allocate the remaining activated and available prb to the needed UEs.
            ru.update_current_load()
            for ue in ru.served_UE_list:
                if ue.allocated_prb >= ue.min_prb:
                    # currently by default we do not allocate more prb to the UE than needed
                    continue

                # the UE needs more prb
                prb_to_allocate_to_ue = min(
                    ue.min_prb - ue.allocated_prb, ru.allocable_prb - ru.allocated_prb
                )
                ue.allocated_prb += prb_to_allocate_to_ue
                ru.allocated_prb += prb_to_allocate_to_ue

            ru.update_current_load()
            # check if the RU is full and UEs are still waiting for more prb
            if settings.RIC_ENABLE_HANDOVER and ru.demanded_prb > ru.max_prb:
                if (
                    ru.allocated_prb == ru.max_prb
                    and ru.allocable_prb == ru.allocated_prb
                ):
                    # try to handover the UEs to the neighbour RUs
                    ue_to_handover_list = []
                    for ue in ru.served_UE_list:
                        if ue.allocated_prb >= ue.min_prb:
                            continue

                        if settings.RIC_BRUTAL_HANDOVER:
                            available_neighbour_RUs = [
                                neighbour_ru
                                for neighbour_ru in ru.neighbour_RU_list
                                if neighbour_ru in ue.connected_RU_list
                            ]
                            if len(available_neighbour_RUs) > 0:
                                # randomly select a neighbour RU to serve the UE
                                neighbour_ru = random.choice(available_neighbour_RUs)

                                self.handover_action_list.append((ue, ru, neighbour_ru))

                                # # perform the handover
                                # # mark the ue to be removed later
                                # ue_to_handover_list.append(ue)
                                # # empty the allocated prb by the RU
                                # ru.allocated_prb -= ue.allocated_prb
                                # ue.allocated_prb = 0
                                # # let the neighbour RU serve the UE
                                # neighbour_ru.serve_UE(ue)
                                # # log the handover event
                                # self.logs.append(f"UE {ue.ue_id} is handed over from RU {ru.ru_id} to RU {neighbour_ru.ru_id}")
                                # num_of_handover_events += 1
                        else:
                            # check if the neighbour RUs can help
                            for neighbour_ru in ru.neighbour_RU_list:
                                # check connectivity between the neighbour RU and the UE
                                if neighbour_ru not in ue.connected_RU_list:
                                    continue

                                # check if the neighbour RU has enough available prb
                                neighbour_ru.update_current_load()
                                if (
                                    neighbour_ru.demanded_prb + ue.min_prb
                                ) <= neighbour_ru.max_prb:
                                    self.handover_action_list.append(
                                        (ue, ru, neighbour_ru)
                                    )
                                    # # perform the handover
                                    # # mark the ue to be removed later
                                    # ue_to_handover_list.append(ue)
                                    # # empty the allocated prb by the RU
                                    # ru.allocated_prb -= ue.allocated_prb
                                    # ue.allocated_prb = 0
                                    # # let the neighbour RU serve the UE
                                    # neighbour_ru.serve_UE(ue)
                                    # # log the handover event
                                    # self.logs.append(f"UE {ue.ue_id} is handed over from RU {ru.ru_id} to RU {neighbour_ru.ru_id}")
                                    # num_of_handover_events += 1
                                    break

                    # for ue in ue_to_handover_list:
                    #     # remove the UE from the served list only.
                    #     # do not remove the UE's prb from RU anymore as it is already done during the handover previously.
                    #     ru.served_UE_list.remove(ue)

            ru.update_current_load()

        self.save_handover_count_history(len(self.handover_action_list))

    def update(self, delta_time):
        self.logs = []
        self.update_RUs(delta_time)
        self.update_UEs(delta_time)

        print("***")
        for ru in self.base_station.RU_list:
            ru.update_current_load()
            ru.save_load_history()

            if ru.ru_id == "ru_11":
                print(
                    f"RU {ru.ru_id} current load: {ru.current_load} demanded prb: {ru.demanded_prb} allocated prb: {ru.allocated_prb}"
                )

    async def start(self):
        if self.base_station is None:
            self.init_simulation()

        while True:
            print(
                f"\n========================= TIME STEP: {self.timestep} =========================\n"
            )
            self.timestep += 1
            self.update(settings.SIM_STEP_TIME_DEFAULT)
            print("\n-------------------------\n")
            await self.websocket.send(
                json.dumps(
                    {"type": "simulationsimulation_state", "data": self.to_json()}
                )
            )
            await asyncio.sleep(settings.SIM_STEP_TIME_DEFAULT)
            if self.timestep >= settings.SIM_MAX_STEP:
                break

    def stop(self):
        pass

    def to_json(self):
        return {
            "time_step": self.timestep,
            "base_stations": [bs.to_json() for bs in self.base_stations.values()],
            "UE_list": [ue.to_json() for ue in self.UE_list],
            "logs": self.logs,
        }
