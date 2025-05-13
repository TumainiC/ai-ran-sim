from typing import Optional, List, Tuple
from .relationships import Relationship
from .routing import KnowledgeRouter

knowledge_router = KnowledgeRouter()
_getter_registry = {}
_explainer_registry = {}


def knowledge_getter(
    key: str,
    tags: Optional[List[str]] = None,
    related: Optional[List[Tuple[str, Relationship]]] = None,
):
    def decorator(func):
        _getter_registry[key] = {
            "func": func,
            "tags": tags or [],
            "related": related or [],
        }
        return func

    return decorator


def knowledge_explainer(key: str):
    def decorator(func):
        _explainer_registry[key] = func
        return func

    return decorator


def register_knowledge_routes(sim):
    for key, entry in _getter_registry.items():
        getter_func = entry["func"]
        explainer_func = _explainer_registry.get(key)

        def wrapped_getter(params, f=getter_func):
            return f(key, sim, params)

        def wrapped_explainer(value, params, f=explainer_func):
            return f(key, sim, params) if f else f"No explanation for key: {key}"

        knowledge_router.register_route(
            pattern=key,
            getter=wrapped_getter,
            explainer=wrapped_explainer if explainer_func else None,
            tags=entry["tags"],
            related=entry["related"],
        )
