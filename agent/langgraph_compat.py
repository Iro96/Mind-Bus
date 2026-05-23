try:
    from langgraph.graph import END, StateGraph
    from langgraph.checkpoint.base import BaseCheckpointSaver
    from langgraph.checkpoint.memory import MemorySaver
except ImportError:
    END = "__end__"

    class BaseCheckpointSaver:
        def get_tuple(self, *args, **kwargs):
            raise NotImplementedError

        def put(self, *args, **kwargs):
            raise NotImplementedError

        def list(self, *args, **kwargs):
            raise NotImplementedError

        def put_writes(self, *args, **kwargs):
            raise NotImplementedError

    class MemorySaver(BaseCheckpointSaver):
        pass

    class _CompiledGraph:
        def __init__(self, nodes, entry_point, edges, conditional_edges):
            self._nodes = nodes
            self._entry_point = entry_point
            self._edges = edges
            self._conditional_edges = conditional_edges

        def invoke(self, state, config=None):
            current = self._entry_point
            while current != END:
                state = self._nodes[current](state)
                if current in self._conditional_edges:
                    current = self._conditional_edges[current](state)
                else:
                    current = self._edges.get(current, END)
            return state

    class StateGraph:
        def __init__(self, _state_type=None):
            self._nodes = {}
            self._edges = {}
            self._conditional_edges = {}
            self._entry_point = None

        def add_node(self, name, func):
            self._nodes[name] = func

        def set_entry_point(self, name):
            self._entry_point = name

        def add_edge(self, source, target):
            self._edges[source] = target

        def add_conditional_edges(self, source, router):
            self._conditional_edges[source] = router

        def compile(self, checkpointer=None):
            return _CompiledGraph(
                self._nodes,
                self._entry_point,
                self._edges,
                self._conditional_edges,
            )
