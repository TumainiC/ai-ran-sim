from typing import Optional, List, Tuple
from .relationships import KnowledgeRelationship

_explainer_registry = {}


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
