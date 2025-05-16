from typing import Optional, List, Tuple
from .relationships import KnowledgeRelationship
from .tags import KnowledgeTag

explainer_registry = {}


def knowledge_explainer(
    key: str,
    tags: Optional[List[KnowledgeTag]] = None,
    related: Optional[List[Tuple[KnowledgeRelationship, str]]] = None,
):
    def decorator(func):
        explainer_registry[key] = {
            "func": func,
            "tags": tags or [],
            "related": related or [],
        }
        return func

    return decorator
