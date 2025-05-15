from typing import Callable, Dict, List, Tuple, Optional
from .relationships import KnowledgeRelationship
from .tags import KnowledgeTag
from .knowledge_route import KnowledgeRoute


class KnowledgeRouter:
    def __init__(self):
        self.getter_routes: List[KnowledgeRoute] = []
        self.explainer_routes: List[KnowledgeRoute] = []

    def register_route(
        self,
        pattern: str,
        getter: Optional[Callable] = None,
        explainer: Optional[Callable] = None,
        tags: Optional[List[KnowledgeTag]] = None,
        related: Optional[List[Tuple[KnowledgeRelationship, str]]] = None,
    ):
        route = KnowledgeRoute(pattern, getter, explainer, tags, related)
        if getter:
            self.getter_routes.append(route)
        if explainer:
            self.explainer_routes.append(route)

    def _find_getter_route(self, key: str) -> Tuple[KnowledgeRoute, Dict[str, str]]:
        for route in self.getter_routes:
            params = route.match(key)
            if params is not None:
                return route, params
        raise KeyError(f"No route found for key: {key}")

    def _find_explainer_route(self, key: str) -> Tuple[KnowledgeRoute, Dict[str, str]]:
        for route in self.explainer_routes:
            params = route.match(key)
            if params is not None:
                return route, params
        raise KeyError(f"No route found for key: {key}")

    def get_value(self, query_key: str):
        try:
            route, params = self._find_getter_route(query_key)
            return route.getter(query_key, params)
        except KeyError:
            return f"No getter found for key: {query_key}"

    def explain_value(self, query_key: str):
        try:
            route, params = self._find_explainer_route(query_key)
            if route.explainer:
                explanation = route.explainer(query_key, params)
                if route.related:
                    explanation += "\nRelated knowledge:\n"
                    for relationship, related_pattern in route.related:
                        explanation += f"- {relationship.value}: {related_pattern.format(**params)}\n"
                return explanation
        except Exception as e:
            return f"Error explaining value for key {query_key}: {str(e)}"

    def get_routes(self):
        return {
            "getter_routes": [
                {"pattern": route.pattern} for route in self.getter_routes
            ],
            "explainer_routes": [
                {
                    "pattern": route.pattern,
                    "tags": [tag.value for tag in route.tags],
                    "related": [
                        {"relationship": relationship_tag.value, "pattern": pattern}
                        for relationship_tag, pattern in route.related
                    ],
                }
                for route in self.explainer_routes
            ],
        }
