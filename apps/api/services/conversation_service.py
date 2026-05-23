import logging
import threading
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from storage.postgres import db

logger = logging.getLogger(__name__)


class _InMemoryConversationStore:
    def __init__(self):
        self._lock = threading.Lock()
        self.users_by_username: Dict[str, Dict[str, Any]] = {}
        self.sessions_by_user: Dict[str, Dict[str, Any]] = {}
        self.threads: Dict[str, Dict[str, Any]] = {}
        self.messages_by_thread: Dict[str, List[Dict[str, Any]]] = {}

    def upsert_user(self, username: str, roles: List[str]) -> Dict[str, Any]:
        with self._lock:
            existing = self.users_by_username.get(username)
            if existing:
                existing["roles"] = roles
                existing["role"] = roles[0]
                return dict(existing)

            user_id = uuid.uuid5(uuid.NAMESPACE_URL, f"mind-bus-user:{username}")
            user = {
                "id": str(user_id),
                "email": f"{username}@demo.local",
                "role": roles[0],
                "roles": roles,
            }
            self.users_by_username[username] = user
            return dict(user)

    def get_or_create_session(self, user_id: str) -> Dict[str, Any]:
        with self._lock:
            session = self.sessions_by_user.get(user_id)
            if session:
                session["last_active_at"] = datetime.utcnow()
                return dict(session)

            session = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "status": "active",
                "created_at": datetime.utcnow(),
                "last_active_at": datetime.utcnow(),
            }
            self.sessions_by_user[user_id] = session
            return dict(session)

    def create_thread(self, user_id: str, session_id: str, title: str) -> Dict[str, Any]:
        with self._lock:
            thread = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "session_id": session_id,
                "title": title,
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            self.threads[thread["id"]] = thread
            self.messages_by_thread.setdefault(thread["id"], [])
            return dict(thread)

    def get_thread(self, user_id: str, thread_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            thread = self.threads.get(thread_id)
            if not thread or thread["user_id"] != user_id:
                return None
            return dict(thread)

    def add_message(self, thread_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        with self._lock:
            message = {
                "id": str(uuid.uuid4()),
                "thread_id": thread_id,
                "role": role,
                "content": content,
                "metadata": metadata or {},
                "created_at": datetime.utcnow(),
            }
            self.messages_by_thread.setdefault(thread_id, []).append(message)
            if thread_id in self.threads:
                self.threads[thread_id]["updated_at"] = datetime.utcnow()
            return dict(message)

    def list_messages(self, thread_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            return [dict(message) for message in self.messages_by_thread.get(thread_id, [])]


_fallback_store = _InMemoryConversationStore()


class ConversationService:
    def upsert_demo_user(self, username: str, roles: List[str]) -> Dict[str, Any]:
        email = f"{username}@demo.local"
        role = roles[0] if roles else "user"
        query = """
        INSERT INTO users (email, password_hash, auth_provider_id, role)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (email) DO UPDATE
        SET auth_provider_id = EXCLUDED.auth_provider_id,
            role = EXCLUDED.role,
            updated_at = NOW()
        RETURNING id, email, role
        """
        try:
            row = db.execute(query, (email, None, username, role))[0]
            return {
                "id": str(row["id"]),
                "email": row["email"],
                "role": row["role"],
                "roles": roles,
            }
        except Exception as exc:
            logger.warning("Falling back to in-memory user storage: %s", exc)
            return _fallback_store.upsert_user(username, roles)

    def get_or_create_thread(self, user_id: UUID, requested_thread_id: Optional[UUID], title_hint: str) -> Dict[str, Any]:
        if requested_thread_id:
            thread = self.get_thread_for_user(user_id, requested_thread_id)
            if thread is None:
                raise KeyError("thread_not_found")
            return thread

        session = self._get_or_create_active_session(user_id)
        title = (title_hint or "New thread").strip()[:120] or "New thread"
        query = """
        INSERT INTO threads (user_id, session_id, title, status)
        VALUES (%s, %s, %s, %s)
        RETURNING id, user_id, session_id, title, status, created_at, updated_at
        """
        try:
            row = db.execute(query, (str(user_id), session["id"], title, "active"))[0]
            return self._normalize_thread_row(row)
        except Exception as exc:
            logger.warning("Falling back to in-memory thread creation: %s", exc)
            return _fallback_store.create_thread(str(user_id), session["id"], title)

    def get_thread_for_user(self, user_id: UUID, thread_id: UUID) -> Optional[Dict[str, Any]]:
        query = """
        SELECT id, user_id, session_id, title, status, created_at, updated_at
        FROM threads
        WHERE id = %s AND user_id = %s
        LIMIT 1
        """
        try:
            rows = db.execute(query, (str(thread_id), str(user_id)))
            if not rows:
                return None
            return self._normalize_thread_row(rows[0])
        except Exception as exc:
            logger.warning("Falling back to in-memory thread lookup: %s", exc)
            return _fallback_store.get_thread(str(user_id), str(thread_id))

    def add_message(
        self,
        thread_id: UUID,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        query = """
        INSERT INTO messages (thread_id, role, content, metadata)
        VALUES (%s, %s, %s, %s)
        RETURNING id, thread_id, role, content, created_at, metadata
        """
        try:
            row = db.execute(query, (str(thread_id), role, content, metadata or {}))[0]
            db.execute(
                "UPDATE threads SET updated_at = NOW() WHERE id = %s",
                (str(thread_id),),
            )
            db.execute(
                """
                UPDATE sessions
                SET last_active_at = NOW(), updated_at = NOW()
                WHERE id = (
                    SELECT session_id FROM threads WHERE id = %s
                )
                """,
                (str(thread_id),),
            )
            return self._normalize_message_row(row)
        except Exception as exc:
            logger.warning("Falling back to in-memory message persistence: %s", exc)
            return _fallback_store.add_message(str(thread_id), role, content, metadata)

    def list_thread_messages(self, user_id: UUID, thread_id: UUID) -> List[Dict[str, Any]]:
        thread = self.get_thread_for_user(user_id, thread_id)
        if thread is None:
            raise KeyError("thread_not_found")

        query = """
        SELECT id, thread_id, role, content, created_at, metadata
        FROM messages
        WHERE thread_id = %s
        ORDER BY created_at ASC
        """
        try:
            rows = db.execute(query, (str(thread_id),))
            return [self._normalize_message_row(row) for row in rows]
        except Exception as exc:
            logger.warning("Falling back to in-memory thread messages: %s", exc)
            return _fallback_store.list_messages(str(thread_id))

    def build_state_messages(self, user_id: UUID, thread_id: UUID) -> List[Dict[str, str]]:
        messages = self.list_thread_messages(user_id, thread_id)
        return [
            {"role": message["role"], "content": message["content"] or ""}
            for message in messages
        ]

    def _get_or_create_active_session(self, user_id: UUID) -> Dict[str, Any]:
        select_query = """
        SELECT id, user_id, status, created_at, last_active_at
        FROM sessions
        WHERE user_id = %s AND status = 'active'
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 1
        """
        insert_query = """
        INSERT INTO sessions (user_id, status, last_active_at)
        VALUES (%s, %s, NOW())
        RETURNING id, user_id, status, created_at, last_active_at
        """
        try:
            rows = db.execute(select_query, (str(user_id),))
            if rows:
                row = rows[0]
                db.execute(
                    "UPDATE sessions SET last_active_at = NOW(), updated_at = NOW() WHERE id = %s",
                    (str(row["id"]),),
                )
                return {"id": str(row["id"]), "user_id": str(row["user_id"]), "status": row["status"]}

            row = db.execute(insert_query, (str(user_id), "active"))[0]
            return {"id": str(row["id"]), "user_id": str(row["user_id"]), "status": row["status"]}
        except Exception as exc:
            logger.warning("Falling back to in-memory session creation: %s", exc)
            return _fallback_store.get_or_create_session(str(user_id))

    @staticmethod
    def _normalize_thread_row(row: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": str(row["id"]),
            "user_id": str(row["user_id"]),
            "session_id": str(row["session_id"]),
            "title": row.get("title"),
            "status": row.get("status"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        }

    @staticmethod
    def _normalize_message_row(row: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": str(row["id"]),
            "thread_id": str(row["thread_id"]),
            "role": row["role"],
            "content": row["content"],
            "created_at": row["created_at"],
            "metadata": row.get("metadata") or {},
        }
