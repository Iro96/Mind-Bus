import json
from typing import Dict, List, Optional
from uuid import UUID

from llm.client import LLMClient
from llm.prompts import build_memory_extraction_prompt
from memory.schemas import (
    BaseMemory,
    CorrectionMemory,
    EpisodicMemory,
    MemoryExtractionRequest,
    MemoryExtractionResponse,
    SemanticMemory,
)
from memory.scoring import MemoryScorer


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

        new_memories: List[BaseMemory] = []
        updated_memories: List[BaseMemory] = []
        existing_memories = request.current_memories or []
        existing_lookup = {
            (memory.memory_type, memory.key): memory
            for memory in existing_memories
        }
        pending_new_lookup: Dict[tuple[str, str], BaseMemory] = {}

        for memory_data in extracted_data:
            memory = self._create_memory_from_data(memory_data, request.user_id, request.thread_id)
            if not memory:
                continue

            identity = (memory.memory_type, memory.key)
            existing_memory = existing_lookup.get(identity)
            if existing_memory:
                merged_memory = self._merge_with_existing(existing_memory, memory)
                existing_lookup[identity] = merged_memory
                self._upsert_memory_list(updated_memories, merged_memory)
                continue

            pending_new = pending_new_lookup.get(identity)
            if pending_new:
                merged_new = self._merge_with_existing(pending_new, memory, preserve_identity=False)
                pending_new_lookup[identity] = merged_new
                self._replace_memory_list_entry(new_memories, merged_new)
                continue

            new_memories.append(memory)
            pending_new_lookup[identity] = memory

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
        normalized = " ".join(conversation.split()) or "Conversation summary unavailable."
        snippet = normalized[:120]
        key_seed = "".join(ch.lower() if ch.isalnum() else "_" for ch in snippet).strip("_")
        key_seed = key_seed[:40] or "conversation"

        extracted: List[Dict] = [
            {
                "type": "episodic",
                "key": f"thread_summary_{key_seed}",
                "value": {
                    "summary": snippet,
                    "source_excerpt": snippet,
                    "evidence_count": 1,
                },
            }
        ]

        if "python" in normalized.lower():
            extracted.append(
                {
                    "type": "semantic",
                    "key": "user_preference_python",
                    "value": {
                        "fact": "User prefers Python for scripting tasks",
                        "provenance": "Observed in the conversation",
                        "evidence_count": 1,
                    },
                }
            )

        if any(keyword in normalized.lower() for keyword in ("wrong", "incorrect", "correction", "fix")):
            extracted.append(
                {
                    "type": "correction",
                    "key": "conversation_correction_pattern",
                    "value": {
                        "error_description": "The conversation references an incorrect or corrected result.",
                        "correction": "Review the conversation for the corrected version before repeating the same claim.",
                        "context": snippet,
                        "reinforcement_count": 1,
                        "evidence_count": 1,
                    },
                }
            )

        return extracted

    def _create_memory_from_data(self, data: Dict, user_id: UUID, thread_id: Optional[UUID]) -> Optional[BaseMemory]:
        """Create a memory object from extracted data."""
        memory_type = data.get("type")
        key = data.get("key")
        value = data.get("value")

        if memory_type not in {"episodic", "semantic", "correction"} or not key or not isinstance(value, dict):
            return None

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

    def _merge_with_existing(
        self,
        existing_memory: BaseMemory,
        incoming_memory: BaseMemory,
        preserve_identity: bool = True,
    ) -> BaseMemory:
        merged_value = dict(existing_memory.value_json)
        for key, value in incoming_memory.value_json.items():
            if key in {"evidence_count", "reinforcement_count"}:
                merged_value[key] = int(merged_value.get(key, 0) or 0) + int(value or 0)
            else:
                merged_value[key] = value

        confidence = MemoryScorer.calculate_confidence(
            BaseMemory(
                memory_type=existing_memory.memory_type,
                key=existing_memory.key,
                value_json=merged_value,
                user_id=existing_memory.user_id,
                thread_id=existing_memory.thread_id,
            ),
            evidence_count=int(merged_value.get("evidence_count", 1) or 1),
            reinforcement=int(merged_value.get("reinforcement_count", 0) or 0),
        )

        base_payload = incoming_memory.model_dump()
        if preserve_identity:
            base_payload.update(
                {
                    "id": existing_memory.id,
                    "user_id": existing_memory.user_id,
                    "thread_id": existing_memory.thread_id,
                    "created_at": existing_memory.created_at,
                    "updated_at": existing_memory.updated_at,
                    "expires_at": existing_memory.expires_at,
                    "source_id": existing_memory.source_id or incoming_memory.source_id,
                    "source_type": existing_memory.source_type or incoming_memory.source_type,
                }
            )
        base_payload["value_json"] = merged_value
        base_payload["confidence"] = confidence

        return self._create_memory_model(existing_memory.memory_type, base_payload)

    def _create_memory_model(self, memory_type: str, payload: Dict) -> BaseMemory:
        if memory_type == "episodic":
            return EpisodicMemory(**payload)
        if memory_type == "semantic":
            return SemanticMemory(**payload)
        return CorrectionMemory(**payload)

    @staticmethod
    def _upsert_memory_list(memories: List[BaseMemory], memory: BaseMemory) -> None:
        for index, existing in enumerate(memories):
            if existing.id == memory.id:
                memories[index] = memory
                return
        memories.append(memory)

    @staticmethod
    def _replace_memory_list_entry(memories: List[BaseMemory], memory: BaseMemory) -> None:
        for index, existing in enumerate(memories):
            if existing.memory_type == memory.memory_type and existing.key == memory.key:
                memories[index] = memory
                return
        memories.append(memory)
