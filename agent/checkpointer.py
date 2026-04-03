import json
import hashlib
from typing import Iterator, Optional, Any, Dict
from langgraph.checkpoint.base import BaseCheckpointSaver
from storage.postgres import db

class PostgresCheckpointSaver(BaseCheckpointSaver):
    def __init__(self):
        super().__init__()

    def save_checkpoint(self, config: Dict[str, Any], checkpoint: Dict[str, Any], metadata: Dict[str, Any]) -> None:
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            raise ValueError("thread_id must be provided in config['configurable']")

        step_name = metadata.get("step", "unknown")
        state_json = json.dumps(checkpoint)

        # Get next version
        result = db.execute(
            "SELECT COALESCE(MAX(version), 0) + 1 as next_version FROM checkpoints WHERE thread_id = %s AND step_name = %s",
            (thread_id, step_name)
        )
        version = result[0]["next_version"]

        # Calculate checksum
        checksum = hashlib.md5(state_json.encode()).hexdigest()

        # Insert checkpoint
        db.execute(
            "INSERT INTO checkpoints (thread_id, step_name, state_json, version, checksum) VALUES (%s, %s, %s, %s, %s)",
            (thread_id, step_name, state_json, version, checksum)
        )

    def load_checkpoint(self, config: Dict[str, Any], before: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            raise ValueError("thread_id must be provided in config['configurable']")

        step_name = before.get("step") if before else None

        query = "SELECT state_json, version, checksum FROM checkpoints WHERE thread_id = %s"
        params = [thread_id]

        if step_name:
            query += " AND step_name = %s"
            params.append(step_name)

        query += " ORDER BY created_at DESC LIMIT 1"

        result = db.execute(query, params)
        if result:
            row = result[0]
            state_json = row["state_json"]
            stored_checksum = row["checksum"]
            calculated_checksum = hashlib.md5(state_json.encode()).hexdigest()
            if stored_checksum != calculated_checksum:
                raise ValueError("Checkpoint integrity check failed")
            return json.loads(state_json)
        return None

    def list_checkpoints(self, config: Dict[str, Any], filter: Optional[Dict[str, Any]] = None) -> Iterator[Dict[str, Any]]:
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            raise ValueError("thread_id must be provided in config['configurable']")

        query = "SELECT id, step_name, created_at, version FROM checkpoints WHERE thread_id = %s"
        params = [thread_id]

        if filter:
            if "step" in filter:
                query += " AND step_name = %s"
                params.append(filter["step"])

        query += " ORDER BY created_at DESC"

        results = db.execute(query, params)
        for row in results:
            yield {
                "id": str(row["id"]),
                "thread_id": thread_id,
                "step": row["step_name"],
                "created_at": row["created_at"].isoformat(),
                "version": row["version"]
            }