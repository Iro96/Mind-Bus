import logging
from ..state import AgentState
from observability.metrics import record_memory_write
from observability.tracing import trace_span
from llm.client import LLMClient

logger = logging.getLogger(__name__)

llm_client = LLMClient()

def responder(state: AgentState) -> AgentState:
    with trace_span("responder"):
        conversation_text = "\n".join(
            [f"{message['role']}: {message['content']}" for message in state.get("messages", [])]
        )
        reflection = state.get("reflection", {})
        reflection_notes = "\n".join(f"- {note}" for note in reflection.get("notes", []))

        prompt_sections = [
            "You are an AI assistant. Use the available evidence carefully, be concise, and do not invent facts.",
            "Conversation:\n" + conversation_text,
        ]

        if state.get("response_context"):
            prompt_sections.append("Agent context:\n" + state["response_context"])
        elif state.get("compact_context"):
            prompt_sections.append("Compressed context:\n" + state["compact_context"])

        if reflection_notes:
            prompt_sections.append("Reflection guidance:\n" + reflection_notes)

        if reflection.get("status") == "tool_failures":
            prompt_sections.append(
                "If a tool failed, answer with the best available information and clearly mention the limitation."
            )

        prompt_sections.append("Respond to the latest user message.")
        response = llm_client.generate_text("\n\n".join(prompt_sections))

        state["final_response"] = response
        # Add to messages
        state["messages"].append({"role": "assistant", "content": response})

        record_memory_write(overwrite=False)
        logger.debug("responder memory write recorded")

    return state
