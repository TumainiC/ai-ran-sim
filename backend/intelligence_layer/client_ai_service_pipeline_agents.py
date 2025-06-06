import asyncio
from utils import stream_agent_chat, WebSocketSingleton, WebSocketResponse

from agents import Agent, function_tool
from .knowledge_tools import get_knowledge, get_knowledge_bulk
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from settings import OPENAI_NON_REASONING_MODEL_NAME
from knowledge_layer import KnowledgeRouter
from network_layer.simulation_engine import SimulationEngine


STEP_SERVICE_NEED_PROFILING = "step_service_need_profiling"
STEP_SERVICE_DEPLOYMENT = "step_service_deployment"
STEP_NETWORK_ADAPTATION = "step_network_adaptation"
STEP_SERVICE_MONITORING = "step_service_monitoring"


@function_tool
def recommend_ai_services(ai_service_names: list[str]) -> str:
    """Recommend AI services for the user to select from.

    Args:
        ai_service_names (list[str]): A list of AI service names to recommend.
    """

    knowledge_router = KnowledgeRouter()
    websocket = WebSocketSingleton().get_websocket()

    if websocket is None:
        print("WebSocket is not available.")
        return "Websocket connection with the frontend is not available."

    ai_service_descriptions = [
        knowledge_router.query_knowledge(f"/ai_services/{name}")
        for name in ai_service_names
    ]

    response = WebSocketResponse(
        layer="intelligence_layer",
        command="ai_service_pipeline_response",
        response={
            "event_type": "ai_services_recommendation",
            "ai_service_names": ai_service_names,
            "ai_service_descriptions": ai_service_descriptions,
        },
        error=None,
    )
    asyncio.create_task(websocket.send(response.to_json()))

    return "AI services recommendation sent to the user."


# client_ai_service_deployer = Agent(
#     name="Client AI Service Deployer Assistant",
#     handoff_description="Specialist agent for deploying AI services to devices and applications.",
#     tools=[
#         get_knowledge,
#         get_knowledge_bulk,
#     ],
#     instructions=f"""{RECOMMENDED_PROMPT_PREFIX}

# You're the second step in helping users to select and deploy the right AI services for their devices and applications connected to our simulated network.

# Currently our telecom network has four base stations at different locations, each with its own edge AI service capabilities.

# Your job is to chat with the user to find the maximum operational region (in terms of min_x, max_x, min_y, max_y, in meters)

# When the user confirms a suitable AI service, you should hand off to the "Client AI Service Deployer Assistant" agent,
# which will handle the deployment of the selected AI service to the user's device or application.

#     """,
# )

client_ai_service_need_profiler = Agent(
    name="Client AI Service Need Profiler Assistant",
    handoff_description="Specialist agent for understanding user's real AI service needs and intentions.",
    tools=[
        get_knowledge,
        get_knowledge_bulk,
        recommend_ai_services,
    ],
    # instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    instructions=f"""You're the the first step in helping users to select and deploy the right AI services for their devices and applications connected to our simulated network.

You're equipped with an AI service knowledge base, containg ready-to-deploy AI services across our simulated network.
The "get knowledge (bulk)" tools allow you to query the AI service database containing ready-to-deploy AI services across our simulated network.
To increase efficiency, you can use the bulk query tools to query multiple keys at once.

Always use the knowledge from the AI services knowledge base to answer user requests or questions.
You can start with the query key "/docs/ai_services" for the guidance to better explore the AI services knowledge base.  

Your job is to chat with the user and guide the user to find a suitable AI service in our knowledge base for their needs.

Use the tool `recommend_ai_services` to recommend AI services based on the user's needs and preferences to allow the user to select from a list of AI services.
""",
    model=OPENAI_NON_REASONING_MODEL_NAME,
)


async def handle_ai_service_pipeline(
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
    else:
        return f"Error: Unsupported step '{current_step}' in AI service pipeline."
