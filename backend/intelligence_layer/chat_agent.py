from functools import cache
from agents import Agent, ModelSettings, RunConfig, Runner
from openai.types.responses import ResponseTextDeltaEvent
from .network_knowledge_agent import (
    non_reasoning_network_knowledge_agent,
    reasoning_network_knowledge_agent,
)
from .user_chat.model_recommender_agents import model_recommender_orchestrator

@cache
def get_config():
    model_settings=ModelSettings(
        temperature=0,   
    )
    return RunConfig(model_settings=model_settings, model="gpt-4.1")



network_chat_agent = Agent(
    name="Network Assistant",
    instructions="""You chat with the network engineers and route network engineer queries to the appropriate specialist agent.
    If you need knowledge from the simulated telecom network, 
    you should always route the network engineer query to the basic network network assistant first 
    as it's using non-reasoning LLM model and thus cheaper and fast.
    If the basic knowledge assistant is not able to answer the network engineer query, 
    you should route the network engineer query to the advanced knowledge assistant agent to try again.""",
    handoffs=[non_reasoning_network_knowledge_agent, reasoning_network_knowledge_agent],
)


user_chat_agent = Agent(
    name = "User Assistant",
    instructions= """
    You interact directly with end users of the network. Users may request various tasks. There are two specific requests to handle as follows:

        1. Create new UE (User Equipment), also known as SIM
            - Always hand off to a suitable agent.
            - Do not attempt to fulfill this request yourself.

        2. Provide a model recommendation
            - Always hand off to a suitable agent.
            - Do not attempt to fulfill this request yourself.

        Your Responsibilities:
            - For the two tasks above: Immediately transfer the conversation to an agent.
            - For all other general user queries: Handle and clarify these yourself. Do not hand off to an agent.
    """,
    handoffs = [model_recommender_orchestrator]
)


async def user_chat_agent_function(data):
    """This function receives the user request sychronously, because it may require parsing in the ui to render"""
    print(data)
    agent = user_chat_agent
    result =  Runner.run_streamed(agent, data , run_config=get_config())
    collected = []
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end = " ", flush=True)
            collected.append(event.data.delta)
    result = "".join(collected)
    return result