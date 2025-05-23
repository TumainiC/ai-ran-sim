import asyncio
import websockets
import json
from intelligence_layer.chat_agent import user_chat_agent_function
import settings
from agents import ItemHelpers
from network_layer.simulation_engine import SimulationEngine
from openai.types.responses import ResponseTextDeltaEvent, ResponseFunctionToolCall
from utils import setup_logging
from knowledge_layer import KnowledgeRouter
from agents import Runner
import dotenv

dotenv.load_dotenv()
from intelligence_layer import network_chat_agent

setup_logging()


class WebSocketResponse:
    def __init__(self, layer=None, command=None, response=None, error=None):
        self.layer = layer
        self.command = command
        self.response = response
        self.error = error

    def to_json(self):
        return json.dumps(
            {
                "layer": self.layer,
                "command": self.command,
                "response": self.response,
                "error": self.error,
            }
        )


async def handle_start_simulation(websocket, simulation_engine, knowledge_router, data):
    response = WebSocketResponse(
        layer="network_layer",
        command="start_simulation",
        response="Starting simulation",
        error=None,
    )
    await websocket.send(response.to_json())
    asyncio.create_task(simulation_engine.start_simulation())


async def handle_stop_simulation(websocket, simulation_engine, knowledge_router, data):
    response = WebSocketResponse(
        layer="network_layer",
        command="stop_simulation",
        response="Stopping simulation",
        error=None,
    )
    await websocket.send(response.to_json())
    simulation_engine.stop()


async def handle_get_simulation_state(
    websocket, simulation_engine, knowledge_router, data
):
    response = WebSocketResponse(
        layer="network_layer",
        command="get_simulation_state",
        response=simulation_engine.to_json(),
        error=None,
    )
    await websocket.send(response.to_json())


async def handle_get_routes(websocket, simulation_engine, knowledge_router, data):
    response = WebSocketResponse(
        layer="knowledge_layer",
        command="get_routes",
        response=knowledge_router.get_routes(),
        error=None,
    )
    await websocket.send(response.to_json())


async def handle_query_knowledge(websocket, simulation_engine, knowledge_router, data):
    response = WebSocketResponse(
        layer="knowledge_layer",
        command="query_knowledge",
        response=knowledge_router.query_knowledge(data),
        error=None,
    )
    await websocket.send(response.to_json())


async def handle_user_chat(websocket, simulation_engine, knowledge_router, data):
    result = await user_chat_agent_function(data)
    response = WebSocketResponse(
        layer="intelligence_layer",
        command="chat_event_stream",
        response={"event_type": "message_output_item", "message_output": result},
        error=None,
    )
    await websocket.send(response.to_json())


# --- Helper functions for network_engineer_chat event types ---


async def send_response_text_delta_event(websocket, delta):
    response = WebSocketResponse(
        layer="intelligence_layer",
        command="chat_event_stream",
        response={
            "event_type": "response_text_delta_event",
            "response_text_delta": delta,
        },
        error=None,
    )
    await websocket.send(response.to_json())


async def send_agent_updated_event(websocket, agent_name):
    response = WebSocketResponse(
        layer="intelligence_layer",
        command="chat_event_stream",
        response={
            "event_type": "agent_updated_stream_event",
            "agent_name": agent_name,
        },
        error=None,
    )
    await websocket.send(response.to_json())


async def send_tool_call_item_event(websocket, tool_name, tool_args):
    response = WebSocketResponse(
        layer="intelligence_layer",
        command="chat_event_stream",
        response={
            "event_type": "tool_call_item",
            "tool_name": tool_name,
            "tool_args": tool_args,
        },
        error=None,
    )
    await websocket.send(response.to_json())


async def send_tool_call_output_item_event(websocket, tool_output):
    response = WebSocketResponse(
        layer="intelligence_layer",
        command="chat_event_stream",
        response={
            "event_type": "tool_call_output_item",
            "tool_output": tool_output,
        },
        error=None,
    )
    await websocket.send(response.to_json())


async def send_message_output_item_event(websocket, message_output):
    response = WebSocketResponse(
        layer="intelligence_layer",
        command="chat_event_stream",
        response={
            "event_type": "message_output_item",
            "message_output": message_output,
        },
        error=None,
    )
    await websocket.send(response.to_json())


# --- Main handler for network_engineer_chat ---


async def handle_network_engineer_chat(
    websocket, simulation_engine, knowledge_router, data
):
    """
    Handles the 'network_engineer_chat' command by streaming events and dispatching
    each event type to its own helper function for clarity and maintainability.
    """
    chat_agent_streamer = Runner.run_streamed(network_chat_agent, data)
    async for event in chat_agent_streamer.stream_events():
        if event.type == "raw_response_event" and isinstance(
            event.data, ResponseTextDeltaEvent
        ):
            await send_response_text_delta_event(websocket, event.data.delta)
        elif event.type == "agent_updated_stream_event":
            await send_agent_updated_event(websocket, event.new_agent.name)
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item" and isinstance(
                event.item.raw_item, ResponseFunctionToolCall
            ):
                await send_tool_call_item_event(
                    websocket,
                    tool_name=event.item.raw_item.name,
                    tool_args=event.item.raw_item.arguments,
                )
            elif event.item.type == "tool_call_output_item":
                await send_tool_call_output_item_event(
                    websocket, tool_output=event.item.raw_item["output"]
                )
            elif event.item.type == "message_output_item":
                await send_message_output_item_event(
                    websocket,
                    message_output=ItemHelpers.text_message_output(event.item),
                )
            # else: ignore other event types


COMMAND_HANDLERS = {
    ("network_layer", "start_simulation"): handle_start_simulation,
    ("network_layer", "stop_simulation"): handle_stop_simulation,
    ("network_layer", "get_simulation_state"): handle_get_simulation_state,
    ("knowledge_layer", "get_routes"): handle_get_routes,
    ("knowledge_layer", "query_knowledge"): handle_query_knowledge,
    ("intelligence_layer", "network_user_chat"): handle_user_chat,
    ("intelligence_layer", "network_engineer_chat"): handle_network_engineer_chat,
}


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
            response = WebSocketResponse(
                layer=None, command=None, response=None, error="Invalid message format"
            )
            await websocket.send(response.to_json())
            continue

        try:
            handler = COMMAND_HANDLERS.get((layer, command))
            if handler:
                await handler(
                    websocket=websocket,
                    simulation_engine=simulation_engine,
                    knowledge_router=knowledge_router,
                    data=data,
                )
            else:
                response = WebSocketResponse(
                    layer=layer, command=command, response=None, error="Unknown command"
                )
                await websocket.send(response.to_json())
        except Exception as e:
            response = WebSocketResponse(
                layer=layer, command=command, response=None, error=str(e)
            )
            await websocket.send(response.to_json())


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
