import json
import os

try:
    import psycopg2
    from psycopg2.extras import Json, RealDictCursor
except ImportError:
    psycopg2 = None
    Json = None
    RealDictCursor = None

class PostgresConnection:
    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/ai_agent_db")

    def connect(self):
        if psycopg2 is None:
            raise RuntimeError("psycopg2 is not installed")
        return psycopg2.connect(self.connection_string)

    def close(self):
        return None

    def _prepare_params(self, params):
        if params is None:
            return None

        prepared = []
        for value in params:
            if Json is not None and isinstance(value, (dict, list)):
                prepared.append(Json(value, dumps=json.dumps))
            else:
                prepared.append(value)
        return tuple(prepared)

    def execute(self, query, params=None):
        conn = self.connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, self._prepare_params(params))
                has_rows = cursor.description is not None
                rows = cursor.fetchall() if has_rows else cursor.rowcount
            conn.commit()
            return rows
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

# Global instance
db = PostgresConnection()
