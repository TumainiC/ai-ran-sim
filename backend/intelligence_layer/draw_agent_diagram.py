from agents.extensions.visualization import draw_graph

from intelligence_layer.chat_agent import network_chat_agent


draw_graph(network_chat_agent, filename="agent_graph.dot")
