import logging
from typing import Any, Dict, List

from observability.tracing import trace_span

from ..state import AgentState

logger = logging.getLogger(__name__)

MAX_TOOL_RETRIES = 1
RETRYABLE_ERROR_MARKERS = (
    "timeout",
    "tempor",
    "network",
    "connection",
    "rate limit",
    "429",
    "503",
    "unavailable",
)
NON_RETRYABLE_ERROR_MARKERS = (
    "disabled",
    "not found",
    "no expression provided",
    "no query provided",
    "no code provided",
    "invalid syntax",
)


def _truncate(value: Any, limit: int = 180) -> str:
    text = "" if value is None else str(value).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _is_tool_failure(result: Dict[str, Any]) -> bool:
    return bool(result.get("error")) or result.get("available") is False


def _is_retryable_failure(result: Dict[str, Any]) -> bool:
    if not _is_tool_failure(result):
        return False
    if result.get("available") is False:
        return False

    error_text = str(result.get("error", "")).lower()
    if any(marker in error_text for marker in NON_RETRYABLE_ERROR_MARKERS):
        return False
    return any(marker in error_text for marker in RETRYABLE_ERROR_MARKERS)


def _summarize_file_system_result(result: Dict[str, Any]) -> str:
    action = result.get("action", "file_system")
    path = result.get("path") or "unknown path"
    status = "ok" if result.get("success") is not False else "failed"
    error = result.get("error")

    if action == "read_text":
        details = f"chars={result.get('chars', 0)}"
        if result.get("truncated"):
            details = f"{details}, truncated=true"
        summary = f"file_system {action} {path} status={status} {details}"
    elif action in {"list_dir", "tree"}:
        summary = f"file_system {action} {path} status={status} entries={result.get('count', 0)}"
        if result.get("truncated"):
            summary = f"{summary}, truncated=true"
    elif action == "replace_text":
        summary = f"file_system {action} {path} status={status} replacements={result.get('replacements', 0)}"
    elif action in {"write_text", "append_text"}:
        summary = f"file_system {action} {path} status={status} chars={result.get('chars', 0)}"
    elif action == "move_path":
        summary = f"file_system {action} {path} -> {result.get('destination', '')} status={status}"
    elif action == "delete_path":
        summary = f"file_system {action} {path} status={status}"
    else:
        summary = f"file_system {action} {path} status={status}"

    if error:
        summary = f"{summary}; error={_truncate(error)}"
    return summary


def _summarize_tool_result(result: Dict[str, Any]) -> str:
    tool_name = result.get("tool", "tool")
    if tool_name == "file_system":
        return _summarize_file_system_result(result)
    if _is_tool_failure(result):
        return f"{tool_name} failed: {_truncate(result.get('error', 'unknown error'))}"
    if "result" in result:
        return f"{tool_name} result: {_truncate(result['result'])}"
    if "stdout" in result and result.get("stdout"):
        return f"{tool_name} output: {_truncate(result['stdout'])}"
    if "results" in result:
        return f"{tool_name} returned {len(result.get('results', []))} results."
    return f"{tool_name} output: {_truncate(result)}"


def _summarize_passage(passage: Dict[str, Any]) -> str:
    return _truncate(passage.get("text") or passage.get("content") or "")


def _build_response_context(state: AgentState, notes: List[str]) -> str:
    sections: List[str] = []
    user_message = state.get("current_user_message") or ""
    if user_message:
        sections.append("User request:\n" + user_message)

    compact_context = state.get("compact_context")
    if compact_context:
        sections.append("Compressed context:\n" + compact_context)

    tool_results = state.get("tool_results", [])
    if tool_results:
        tool_lines = "\n".join(f"- {_summarize_tool_result(result)}" for result in tool_results)
        sections.append("Tool observations:\n" + tool_lines)

    retrieved_passages = state.get("retrieved_passages", [])
    if retrieved_passages:
        passage_lines = "\n".join(
            f"- {_summarize_passage(passage)}"
            for passage in retrieved_passages[:3]
            if passage.get("text") or passage.get("content")
        )
        if passage_lines:
            sections.append("Retrieved evidence:\n" + passage_lines)

    if notes:
        sections.append("Reflection notes:\n" + "\n".join(f"- {note}" for note in notes))

    return "\n\n".join(section for section in sections if section).strip()


def reflector(state: AgentState) -> AgentState:
    with trace_span("reflector"):
        tool_results = state.get("tool_results", [])
        last_tool_calls = state.get("last_tool_calls", [])
        retry_count = int(state.get("retry_count", 0) or 0)

        notes: List[str] = []
        tool_failures: List[Dict[str, Any]] = []
        retry_calls: List[dict] = []

        if tool_results:
            for index, result in enumerate(tool_results):
                if _is_tool_failure(result):
                    tool_name = result.get("tool") or (
                        last_tool_calls[index]["name"] if index < len(last_tool_calls) else "tool"
                    )
                    error_text = _truncate(result.get("error", "unknown error"))
                    retryable = index < len(last_tool_calls) and _is_retryable_failure(result)
                    tool_failures.append(
                        {
                            "tool": tool_name,
                            "error": error_text,
                            "retryable": retryable,
                        }
                    )
                    notes.append(f"{tool_name} failed with: {error_text}")
                    if retryable:
                        retry_calls.append(dict(last_tool_calls[index]))
                else:
                    notes.append(_summarize_tool_result(result))
        else:
            retrieved_count = len(state.get("retrieved_passages", []))
            if retrieved_count:
                notes.append(f"Retrieved {retrieved_count} supporting passages for the response.")
            else:
                notes.append("No tool output or retrieved evidence is available; respond from the conversation only.")

        retry_planned = bool(retry_calls) and retry_count < MAX_TOOL_RETRIES
        if retry_planned:
            state["tool_calls"] = retry_calls
            state["retry_count"] = retry_count + 1
            state["current_task"] = "call_tool"
            notes.append("Retrying retryable tool failures before generating the final answer.")
            status = "retrying_tools"
        elif tool_failures:
            state["tool_calls"] = []
            state["current_task"] = "respond"
            notes.append("Proceeding with a best-effort response and explicitly acknowledging tool limitations.")
            status = "tool_failures"
        else:
            state["tool_calls"] = []
            state["current_task"] = "respond"
            if tool_results:
                notes.append("Tool outputs look usable for the final response.")
            status = "ready"

        state["reflection"] = {
            "status": status,
            "notes": notes,
            "tool_failures": tool_failures,
            "retry_planned": retry_planned,
            "retry_count": state.get("retry_count", retry_count),
        }
        state["response_context"] = _build_response_context(state, notes)

        logger.debug(
            "reflector status=%s retry_planned=%s retry_count=%s failures=%s",
            status,
            retry_planned,
            state.get("retry_count", retry_count),
            len(tool_failures),
        )
        return state
