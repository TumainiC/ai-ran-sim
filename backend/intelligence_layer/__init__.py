import os
from agents import set_default_openai_key

set_default_openai_key(os.environ.get("OPENAI_API_KEY"))


from .chat_agent import chat_agent
