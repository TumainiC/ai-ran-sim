import json

from agents import Agent, FunctionTool, RunContextWrapper, function_tool


from knowledge_layer import KnowledgeRouter

knowledge_router = KnowledgeRouter()  # get the singleton instance of KnowledgeRouter


@function_tool
async def get_knowledge_value(knowledge_query_key: str) -> str:
    """Get the knowledge value of a specific key in the network knowledge database.

    Args:
        knowledge_query_key (str): The key to query in the knowledge layer.
    """
    return knowledge_router.get_value(knowledge_query_key)


@function_tool
async def get_knowledge_explanation(knowledge_query_key: str) -> str:
    """Get the explanation of a specific key in the network knowledge database.

    Args:
        knowledge_query_key (str): The key to query in the knowledge layer.
    """
    return knowledge_router.explain_value(knowledge_query_key)


@function_tool
async def get_knowledge_value_bulk(knowledge_query_key_list: list[str]) -> str:
    """Get the knowledge values of a list of keys in the network knowledge database.

    Args:
        knowledge_query_key_list (list[str]): The list of keys to query in the knowledge layer.
    """

    response_text = ""

    for knowledge_query_key in knowledge_query_key_list:
        if knowledge_query_key.trim():
            response_text += f"Query {knowledge_query_key} response: \n{knowledge_router.get_value(knowledge_query_key)}\n"

    return response_text


@function_tool
async def get_knowledge_explanation_bulk(knowledge_query_key_list: list[str]) -> str:
    """Get the explanations of a list of keys in the network knowledge database.

    Args:
        knowledge_query_key_list (list[str]): The list of keys to query in the knowledge layer.
    """

    response_text = ""

    for knowledge_query_key in knowledge_query_key_list:
        if knowledge_query_key.trim():
            response_text += f"Query {knowledge_query_key} explanation: \n{knowledge_router.explain_value(knowledge_query_key)}\n"

    return response_text
