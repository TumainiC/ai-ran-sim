from agents import Agent
from .network_knowledge_agent import network_knowledge_agent


chat_agent = Agent(
    name="Chat Assistant",
    instructions="You chat with the user and route user queries to the appropriate specialist agent.",
    handoffs=[network_knowledge_agent],
)
