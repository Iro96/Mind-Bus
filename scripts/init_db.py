import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor

DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    print("DATABASE_URL is not set; skipping DB initialization.")
    raise SystemExit(0)

SQL_PATH = os.path.join(os.path.dirname(__file__), "..", "migrations", "0001_initial_schema.sql")
SQL_PATH = os.path.abspath(SQL_PATH)

print("Waiting for PostgreSQL at", DB_URL)
for attempt in range(30):
    try:
        conn = psycopg2.connect(DB_URL)
        conn.close()
        break
    except Exception as exc:
        print(f"Postgres not ready yet ({exc}), retrying...")
        time.sleep(2)
else:
    raise SystemExit("Could not connect to PostgreSQL")

with open(SQL_PATH, "r", encoding="utf-8") as file:
    sql = file.read()

# Make migration idempotent for repeated startup and existing databases.
sql = sql.replace("CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ")
sql = sql.replace("CREATE INDEX ", "CREATE INDEX IF NOT EXISTS ")

print("Running database migrations from", SQL_PATH)
conn = psycopg2.connect(DB_URL)
conn.autocommit = True
with conn.cursor(cursor_factory=RealDictCursor) as cursor:
    for statement in sql.split(";"):
        statement = statement.strip()
        if not statement:
            continue
        cursor.execute(statement)
conn.close()
print("Database initialization completed.")
