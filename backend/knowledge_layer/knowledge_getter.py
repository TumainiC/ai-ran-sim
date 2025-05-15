_getter_registry = {}


def knowledge_getter(
    key: str,
):
    def decorator(func):
        _getter_registry[key] = func
        return func

    return decorator
