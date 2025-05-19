import os
from agents import set_default_openai_key
from agents import set_tracing_disabled

set_default_openai_key(os.environ.get("OPENAI_API_KEY", ""))
set_tracing_disabled(True)

from .chat_agent import chat_agent
