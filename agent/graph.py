import logging
import os
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import AgentState
from .nodes import planner, retriever, compressor, tool_runner, responder
from .checkpointer import PostgresCheckpointSaver
from storage.postgres import db

logger = logging.getLogger(__name__)


def _create_checkpointer():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.info("DATABASE_URL not set; using in-memory graph checkpoints")
        return MemorySaver()

    try:
        db.connect()
    except Exception as exc:
        logger.warning(
            "Postgres checkpoints unavailable; using in-memory graph checkpoints: %s",
            exc,
        )
        return MemorySaver()

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
