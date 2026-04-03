from ..state import AgentState
from agent.retrieval.hybrid_search import searcher
from observability.tracing import trace_span
from observability.metrics import record_retrieval_hit, record_retrieval_failure


def retriever(state: AgentState) -> AgentState:
    # Retrieve external context from Qdrant if query present
    with trace_span("retriever"):
        user_message = state["messages"][-1]["content"] if state.get("messages") else ""
        if user_message:
            try:
                results = searcher.hybrid_search(user_message, limit=5)
                state["retrieved_passages"] = results
                record_retrieval_hit(bool(results))
            except Exception as e:
                record_retrieval_failure()
                state["retrieved_passages"] = []
        else:
            state["retrieved_passages"] = []
            record_retrieval_hit(False)
    return state