import asyncio
import json
from utils import stream_agent_chat

from .client_ai_service_need_profiler import client_ai_service_need_profiler
from .client_ai_service_deployer import client_ai_service_deployer

from .constants import (
    STEP_SERVICE_NEED_PROFILING,
    STEP_SERVICE_DEPLOYMENT,
    STEP_NETWORK_ADAPTATION,
    STEP_SERVICE_MONITORING,
)


async def handle_ai_service_pipeline_chat(
    websocket, simulation_engine, knowledge_router, data
):
    current_step = data.get("current_step", None)
    messages = data.get("messages", [])

    if current_step is None:
        return "Error: 'current_step' is required in the data."
    if not messages:
        return "Error: 'messages' cannot be empty."

    print(f"Handling AI service pipeline step {current_step}")
    print(f"last message: {messages[-1]}")

    if current_step == STEP_SERVICE_NEED_PROFILING:
        await stream_agent_chat(
            websocket=websocket,
            simulation_engine=simulation_engine,
            knowledge_router=knowledge_router,
            data=messages,
            command="ai_service_pipeline_response",
            agent_func=client_ai_service_need_profiler,
        )
    elif current_step == STEP_SERVICE_DEPLOYMENT:
        await stream_agent_chat(
            websocket=websocket,
            simulation_engine=simulation_engine,
            knowledge_router=knowledge_router,
            data=messages,
            command="ai_service_pipeline_response",
            agent_func=client_ai_service_deployer,
        )
    else:
        return f"Error: Unsupported step '{current_step}' in AI service pipeline."
