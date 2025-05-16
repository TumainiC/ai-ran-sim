import asyncio
import random
from agents import Agent, ItemHelpers, Runner, function_tool
from openai.types.responses import ResponseTextDeltaEvent
import dotenv
dotenv.load_dotenv()

@function_tool
def how_many_jokes() -> int:
    return random.randint(1, 3)


async def main():
    agent = Agent(
        name="Joker",
        instructions="First call the `how_many_jokes` tool, then tell that many jokes.",
        tools=[how_many_jokes],
    )

    result = Runner.run_streamed(
        agent,
        input="Hello",
    )
    print("=== Run starting ===")
    event_history = []
    async for event in result.stream_events():
        event_history.append(event)

        # We'll ignore the raw responses event deltas
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
        # When the agent updates, print that
        elif event.type == "agent_updated_stream_event":
            print(f"Agent updated: {event.new_agent.name}")
            continue
        # When items are generated, print them
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                print("-- Tool was called")
            elif event.item.type == "tool_call_output_item":
                print(f"-- Tool output: {event.item.output}")
            elif event.item.type == "message_output_item":
                print(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
            else:
                pass  # Ignore other event types

    print("=== Run complete ===")
    print("Event history:")

    for event in event_history:
        print("---- New EVENT ----")
        if getattr(event, "type", None) is not None:
            print(f"Event type:")
            print(event.type)
        if getattr(event, "new_agent", None) is not None:
            print(f"Event new agent:")
            print(event.new_agent)
        if getattr(event, "data", None) is not None:
            print(f"Event data:")
            print(event.data)
        if getattr(event, "item", None) is not None:
            print(f"Event item:")
            print(event.item)
        print("\n\n")

if __name__ == "__main__":
    asyncio.run(main())