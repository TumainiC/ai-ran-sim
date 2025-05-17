from agents import Agent
from .network_knowledge_tools import (
    get_knowledge_value,
    get_knowledge_explanation,
    get_knowledge_value_bulk,
    get_knowledge_explanation_bulk,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX


network_knowledge_agent = Agent(
    name="Telecom Network Knowledge Assistant",
    handoff_description="Specialist agent for querying the telecom network knowledge database using tools",
    tools=[
        get_knowledge_value,
        get_knowledge_explanation,
        get_knowledge_value_bulk,
        get_knowledge_explanation_bulk,
    ],
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
Use the tools to query the network knowledge database. To get started:
    call get_knowledge_explanation("/net")

To increase efficiency, you can use the bulk query tools to query multiple keys at once.
""",
)


# backup prompt template
"""
All knowledge entries in the database can be queried using URL-like query keys, e.g.,
    * To get the live attribute value of a user equipment: 
        call get_knowledge_value("/net/ue/attribute/{{ue_imsi}}/{{attribute_name}}")
    * To get the explanation of an user equipment attribute or method:
        call get_knowledge_explanation("/net/ue/attribute/{{attribute_name}}")
        call get_knowledge_explanation("/net/ue/method/{{method_name}}")

The above query approaches can also be used to query the cell knowledge database, 
simply replace "/net/ue" with "/net/cell" in the query key.
If you don't know the supported UE/Cell attributes or methods, you can first 
    call get_knowledge_explanation("/net/ue")
    or call get_knowledge_explanation("/net/cell")
"""
