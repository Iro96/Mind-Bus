from .state import AgentState

__all__ = ["create_graph", "AgentState"]


def __getattr__(name):
    if name == "create_graph":
        from .graph import create_graph
        return create_graph
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
