from agents import Agent
from .network_knowledge_agent import (
    non_reasoning_network_knowledge_agent,
    reasoning_network_knowledge_agent,
)


chat_agent = Agent(
    name="Chat Assistant",
    instructions="""You chat with the user and route user queries to the appropriate specialist agent.
If you need knowledge from the simulated telecom network, 
you should always route the user query to the basic network network assistant first 
as it's using non-reasoning LLM model and thus cheaper and fast.
If the basic knowledge assistant is not able to answer the user query, 
you should route the user query to the advanced knowledge assistant agent to try again.""",
    handoffs=[non_reasoning_network_knowledge_agent, reasoning_network_knowledge_agent],
)
