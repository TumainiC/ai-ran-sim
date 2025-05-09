import asyncio
import websockets
import json
import settings
from simulation_engine import SimulationEngine
from utils import setup_logging

setup_logging()


async def websocket_handler(websocket):
    simulation_engine = SimulationEngine(websocket)
    simulation_engine.network_setup()
    while True:
        message = await websocket.recv()
        if message == "start_simulation":
            await websocket.send(
                json.dumps({"type": "log", "data": "Starting simulation"})
            )
            asyncio.create_task(simulation_engine.start_simulation())
        elif message == "stop_simulation":
            await websocket.send(
                json.dumps({"type": "log", "data": "Stopping simulation"})
            )
            simulation_engine.stop()
        elif message == "get_simulation_state":
            await websocket.send(
                json.dumps(
                    {"type": "simulation_state", "data": simulation_engine.to_json()}
                )
            )
        else:
            print("Unknown command")


async def main():
    async with websockets.serve(
        websocket_handler, settings.WS_SERVER_HOST, settings.WS_SERVER_PORT
    ):
        print(
            f"WebSocket server started on ws://{settings.WS_SERVER_HOST}:{settings.WS_SERVER_PORT}"
        )
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
