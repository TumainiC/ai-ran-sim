import os
from agents import Agent
from .network_knowledge_tools import get_knowledge, get_knowledge_bulk
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX


REASONING_MODEL = os.getenv("OPENAI_REASONING_MODEL_NAME", "gpt-4o")
NON_REASONING_MODEL = os.getenv("OPENAI_NON_REASONING_MODEL_NAME", "gpt-4o")

print(f"Using reasoning model: {REASONING_MODEL}")
print(f"Using non-reasoning model: {NON_REASONING_MODEL}")


non_reasoning_network_knowledge_agent = Agent(
    name="Basic Network Knowledge Assistant",
    handoff_description="Specialist agent for querying the telecom network knowledge database using tools",
    tools=[
        get_knowledge,
        get_knowledge_bulk,
    ],
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
Use the tools to query the knowledge database of the simulated telecom network. 
To increase efficiency, you can use the bulk query tools to query multiple keys at once.
You should always start with  
    "/docs/user_equipments" (for detailed UE knowledge base documentation) 

The knowledge tools often returns a list of related knowledge keys. 
You should explore these related knowledge keys as well to gather more information to answer the user query wherever possible.
""",
    model=NON_REASONING_MODEL,
)

#     instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
# Use the tools to query the knowledge database of the simulated telecom network.
# To increase efficiency, you can use the bulk query tools to query multiple keys at once.
# You should always query
#     "/net" (for network simulation related knowledge, such as list of UEs, Cells and Base Stations),
#     "/net/user_equipments" (for simulated UE class and instance related knowledge), or
#     "/net/cell" (for simulated Cell class and instance related knowledge) or
#     "/net/base_station" (for simulated BaseStation class and instance related knowledge)
#     "/net/ric" (for simulated NearRT RIC class and instance related knowledge)
# first to get the list of supported attributes and methods.

# The knowledge explanation tools often returns a list of related knowledge keys.
# You should explore these related knowledge keys as well to gather more information to answer the user query.
# """,


reasoning_network_knowledge_agent = Agent(
    name="Advanced Network Knowledge Assistant",
    handoff_description="Specialist agent for querying the telecom network knowledge database using tools",
    tools=[
        get_knowledge,
        get_knowledge_bulk,
    ],
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
Use the tools to query the knowledge database of the simulated telecom network. 
To increase efficiency, you can use the bulk query tools to query multiple keys at once.
You should always start with  
    "/net/user_equipments/help" (for detailed UE knowledge base documentation) 

The knowledge tools often returns a list of related knowledge keys. 
You should explore these related knowledge keys as well to gather more information to answer the user query wherever possible.
""",
    model=NON_REASONING_MODEL,
)
