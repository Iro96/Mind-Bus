from ..state import AgentState
from compression import ACC, CompressionInput

def compressor(state: AgentState) -> AgentState:
    # Use ACC for compression
    acc = ACC()
    # Assume state has the necessary fields; if not, provide defaults
    user_message = state.get('current_user_message', '')
    retrieved_passages = state.get('retrieved_passages', [])
    memories = state.get('memories', [])
    tool_outputs = state.get('tool_results', [])
    policy_rules = state.get('policy_rules', {})

    input_data = CompressionInput(
        user_message=user_message,
        session_state=state,
        retrieved_passages=retrieved_passages,
        memories=memories,
        tool_outputs=tool_outputs,
        policy_rules=policy_rules
    )

    output = acc.compress(input_data)

    # Update state with compressed context
    state['compact_context'] = output.compact_active_context
    state['retained_citations'] = output.retained_citations
    state['discarded_references'] = output.discarded_references
    state['summary_deltas'] = output.summary_deltas

    return state