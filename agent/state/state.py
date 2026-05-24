from typing import Any, Dict, List, Optional
from typing_extensions import NotRequired, TypedDict


class ReflectionState(TypedDict, total=False):
    status: str
    notes: List[str]
    tool_failures: List[Dict[str, Any]]
    retry_planned: bool
    retry_count: int


class AgentState(TypedDict):
    messages: List[dict]  # Conversation history
    current_task: Optional[str]  # Current task or plan
    tool_calls: List[dict]  # Pending tool calls
    tool_results: List[dict]  # Results from tool executions
    retry_count: int  # For handling retries
    final_response: Optional[str]  # Final response to user
    current_user_message: NotRequired[str]
    retrieved_passages: NotRequired[List[dict]]
    memories: NotRequired[List[Any]]
    policy_rules: NotRequired[Dict[str, Any]]
    compact_context: NotRequired[str]
    retained_citations: NotRequired[List[dict]]
    discarded_references: NotRequired[List[dict]]
    summary_deltas: NotRequired[List[dict]]
    last_tool_calls: NotRequired[List[dict]]
    tool_result_history: NotRequired[List[dict]]
    reflection: NotRequired[ReflectionState]
    response_context: NotRequired[str]
