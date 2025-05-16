from typing import Callable, Dict

getter_registry: Dict[str, Callable] = {}


def knowledge_getter(
    key: str,
) -> Callable[[Callable], Callable]:
    def decorator(func: Callable) -> Callable:
        getter_registry[key] = func
        return func

    return decorator