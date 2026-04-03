import logging
from ..state import AgentState
from observability.metrics import record_memory_write
from observability.tracing import trace_span
from llm.client import LLMClient

logger = logging.getLogger(__name__)

llm_client = LLMClient()

def responder(state: AgentState) -> AgentState:
    with trace_span("responder"):
        if state["tool_results"]:
            tool_summary = "\n".join([str(result) for result in state["tool_results"]])
            prompt = (
                "You are an AI assistant. You were given these tool results: \n" + tool_summary + "\n"
                "Respond concisely and continue the conversation."
            )
            response = llm_client.generate_text(prompt)
        else:
            conversation_text = "\n".join([f"{m['role']}: {m['content']}" for m in state["messages"]])
            prompt = (
                "You are an AI assistant. Continue the conversation with context:\n" + conversation_text
            )
            response = llm_client.generate_text(prompt)

        state["final_response"] = response
        # Add to messages
        state["messages"].append({"role": "assistant", "content": response})

        record_memory_write(overwrite=False)
        logger.debug("responder memory write recorded")

    return state