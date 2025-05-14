import asyncio
import json
import random
from .core_network import CoreNetwork
from .ran import BaseStation, Cell
from .ric import NearRTRIC
from .ue import UE
import settings
import knowledge_layer


class SimulationEngine:
    def __init__(self, websocket=None):
        self.websocket = websocket
        self.core_network = None
        self.nearRT_ric = None

        self.base_station_list = {}
        self.cell_list = {}
        self.ue_list = {}

        self.sim_started = False
        self.sim_step = 0

        self.global_UE_counter = 0
        self.logs = []

        self.knowledge_router = knowledge_layer.initialize_knowledge(self)

    def add_base_station(self, bs):
        assert isinstance(bs, BaseStation)
        assert bs.simulation_engine == self
        assert bs.bs_id is not None
        assert bs.bs_id not in self.base_station_list
        self.base_station_list[bs.bs_id] = bs
        for cell in bs.cell_list.values():
            self.add_cell(cell)

    def add_cell(self, cell):
        assert isinstance(cell, Cell)
        assert cell.cell_id is not None
        assert cell.cell_id not in self.cell_list
        self.cell_list[cell.cell_id] = cell

    def network_setup(self):
        self.core_network = CoreNetwork(self)

        # init base station list
        for bs_init_data in settings.RAN_DEFAULT_BS_LIST:
            assert (
                bs_init_data["bs_id"] not in self.base_station_list
            ), f"Base station ID {bs_init_data[0]} already exists"
            self.add_base_station(
                BaseStation(
                    simulation_engine=self,
                    bs_init_data=bs_init_data,
                )
            )

        # for the moment, the ric must be initialized after the core network and the base stations.
        # so that the xApps can subscribe information from the base stations.
        self.nearRT_ric = NearRTRIC(self)
        self.nearRT_ric.load_xApps()

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
        speed_mps = random.randint(settings.UE_speed_mps_MIN, settings.UE_speed_mps_MAX)

        ue = UE(
            ue_imsi=f"IMSI_{self.global_UE_counter}",
            position_x=position_x,
            position_y=position_y,
            target_x=target_x,
            target_y=target_y,
            speed_mps=speed_mps,
            simulation_engine=self,
        )
        if not ue.power_up():
            print(f"UE {ue.ue_imsi} power up procedures failed.")
            return None
        self.add_ue(ue)
        print(
            f"UE {ue.ue_imsi} registered to network. Served by cell: {ue.current_cell.cell_id}."
        )
        return ue

    def add_ue(self, ue):
        assert isinstance(ue, UE)
        assert ue.ue_imsi is not None
        assert ue.ue_imsi not in self.ue_list
        self.ue_list[ue.ue_imsi] = ue
        self.global_UE_counter += 1

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

    def remove_UE(self, ue):
        assert isinstance(ue, UE)
        assert ue.ue_imsi in self.ue_list
        del self.ue_list[ue.ue_imsi]
        print(f"UE {ue.ue_imsi} deregistered and removed from simulation.")

    def step_BSs(self, delta_time):
        for bs in self.base_station_list.values():
            bs.step(delta_time)

    def step(self, delta_time):
        print("===================================")
        print("        Simulation Step  ")
        print("===================================")

        self.logs = []

        # spawn new UEs if needed
        print("\n ---------- Spawning UEs -----------\n")
        self.spawn_UEs()

        # move UEs towards their targets, monitor signal quality, report measurement events ...
        print("\n ---------- Step UEs ----------- \n")
        self.step_UEs(delta_time)

        # dynamically allocate resources for UEs
        print("\n ---------- Step BSs ----------- \n")
        self.step_BSs(delta_time)

    async def start_simulation(self):
        assert not self.sim_started
        self.sim_step = 0
        self.sim_started = True

        while self.sim_started and self.sim_step < settings.SIM_MAX_STEP:
            print(f"\n========= TIME STEP: {self.sim_step} ==========\n")
            self.sim_step += 1
            self.step(settings.SIM_STEP_TIME_DEFAULT)
            await self.websocket.send(
                json.dumps({"type": "simulation_state", "data": self.to_json()})
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
            "cells": [cell.to_json() for cell in self.cell_list.values()],
            "UE_list": [ue.to_json() for ue in self.ue_list.values()],
            "logs": self.logs,
        }
