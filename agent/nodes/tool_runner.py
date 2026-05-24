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
        pending_calls = [dict(call) for call in state.get("tool_calls", [])]
        current_results = []
        history = list(state.get("tool_result_history", []))

        for call in pending_calls:
            start = time.perf_counter()
            try:
                # Delegated tool execution
                result = run_tool(call["name"], call.get("args", {}))
                current_results.append(result)
            except Exception as e:
                logger.exception("Tool execution failed: %s", e)
                current_results.append({"tool": call.get("name"), "error": str(e)})
            finally:
                duration_ms = (time.perf_counter() - start) * 1000.0
                record_tool_call_latency(duration_ms)
                logger.debug(
                    "tool_runner tool=%s latency_ms=%.2f", call["name"], duration_ms
                )
                history.append(
                    {
                        "call": call,
                        "result": current_results[-1] if current_results else None,
                    }
                )

        state["last_tool_calls"] = pending_calls
        state["tool_results"] = current_results
        state["tool_result_history"] = history
        state["tool_calls"] = []  # Clear after execution
        state["current_task"] = "reflect"  # Next step
        return state
