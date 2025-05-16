from agents import Agent
from .network_knowledge_tools import (
    get_knowledge_value,
    get_knowledge_explanation,
    get_knowledge_value_bulk,
    get_knowledge_explanation_bulk,
)


network_knowledge_agent = Agent(
    name="Telecom Network Knowledge Assistant",
    handoff_description="Specialist agent for querying the telecom network knowledge database using tools",
    tools=[
        get_knowledge_value,
        get_knowledge_explanation,
        get_knowledge_value_bulk,
        get_knowledge_explanation_bulk,
    ],
    instructions="""Use the tools to query the network knowledge database.

All knowledge entries in the database can be queried using URL-like query keys.
    * To get an attribute value of a user equipment: 
        call get_knowledge_value("/net/ue/attribute/<user_equipment_id>/<attribute_name>")
    * To get the explanation of an user equipment attribute:
        call get_knowledge_explanation("/net/ue/attribute/<user_equipment_id>/<attribute_name>")
    * To get the source code of a function defined in the simulated user equipment class:
        call get_knowledge_value("/net/ue/method/<function_name>")
    * To get the explanation of the function logic in the simulated user equipment class:
        call get_knowledge_explanation("/net/ue/method/<function_name>")

If you don't know the supported UE attributes or methods, you can first call get_knowledge_explanation("/net/ue")

To get started if you wish to explore the knowledge database:
        call get_knowledge_value("/net")
        or call get_knowledge_explanation("/net")
""",
)
