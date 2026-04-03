from typing import List, Optional, Dict, Any
from uuid import UUID
from memory.schemas import CorrectionMemory
from memory.long_term import LongTermMemoryManager
from memory.scoring import MemoryScorer


class CorrectionMemoryHandler:
    """Handles correction memories with priority for recurring errors."""

    def __init__(self, memory_manager: LongTermMemoryManager):
        self.memory_manager = memory_manager
        self.scorer = MemoryScorer()

    def add_correction(
        self,
        user_id: UUID,
        error_description: str,
        correction: str,
        context: str,
        thread_id: Optional[UUID] = None
    ) -> UUID:
        """
        Add a new correction memory.

        Args:
            user_id: User ID
            error_description: Description of the error/mistake
            correction: The correction or fix
            context: Context where the error occurred
            thread_id: Optional thread ID

        Returns:
            ID of the created correction memory
        """
        key = f"correction_{hash(error_description + correction) % 10000}"

        # Check if similar correction already exists
        existing = self.memory_manager.retrieve_memories(
            user_id=user_id,
            memory_type="correction",
            key_pattern=key
        )

        if existing:
            # Update existing correction with reinforcement
            existing_memory = existing[0]
            value_json = existing_memory.value_json
            value_json["reinforcement_count"] = value_json.get("reinforcement_count", 0) + 1
            value_json["last_context"] = context

            confidence = self.scorer.calculate_confidence(
                existing_memory,
                evidence_count=value_json.get("evidence_count", 1),
                reinforcement=value_json["reinforcement_count"]
            )

            self.memory_manager.update_memory(
                existing_memory.id,
                {"value_json": value_json, "confidence": confidence}
            )
            return existing_memory.id

        # Create new correction memory
        value_json = {
            "error_description": error_description,
            "correction": correction,
            "context": context,
            "reinforcement_count": 1,
            "evidence_count": 1
        }

        correction_memory = CorrectionMemory(
            user_id=user_id,
            thread_id=thread_id,
            key=key,
            value_json=value_json,
            confidence=self.scorer.calculate_confidence(
                CorrectionMemory(memory_type="correction", key=key, value_json=value_json, user_id=user_id),
                evidence_count=1,
                reinforcement=1
            ),
            source_type="conversation",
            status="active"
        )

        return self.memory_manager.store_memory(correction_memory)

    def get_relevant_corrections(
        self,
        user_id: UUID,
        context_keywords: List[str],
        limit: int = 10
    ) -> List[CorrectionMemory]:
        """
        Get correction memories relevant to the current context.

        Args:
            user_id: User ID
            context_keywords: Keywords from current context
            limit: Maximum corrections to return

        Returns:
            List of relevant correction memories
        """
        all_corrections = self.memory_manager.retrieve_memories(
            user_id=user_id,
            memory_type="correction",
            limit=limit * 2  # Get more to filter
        )

        # Filter and score by relevance to context
        relevant_corrections = []
        for correction in all_corrections:
            relevance_score = self._calculate_context_relevance(
                correction.value_json.get("context", ""),
                context_keywords
            )
            if relevance_score > 0.3:  # Threshold for relevance
                relevant_corrections.append((correction, relevance_score))

        # Sort by relevance and confidence, take top limit
        relevant_corrections.sort(
            key=lambda x: (x[1], x[0].confidence or 0),
            reverse=True
        )

        return [corr for corr, _ in relevant_corrections[:limit]]

    def decay_old_corrections(self, user_id: UUID):
        """
        Apply time decay to old corrections that haven't been reinforced.

        Args:
            user_id: User ID
        """
        # Placeholder - implement time-based decay logic
        # Reduce confidence of corrections older than X days with low reinforcement
        pass

    def _calculate_context_relevance(self, correction_context: str, keywords: List[str]) -> float:
        """
        Calculate how relevant a correction is to the given keywords.

        Args:
            correction_context: The context string from the correction
            keywords: List of keywords from current context

        Returns:
            Relevance score between 0.0 and 1.0
        """
        if not correction_context or not keywords:
            return 0.0

        correction_lower = correction_context.lower()
        matches = sum(1 for keyword in keywords if keyword.lower() in correction_lower)
        return matches / len(keywords) if keywords else 0.0