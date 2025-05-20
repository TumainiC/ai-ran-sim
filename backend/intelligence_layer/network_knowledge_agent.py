import os
from agents import Agent
from .network_knowledge_tools import (
    get_knowledge_value,
    get_knowledge_explanation,
    get_knowledge_value_bulk,
    get_knowledge_explanation_bulk,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX


REASONING_MODEL = os.getenv("OPENAI_REASONING_MODEL_NAME", "gpt-4o")
NON_REASONING_MODEL = os.getenv("OPENAI_NON_REASONING_MODEL_NAME", "gpt-4o")

print(f"Using reasoning model: {REASONING_MODEL}")
print(f"Using non-reasoning model: {NON_REASONING_MODEL}")


non_reasoning_network_knowledge_agent = Agent(
    name="Basic Network Knowledge Assistant",
    handoff_description="Specialist agent for querying the telecom network knowledge database using tools",
    tools=[
        get_knowledge_value,
        get_knowledge_explanation,
        get_knowledge_value_bulk,
        get_knowledge_explanation_bulk,
    ],
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
Use the tools to query the knowledge database of the simulated telecom network. 
To increase efficiency, you can use the bulk query tools to query multiple keys at once.
You should always query 
    "/sim" (for network simulation related knowledge, such as list of UEs, Cells and Base Stations), 
    "/net/ue" (for simulated UE class and instance related knowledge), or
    "/net/cell" (for simulated Cell class and instance related knowledge) or 
    "/net/base_station" (for simulated BaseStation class and instance related knowledge)
    "/net/ric" (for simulated NearRT RIC class and instance related knowledge)
first to get the list of supported attributes and methods.

The knowledge explanation tools often returns a list of related knowledge keys. 
You should explore these related knowledge keys as well to gather more information to answer the user query.
""",
    model=NON_REASONING_MODEL,
)


reasoning_network_knowledge_agent = Agent(
    name="Advanced Network Knowledge Assistant",
    handoff_description="Specialist agent for querying the telecom network knowledge database using tools",
    tools=[
        get_knowledge_value,
        get_knowledge_explanation,
        get_knowledge_value_bulk,
        get_knowledge_explanation_bulk,
    ],
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
Use the tools to query the knowledge database of the simulated telecom network. 
To increase efficiency, you can use the bulk query tools to query multiple keys at once.
You should always query 
    "/sim" (for overall network simulation related knowledge), 
    "/net/ue" (for simulated UE class related knowledge), or
    "/net/cell" (for simulated Cell class related knowledge) or 
    "/net/base_station" (for simulated BaseStation class related knowledge)
    "/net/ric" (for simulated NearRT RIC class related knowledge)
first to get the list of supported attributes and methods.

The knowledge explanation tools often returns a list of related knowledge keys. 
You should explore these related knowledge keys as well to gather more information to answer the user query.
""",
    model=REASONING_MODEL,
)
