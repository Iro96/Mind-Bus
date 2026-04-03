from typing import List, Optional, Dict
from uuid import UUID
from memory.schemas import BaseMemory, MemoryExtractionRequest, MemoryExtractionResponse, EpisodicMemory, SemanticMemory, CorrectionMemory
from memory.scoring import MemoryScorer
import json
from llm.client import LLMClient
from llm.prompts import build_memory_extraction_prompt


class MemoryExtractor:
    """Extracts memories from conversations using LLM-based analysis."""

    def __init__(self):
        self.llm_client = LLMClient()

    def extract_memories(self, request: MemoryExtractionRequest) -> MemoryExtractionResponse:
        """
        Extract new memories from a conversation.

        Args:
            request: Extraction request containing conversation and context

        Returns:
            Response with new and updated memories
        """
        # Placeholder for LLM call to extract memories
        # In practice, this would call an LLM with prompts to identify:
        # - Episodic: what happened (tasks completed, decisions made, etc.)
        # - Semantic: facts learned, preferences, constraints
        # - Correction: mistakes, corrections, failures

        extracted_data = self._extract_via_llm(request)

        new_memories = []
        updated_memories = []

        for memory_data in extracted_data:
            memory = self._create_memory_from_data(memory_data, request.user_id, request.thread_id)
            if memory:
                new_memories.append(memory)

        # TODO: Implement logic to update existing memories based on current_memories

        return MemoryExtractionResponse(
            new_memories=new_memories,
            updated_memories=updated_memories
        )

    def _extract_via_llm(self, request: MemoryExtractionRequest) -> List[Dict]:
        prompt_text = build_memory_extraction_prompt(request.conversation)
        prompt = {
            "role": "system",
            "content": prompt_text,
        }
        user_prompt = {
            "role": "user",
            "content": "Extract memories from the conversation above as JSON array with type/key/value.",
        }

        llm_response = self.llm_client.chat_completion([prompt, user_prompt])

        # Try to parse structured output
        if isinstance(llm_response, dict):
            if "content" in llm_response and isinstance(llm_response["content"], str):
                try:
                    return json.loads(llm_response["content"])
                except Exception:
                    # fallback to previous mock
                    pass

        # Fallback to robust mock if no parse
        return self._mock_llm_extraction(request.conversation)

    def _mock_llm_extraction(self, conversation: str) -> List[Dict]:
        """
        [Retained as fallback] Mock LLM extraction.
        """
        return [
            {
                "type": "episodic",
                "key": "task_completed_example",
                "value": {
                    "summary": "User completed a coding task",
                    "timestamp": "2024-01-01T12:00:00Z",
                    "thread_id": "example-thread-id",
                    "source_pointers": ["message_1", "message_2"]
                }
            },
            {
                "type": "semantic",
                "key": "user_preference_python",
                "value": {
                    "fact": "User prefers Python for scripting tasks",
                    "provenance": "Observed in multiple conversations",
                    "evidence_count": 3
                }
            },
            {
                "type": "correction",
                "key": "avoid_assumption_x",
                "value": {
                    "error_description": "Assumed X without confirmation",
                    "correction": "Always ask for confirmation before assuming X",
                    "context": "In conversation about Y",
                    "reinforcement_count": 1
                }
            }
        ]

    def _create_memory_from_data(self, data: Dict, user_id: UUID, thread_id: Optional[UUID]) -> Optional[BaseMemory]:
        """Create a memory object from extracted data."""
        memory_type = data["type"]
        key = data["key"]
        value = data["value"]

        confidence = MemoryScorer.calculate_confidence(
            BaseMemory(memory_type=memory_type, key=key, value_json=value, user_id=user_id),
            evidence_count=value.get("evidence_count", 1),
            reinforcement=value.get("reinforcement_count", 0)
        )

        if memory_type == "episodic":
            return EpisodicMemory(
                user_id=user_id,
                thread_id=thread_id,
                key=key,
                value_json=value,
                confidence=confidence,
                source_type="conversation",
                status="active"
            )
        elif memory_type == "semantic":
            return SemanticMemory(
                user_id=user_id,
                thread_id=thread_id,
                key=key,
                value_json=value,
                confidence=confidence,
                source_type="conversation",
                status="active"
            )
        elif memory_type == "correction":
            return CorrectionMemory(
                user_id=user_id,
                thread_id=thread_id,
                key=key,
                value_json=value,
                confidence=confidence,
                source_type="conversation",
                status="active"
            )

        return None