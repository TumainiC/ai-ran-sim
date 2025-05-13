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
        explainer_entry = _explainer_registry.get(reg_key)
        explainer_func = explainer_entry["func"] if explainer_entry else None

        def wrapped_getter(query_key, params, f=getter_func):
            return f(sim, knowledge_router, query_key, params)

        def wrapped_explainer(query_key, params, f=explainer_func):
            return (
                f(sim, knowledge_router, query_key, params)
                if f
                else f"No explanation for key: {query_key}"
            )

        knowledge_router.register_route(
            pattern=reg_key,
            getter=wrapped_getter,
            explainer=wrapped_explainer if explainer_func else None,
            tags=explainer_entry["tags"],
            related=explainer_entry["related"],
        )
