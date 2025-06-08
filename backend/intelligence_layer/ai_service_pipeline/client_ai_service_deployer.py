import asyncio
from utils import WebSocketSingleton, WebSocketResponse

from agents import Agent, function_tool
from ..knowledge_tools import get_knowledge, get_knowledge_bulk
from settings import OPENAI_NON_REASONING_MODEL_NAME
from knowledge_layer import KnowledgeRouter
from network_layer.simulation_engine import SimulationEngine


@function_tool
def deploy_ai_service(ai_service_name: str, ue_ids: list[str]) -> str:
    """Deploys an AI service for specified User Equipment (UE) IDs.

    Args:
        ai_service_name (str): The name of the AI service to deploy.
        ue_ids (list[str]): A list of User Equipment IDs in the format `IMSI_<digits>`.
    """
    websocket = WebSocketSingleton().get_websocket()
    simulation_engine = SimulationEngine()

    if websocket is None:
        print("WebSocket is not available.")
        return "Websocket connection with the frontend is not available."

    # ai_service_descriptions = [
    #     knowledge_router.query_knowledge(f"/ai_services/{name}")
    #     for name in ai_service_names
    # ]

    # response = WebSocketResponse(
    #     layer="intelligence_layer",
    #     command="ai_service_pipeline_response",
    #     response={
    #         "event_type": "ai_services_recommendation",
    #         "ai_service_names": ai_service_names,
    #         "ai_service_descriptions": ai_service_descriptions,
    #     },
    #     error=None,
    # )
    # asyncio.create_task(websocket.send(response.to_json()))

    return "AI services recommendation sent to the user."


client_ai_service_deployer = Agent(
    name="Client AI Service Deployer Assistant",
    handoff_description="Specialist agent for deploying AI services across our network's edge clusters.",
    tools=[
        deploy_ai_service,
    ],
    instructions=f"""You're the second step in helping users to select and deploy the right AI services for their devices or applications connected to our simulated network.

The user has just selected the AI service for deployment.
You follow steps below to complete your task:

1. Ask the user for his/her User Equipment IDs. The UE IDs are in the format of `IMSI_<digits>`, where `<digits>` is a sequence of digits. The user can provide multiple UE IDs.
2. Call the `deploy_ai_service` function tool with the selected AI service name and the provided UE IDs.
    """,
)
