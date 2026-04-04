import logging
import os
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver

from .state import AgentState
from .nodes import planner, retriever, compressor, tool_runner, responder
from .checkpointer import PostgresCheckpointSaver
from storage.postgres import db

logger = logging.getLogger(__name__)
_SHARED_MEMORY_CHECKPOINTER = MemorySaver()


def _supports_postgres_checkpointer() -> bool:
    required_methods = ("get_tuple", "put", "list", "put_writes")
    return all(
        getattr(PostgresCheckpointSaver, method_name)
        is not getattr(BaseCheckpointSaver, method_name)
        for method_name in required_methods
    )


def _create_checkpointer():
    backend = os.getenv("GRAPH_CHECKPOINT_BACKEND", "memory").strip().lower() or "memory"
    if backend != "postgres":
        if backend != "memory":
            logger.warning(
                "Unknown GRAPH_CHECKPOINT_BACKEND=%s; using in-memory graph checkpoints",
                backend,
            )
        return _SHARED_MEMORY_CHECKPOINTER

    if not _supports_postgres_checkpointer():
        logger.warning(
            "GRAPH_CHECKPOINT_BACKEND=postgres requested, but PostgresCheckpointSaver "
            "does not implement the current LangGraph checkpoint API; using in-memory "
            "graph checkpoints"
        )
        return _SHARED_MEMORY_CHECKPOINTER

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.info(
            "GRAPH_CHECKPOINT_BACKEND=postgres requested, but DATABASE_URL is not set; "
            "using in-memory graph checkpoints"
        )
        return _SHARED_MEMORY_CHECKPOINTER

    try:
        db.connect()
    except Exception as exc:
        logger.warning(
            "Postgres checkpoints unavailable; using in-memory graph checkpoints: %s",
            exc,
        )
        return _SHARED_MEMORY_CHECKPOINTER

    return PostgresCheckpointSaver()

def create_graph():
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("planner", planner)
    graph.add_node("retriever", retriever)
    graph.add_node("compressor", compressor)
    graph.add_node("tool_runner", tool_runner)
    graph.add_node("responder", responder)

    # Set entry point
    graph.set_entry_point("planner")

    # Add normal edges
    graph.add_edge("planner", "retriever")
    graph.add_edge("retriever", "compressor")

    # Add conditional edges
    def route_after_compressor(state: AgentState):
        return "tool_runner" if state.get("tool_calls") else "responder"

    graph.add_conditional_edges("compressor", route_after_compressor)
    graph.add_edge("tool_runner", "responder")
    graph.add_edge("responder", END)

    # Add checkpointer for persistence
    checkpointer = _create_checkpointer()
    app = graph.compile(checkpointer=checkpointer)

    return app
