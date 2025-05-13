
import re
from typing import Callable, Dict, List, Tuple, Optional
from .relationships import Relationship

class KnowledgeRoute:
    def __init__(
        self,
        pattern: str,
        getter: Callable[[Dict[str, str]], any],
        explainer: Optional[Callable[[any, Dict[str, str]], str]] = None,
        tags: Optional[List[str]] = None,
        related: Optional[List[Tuple[str, Relationship]]] = None
    ):
        self.pattern = pattern
        self.regex, self.param_names = self._compile_pattern(pattern)
        self.getter = getter
        self.explainer = explainer
        self.tags = tags or []
        self.related = related or []

    def _compile_pattern(self, pattern: str):
        param_names = []
        regex_pattern = re.sub(r"\{(\w+)\}", lambda m: self._param_replacer(m, param_names), pattern)
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
        self.routes: List[KnowledgeRoute] = []

    def register_route(self, pattern: str, getter: Callable, explainer: Optional[Callable] = None,
                       tags: Optional[List[str]] = None,
                       related: Optional[List[Tuple[str, Relationship]]] = None):
        route = KnowledgeRoute(pattern, getter, explainer, tags, related)
        self.routes.append(route)

    def _find_route(self, key: str) -> Tuple[KnowledgeRoute, Dict[str, str]]:
        for route in self.routes:
            params = route.match(key)
            if params:
                return route, params
        raise KeyError(f"No route found for key: {key}")

    def get_value(self, key: str):
        route, params = self._find_route(key)
        return route.getter(params)

    def explain_value(self, key: str):
        route, params = self._find_route(key)
        value = route.getter(params)
        if route.explainer:
            return route.explainer(value, params)
        return f"No explanation available for value: {value}"

    def get_related_knowledge(self, key: str):
        route, _ = self._find_route(key)
        return route.related

    def get_routes_by_tag(self, tag: str) -> List[str]:
        return [r.pattern for r in self.routes if tag in r.tags]