from agents import Agent


network_knowledge_agent = Agent(
    name="Network Knowledge Assistant",
    handoff_description="Specialist agent for querying the network knowledge database using tools",
    instructions="You answer user's or other agent assistants' questions by exploring the knowledge in the network knowledge database with given tools",
)