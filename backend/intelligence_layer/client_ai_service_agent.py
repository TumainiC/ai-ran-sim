from agents import Agent
from .knowledge_tools import get_knowledge, get_knowledge_bulk
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from settings import OPENAI_NON_REASONING_MODEL_NAME


client_ai_service_agent = Agent(
    name="Client AI Service Assistant",
    handoff_description="Specialist agent for selecting and deploying AI serivces for network clients/users.",
    tools=[
        get_knowledge,
        get_knowledge_bulk,
    ],
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}

You're equipped with an AI service knowledge base, containg ready-to-deploy AI services across our simulated network.
The "get knowledge (bulk)" tools allow you to query the AI service database containing ready-to-deploy AI services across our simulated network.
To increase efficiency, you can use the bulk query tools to query multiple keys at once.

Always use the knowledge from the AI services knowledge base to answer user requests or questions.

You should start with the following query key:
    "/docs/ai_services", which will guide you to better explore the AI services knowledge base.
""",
    model=OPENAI_NON_REASONING_MODEL_NAME,
)
