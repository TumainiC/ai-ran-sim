from typing import Callable, Dict, List, Tuple, Optional
from .relationships import KnowledgeRelationship
from .tags import KnowledgeTag
from .knowledge_route import KnowledgeRoute
import utils
from .knowledge_getter import _getter_registry
from .knowledge_explainer import _explainer_registry
from .knowledge_sources import *  # do not remove this import, it is to import all the getters and explainers.


class KnowledgeRouter(metaclass=utils.SingletonMeta):
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

    def import_routes(self, sim=None):

        for reg_key, getter_func in _getter_registry.items():

            def wrapped_getter(query_key, params, f=getter_func):
                return f(sim, self, query_key, params)

            self.register_route(
                pattern=reg_key,
                getter=wrapped_getter,
            )

        for reg_key, explainer_entry in _explainer_registry.items():

            explainer_func = explainer_entry["func"]
            tags = explainer_entry["tags"]
            related = explainer_entry["related"]

            def wrapped_explainer(query_key, params, f=explainer_func):
                return (
                    f(sim, self, query_key, params)
                    if f
                    else f"No explanation for key: {query_key}"
                )

            self.register_route(
                pattern=reg_key,
                explainer=wrapped_explainer,
                tags=tags,
                related=related,
            )

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
