import time
import logging
from ..state import AgentState
from observability.metrics import record_tool_call_latency
from observability.tracing import trace_span
from tools import run_tool

logger = logging.getLogger(__name__)

def tool_runner(state: AgentState) -> AgentState:
    # Execute pending tool calls
    with trace_span("tool_runner"):
        for call in state["tool_calls"]:
            start = time.perf_counter()
            try:
                # Delegated tool execution
                result = run_tool(call["name"], call.get("args", {}))
                state["tool_results"].append(result)
            except Exception as e:
                logger.exception("Tool execution failed: %s", e)
                state["tool_results"].append({"tool": call.get("name"), "error": str(e)})
            finally:
                duration_ms = (time.perf_counter() - start) * 1000.0
                record_tool_call_latency(duration_ms)
                logger.debug(
                    "tool_runner tool=%s latency_ms=%.2f", call["name"], duration_ms
                )

        state["tool_calls"] = []  # Clear after execution
        state["current_task"] = "respond"  # Next step
        return state