from typing import Optional, List, Tuple
from .relationships import KnowledgeRelationship
from .routing import KnowledgeRouter

knowledge_router = KnowledgeRouter()
_getter_registry = {}
_explainer_registry = {}


def knowledge_getter(
    key: str,
):
    def decorator(func):
        _getter_registry[key] = func
        return func

    return decorator


def knowledge_explainer(
    key: str,
    tags: Optional[List[str]] = None,
    related: Optional[List[Tuple[KnowledgeRelationship, str]]] = None,
):
    def decorator(func):
        _explainer_registry[key] = {
            "func": func,
            "tags": tags or [],
            "related": related or [],
        }
        return func

    return decorator


def register_knowledge_routes(sim):
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
