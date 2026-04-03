from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from memory.schemas import BaseMemory, EpisodicMemory, SemanticMemory, CorrectionMemory
from memory.scoring import MemoryScorer
from storage.postgres import db  # Use the global db instance
import json


class LongTermMemoryManager:
    """Manages long-term memory storage and retrieval."""

    def __init__(self):
        self.scorer = MemoryScorer()

    def store_memory(self, memory: BaseMemory) -> UUID:
        """
        Store a new memory in the database.

        Args:
            memory: The memory to store

        Returns:
            The ID of the stored memory
        """
        query = """
        INSERT INTO memories (
            user_id, thread_id, memory_type, key, value_json,
            confidence, source_type, source_id, expires_at, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        expires_at = self._calculate_expiry(memory)
        params = (
            str(memory.user_id), str(memory.thread_id) if memory.thread_id else None, memory.memory_type,
            memory.key, json.dumps(memory.value_json), memory.confidence,
            memory.source_type, str(memory.source_id) if memory.source_id else None, expires_at, memory.status
        )

        result = db.execute(query, params)
        if result:
            return UUID(result[0]['id'])
        return None

    def retrieve_memories(
        self,
        user_id: UUID,
        memory_type: Optional[str] = None,
        key_pattern: Optional[str] = None,
        limit: int = 100
    ) -> List[BaseMemory]:
        """
        Retrieve memories from the database.

        Args:
            user_id: User ID
            memory_type: Optional filter by memory type
            key_pattern: Optional pattern to match keys
            limit: Maximum number of memories to return

        Returns:
            List of memories
        """
        query = """
        SELECT * FROM memories
        WHERE user_id = %s AND status = 'active'
        """
        params = [str(user_id)]

        if memory_type:
            query += " AND memory_type = %s"
            params.append(memory_type)

        if key_pattern:
            query += " AND key LIKE %s"
            params.append(f"%{key_pattern}%")

        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)

        rows = db.execute(query, params)
        memories = []
        for row in rows:
            memory = self._row_to_memory(row)
            if memory:
                memories.append(memory)

        return memories

    def update_memory(self, memory_id: UUID, updates: Dict[str, Any]) -> bool:
        """
        Update an existing memory.

        Args:
            memory_id: ID of the memory to update
            updates: Fields to update

        Returns:
            True if update was successful
        """
        # Build dynamic update query
        set_parts = []
        params = []

        for key, value in updates.items():
            if key in ['value_json', 'confidence', 'status', 'expires_at']:
                set_parts.append(f"{key} = %s")
                if key == 'value_json':
                    params.append(json.dumps(value))
                else:
                    params.append(value)

        if not set_parts:
            return False

        query = f"""
        UPDATE memories
        SET {', '.join(set_parts)}, updated_at = NOW()
        WHERE id = %s
        """
        params.append(str(memory_id))

        result = db.execute(query, params)
        return result > 0

    def merge_duplicate_memories(self, user_id: UUID, memory_type: str):
        """
        Merge duplicate memories of the same type and key.

        Args:
            user_id: User ID
            memory_type: Type of memories to merge
        """
        # Placeholder - implement merging logic
        # Find memories with same key, merge value_json, update confidence, etc.
        pass

    def cleanup_expired_memories(self):
        """Remove or mark expired memories."""
        query = """
        UPDATE memories
        SET status = 'expired'
        WHERE expires_at IS NOT NULL AND expires_at < NOW() AND status = 'active'
        """
        db.execute(query)

    def _calculate_expiry(self, memory: BaseMemory) -> Optional[datetime]:
        """Calculate expiry date based on memory type."""
        now = datetime.utcnow()
        if memory.memory_type == "correction":
            # Expire correction memories after 30 days unless reinforced
            return now + timedelta(days=30)
        elif memory.memory_type == "episodic":
            # Keep episodic memories for 1 year
            return now + timedelta(days=365)
        # Semantic memories don't expire by default
        return None

    def _row_to_memory(self, row) -> Optional[BaseMemory]:
        """Convert database row to memory object."""
        memory_type = row['memory_type']
        base_data = {
            'id': UUID(row['id']),
            'user_id': UUID(row['user_id']),
            'thread_id': UUID(row['thread_id']) if row['thread_id'] else None,
            'memory_type': memory_type,
            'key': row['key'],
            'value_json': row['value_json'],
            'confidence': row['confidence'],
            'source_type': row['source_type'],
            'source_id': UUID(row['source_id']) if row['source_id'] else None,
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
            'expires_at': row['expires_at'],
            'status': row['status']
        }

        if memory_type == "episodic":
            return EpisodicMemory(**base_data)
        elif memory_type == "semantic":
            return SemanticMemory(**base_data)
        elif memory_type == "correction":
            return CorrectionMemory(**base_data)

        return None