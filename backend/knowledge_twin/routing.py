import re
from typing import Callable, Dict, List, Tuple, Optional
from .relationships import KnowledgeRelationship


class KnowledgeRoute:
    def __init__(
        self,
        pattern: str,
        getter: Optional[Callable] = None,
        explainer: Optional[Callable] = None,
        tags: Optional[List[str]] = None,
        related: Optional[List[Tuple[KnowledgeRelationship, str]]] = None,
    ):
        self.pattern = pattern
        self.regex, self.param_names = self._compile_pattern(pattern)
        self.getter = getter
        self.explainer = explainer
        self.tags = tags or []
        self.related = related or []

    def _compile_pattern(self, pattern: str):
        param_names = []
        regex_pattern = re.sub(
            r"\{(\w+)\}", lambda m: self._param_replacer(m, param_names), pattern
        )
        return re.compile(f"^{regex_pattern}$"), param_names

    def _param_replacer(self, match, param_names):
        name = match.group(1)
        param_names.append(name)
        return f"(?P<{name}>[^/]+)"

    def match(self, key: str):
        match = self.regex.match(key)
        return match.groupdict() if match else None


class KnowledgeRouter:
    def __init__(self):
        self.getter_routes: List[KnowledgeRoute] = []
        self.explainer_routes: List[KnowledgeRoute] = []

    def register_route(
        self,
        pattern: str,
        getter: Optional[Callable] = None,
        explainer: Optional[Callable] = None,
        tags: Optional[List[str]] = None,
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
            if params:
                return route, params
        raise KeyError(f"No route found for key: {key}")

    def _find_explainer_route(self, key: str) -> Tuple[KnowledgeRoute, Dict[str, str]]:
        for route in self.explainer_routes:
            params = route.match(key)
            if params:
                return route, params
        raise KeyError(f"No route found for key: {key}")

    def get_value(self, query_key: str):
        route, params = self._find_getter_route(query_key)
        return route.getter(query_key, params)

    def explain_value(self, key: str):
        route, params = self._find_explainer_route(key)
        if route.explainer:
            return route.explainer(key, params)
        return f"No explanation available for key: {key}"
