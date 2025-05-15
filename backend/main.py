import asyncio
import websockets
import json
import settings
from network_layer.simulation_engine import SimulationEngine
from utils import setup_logging
import knowledge_layer

setup_logging()


async def websocket_handler(websocket):
    simulation_engine = SimulationEngine(websocket)
    simulation_engine.network_setup()
    knowledge_router = knowledge_layer.initialize_knowledge_router(simulation_engine)
    while True:
        message = await websocket.recv()
        try:
            message_json = json.loads(message)
            layer = message_json.get("layer")
            command = message_json.get("command")
            data = message_json.get("data", {})
        except (json.JSONDecodeError, KeyError):
            await websocket.send(
                json.dumps(
                    {
                        "layer": None,
                        "command": None,
                        "response": None,
                        "error": "Invalid message format",
                    }
                )
            )
            continue

        try:
            if layer == "network_layer" and command == "start_simulation":
                await websocket.send(
                    json.dumps(
                        {
                            "layer": "network_layer",
                            "command": "start_simulation",
                            "response": "Starting simulation",
                            "error": None,
                        }
                    )
                )
                asyncio.create_task(simulation_engine.start_simulation())
            elif layer == "network_layer" and command == "stop_simulation":
                await websocket.send(
                    json.dumps(
                        {
                            "layer": "network_layer",
                            "command": "stop_simulation",
                            "response": "Stopping simulation",
                            "error": None,
                        }
                    )
                )
                simulation_engine.stop()
            elif layer == "network_layer" and command == "get_simulation_state":
                await websocket.send(
                    json.dumps(
                        {
                            "layer": "network_layer",
                            "command": "get_simulation_state",
                            "response": simulation_engine.to_json(),
                            "error": None,
                        }
                    )
                )
            elif layer == "knowledge_layer" and command == "get_routes":
                await websocket.send(
                    json.dumps(
                        {
                            "layer": "knowledge_layer",
                            "command": "get_routes",
                            "response": knowledge_router.get_routes(),
                            "error": None,
                        }
                    )
                )
            elif layer == "knowledge_layer" and command == "get_value":
                await websocket.send(
                    json.dumps(
                        {
                            "layer": "knowledge_layer",
                            "command": "get_value",
                            "response": knowledge_router.get_value(data),
                            "error": None,
                        }
                    )
                )
            elif layer == "knowledge_layer" and command == "explain_value":
                await websocket.send(
                    json.dumps(
                        {
                            "layer": "knowledge_layer",
                            "command": "explain_value",
                            "response": knowledge_router.explain_value(data),
                            "error": None,
                        }
                    )
                )
            elif layer == "intelligence_layer" and command == "chat":
                pass
            else:
                await websocket.send(
                    json.dumps(
                        {
                            "layer": layer,
                            "command": command,
                            "response": None,
                            "error": "Unknown command",
                        }
                    )
                )
        except Exception as e:
            await websocket.send(
                json.dumps(
                    {
                        "layer": layer,
                        "command": command,
                        "response": None,
                        "error": str(e),
                    }
                )
            )


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
