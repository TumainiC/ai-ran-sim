import asyncio
import websockets
import json
import settings
from network_layer.simulation_engine import SimulationEngine
from utils import setup_logging

setup_logging()


async def websocket_handler(websocket):
    simulation_engine = SimulationEngine(websocket)
    simulation_engine.network_setup()
    while True:
        message = await websocket.recv()
        if message == "network_layer/start_simulation":
            await websocket.send(
                json.dumps({"type": "log", "data": "Starting simulation"})
            )
            asyncio.create_task(simulation_engine.start_simulation())
        elif message == "network_layer/stop_simulation":
            await websocket.send(
                json.dumps({"type": "log", "data": "Stopping simulation"})
            )
            simulation_engine.stop()
        elif message == "network_layer/get_simulation_state":
            await websocket.send(
                json.dumps(
                    {"type": "simulation_state", "data": simulation_engine.to_json()}
                )
            )
        elif message == "knowledge_layer/get_routes":
            await websocket.send(
                json.dumps(
                    {
                        "type": "knowledge_layer/routes",
                        "data": simulation_engine.knowledge_router.get_routes(),
                    }
                )
            )
        elif message.startswith("knowledge_layer/get_value/"):
            query_key = message.replace("knowledge_layer/get_value/", "")
            print(f"Querying value for key: {query_key}")
            await websocket.send(
                json.dumps(
                    {
                        "type": "knowledge_layer/value_response",
                        "data": simulation_engine.knowledge_router.get_value(query_key),
                    }
                )
            )
        elif message.startswith("knowledge_layer/explain_value/"):
            query_key = message.replace("knowledge_layer/explain_value/", "")
            print(f"Explaining value for key: {query_key}")
            await websocket.send(
                json.dumps(
                    {
                        "type": "knowledge_layer/explanation_response",
                        "data": simulation_engine.knowledge_router.explain_value(
                            query_key
                        ),
                    }
                )
            )
        else:
            print(f"Unknown command: {message}")


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
