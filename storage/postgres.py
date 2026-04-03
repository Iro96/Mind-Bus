import os
import psycopg2
from psycopg2.extras import RealDictCursor

class PostgresConnection:
    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/ai_agent_db")
        self.conn = None

    def connect(self):
        if self.conn is None:
            self.conn = psycopg2.connect(self.connection_string)
        return self.conn

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute(self, query, params=None):
        conn = self.connect()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            # Support SELECT and RETURNING clauses that return rows
            if query.strip().upper().startswith("SELECT") or cursor.description is not None:
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.rowcount

# Global instance
db = PostgresConnection()