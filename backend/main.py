import asyncio
import websockets
import json
import settings
from agents import ItemHelpers
from network_layer.simulation_engine import SimulationEngine
from openai.types.responses import ResponseTextDeltaEvent, ResponseFunctionToolCall
from utils import setup_logging
from knowledge_layer import KnowledgeRouter
from agents import Runner
import dotenv

dotenv.load_dotenv()
from intelligence_layer import chat_agent

setup_logging()


async def websocket_handler(websocket):
    simulation_engine = SimulationEngine(websocket)
    simulation_engine.network_setup()
    knowledge_router = KnowledgeRouter()
    knowledge_router.import_routes(simulation_engine)
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
            elif layer == "knowledge_layer" and command == "query_knowledge":
                await websocket.send(
                    json.dumps(
                        {
                            "layer": "knowledge_layer",
                            "command": "query_knowledge",
                            "response": knowledge_router.query_knowledge(data),
                            "error": None,
                        }
                    )
                )
            elif layer == "intelligence_layer" and command == "chat":
                # by default the data is the chat history with the new user input
                chat_agent_streamer = Runner.run_streamed(chat_agent, data)

                async for event in chat_agent_streamer.stream_events():
                    # We'll ignore the raw responses event deltas
                    if event.type == "raw_response_event" and isinstance(
                        event.data, ResponseTextDeltaEvent
                    ):
                        # print(event.data.delta, end="", flush=True)
                        await websocket.send(
                            json.dumps(
                                {
                                    "layer": "intelligence_layer",
                                    "command": "chat_event_stream",
                                    "response": {
                                        "event_type": "response_text_delta_event",
                                        "response_text_delta": event.data.delta,
                                    },
                                    "error": None,
                                }
                            )
                        )
                    # When the agent updates, print that
                    elif event.type == "agent_updated_stream_event":
                        # print(f"Agent updated: {event.new_agent.name}")
                        await websocket.send(
                            json.dumps(
                                {
                                    "layer": "intelligence_layer",
                                    "command": "chat_event_stream",
                                    "response": {
                                        "event_type": "agent_updated_stream_event",
                                        "agent_name": event.new_agent.name,
                                    },
                                    "error": None,
                                }
                            )
                        )
                    # When items are generated, print them
                    elif event.type == "run_item_stream_event":
                        if event.item.type == "tool_call_item" and isinstance(
                            event.item.raw_item, ResponseFunctionToolCall
                        ):
                            # print("-- Tool was called")
                            await websocket.send(
                                json.dumps(
                                    {
                                        "layer": "intelligence_layer",
                                        "command": "chat_event_stream",
                                        "response": {
                                            "event_type": "tool_call_item",
                                            "tool_name": event.item.raw_item.name,
                                            "tool_args": event.item.raw_item.arguments,
                                        },
                                        "error": None,
                                    }
                                )
                            )
                        elif event.item.type == "tool_call_output_item":
                            # print(f"-- Tool output: {event.item.output}")
                            await websocket.send(
                                json.dumps(
                                    {
                                        "layer": "intelligence_layer",
                                        "command": "chat_event_stream",
                                        "response": {
                                            "event_type": "tool_call_output_item",
                                            "tool_output": event.item.raw_item[
                                                "output"
                                            ],
                                        },
                                        "error": None,
                                    }
                                )
                            )
                        elif event.item.type == "message_output_item":
                            # print(
                            #     f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}"
                            # )
                            await websocket.send(
                                json.dumps(
                                    {
                                        "layer": "intelligence_layer",
                                        "command": "chat_event_stream",
                                        "response": {
                                            "event_type": "message_output_item",
                                            "message_output": ItemHelpers.text_message_output(
                                                event.item
                                            ),
                                        },
                                        "error": None,
                                    }
                                )
                            )
                        else:
                            pass  # Ignore other event types

                    # await websocket.send(
                    #     json.dumps(
                    #         {
                    #             "layer": "intelligence_layer",
                    #             "command": "chat",
                    #             "response": chat_agent_response.final_output,
                    #             "error": None,
                    #         }
                    #     )
                    # )
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
