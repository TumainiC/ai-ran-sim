from .knowledge_router import KnowledgeRouter
from .knowledge_getter import _getter_registry
from .knowledge_explainer import _explainer_registry

from .knowledge_sources import *  # do not remove this import, it is to import all the getters and explainers.


def initialize_knowledge_router(sim):
    knowledge_router = KnowledgeRouter()

    for reg_key, getter_func in _getter_registry.items():

        def wrapped_getter(query_key, params, f=getter_func):
            return f(sim, knowledge_router, query_key, params)

        knowledge_router.register_route(
            pattern=reg_key,
            getter=wrapped_getter,
        )

    for reg_key, explainer_entry in _explainer_registry.items():

        explainer_func = explainer_entry["func"]
        tags = explainer_entry["tags"]
        related = explainer_entry["related"]

        def wrapped_explainer(query_key, params, f=explainer_func):
            return (
                f(sim, knowledge_router, query_key, params)
                if f
                else f"No explanation for key: {query_key}"
            )

        knowledge_router.register_route(
            pattern=reg_key,
            explainer=wrapped_explainer,
            tags=tags,
            related=related,
        )
    return knowledge_router
