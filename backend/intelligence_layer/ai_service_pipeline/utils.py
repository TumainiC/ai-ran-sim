def prepare_ai_service_deployment_data(knowledge_router, ai_service_name: str) -> str:
    """Prepare the data for AI service deployment agent

    This is called after the user has selected the AI service to deploy.
    The function will query the network knowledge database to get as much information as possible
    relevant about deploying the selected AI service at different edge clusters available in the network.

    It will format the information in a long string and will be appended to the chat messages as the context
    for the AI service deployment agent. The agent will then use this information as the basis when chatting with the user
    and helping the user to deploy the AI services.

    Args:
        ai_service_name (str): The name of the AI service to deploy.
        ai_service_description (str): The description of the AI service.

    Returns:
        dict: A dictionary containing the AI service name and description.
    """

    ai_service_raw_data = knowledge_router.query_knowledge(
        f"/ai_services/{ai_service_name}/raw"
    )

    print(f"AI service raw data: {ai_service_raw_data}")

    # return {
    #     "ai_service_name": ai_service_name,
    #     "ai_service_description": ai_service_description,
    # }

    return ""
