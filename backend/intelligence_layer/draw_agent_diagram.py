from agents.extensions.visualization import draw_graph

from intelligence_layer.chat_agent import chat_agent


draw_graph(chat_agent, filename="agent_graph.dot")
