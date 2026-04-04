from typing import List, Optional, Any
from typing_extensions import TypedDict

class AgentState(TypedDict):
    messages: List[dict]  # Conversation history
    current_task: Optional[str]  # Current task or plan
    tool_calls: List[dict]  # Pending tool calls
    tool_results: List[dict]  # Results from tool executions
    retry_count: int  # For handling retries
    final_response: Optional[str]  # Final response to user
