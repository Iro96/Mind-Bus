from typing import List, Optional, Dict, Any
from uuid import UUID
from memory.schemas import BaseMemory
from memory.long_term import LongTermMemoryManager


class ShortTermMemory:
    """Manages short-term memory for current session/context."""

    def __init__(self, long_term_manager: LongTermMemoryManager):
        self.long_term_manager = long_term_manager
        self.session_memories: List[BaseMemory] = []
        self.context_window_size = 50  # Maximum memories to keep in short-term

    def add_memory(self, memory: BaseMemory):
        """
        Add a memory to short-term storage.

        Args:
            memory: The memory to add
        """
        self.session_memories.append(memory)

        # Maintain context window size
        if len(self.session_memories) > self.context_window_size:
            # Move oldest to long-term if not already there
            oldest = self.session_memories.pop(0)
            if not oldest.id:  # If not persisted yet
                # Persist to long-term asynchronously
                pass  # TODO: Implement async persistence

    def get_recent_memories(self, limit: int = 20) -> List[BaseMemory]:
        """
        Get recent memories from short-term storage.

        Args:
            limit: Maximum number of memories to return

        Returns:
            List of recent memories
        """
        return self.session_memories[-limit:] if self.session_memories else []

    def search_memories(self, query: str) -> List[BaseMemory]:
        """
        Search short-term memories for relevant content.

        Args:
            query: Search query

        Returns:
            List of matching memories
        """
        # Simple keyword search - in practice, use semantic search
        query_lower = query.lower()
        matches = []
        for memory in self.session_memories:
            if query_lower in str(memory.value_json).lower():
                matches.append(memory)
        return matches

    def flush_to_long_term(self, user_id: UUID):
        """
        Flush short-term memories to long-term storage.

        Args:
            user_id: User ID
        """
        for memory in self.session_memories:
            if not memory.id:  # Only persist if not already persisted
                memory.user_id = user_id
                self.long_term_manager.store_memory(memory)

        # Clear short-term after flushing
        self.session_memories.clear()

    def clear_session(self):
        """Clear all short-term memories for the current session."""
        self.session_memories.clear()