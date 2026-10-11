"""Read-only DB access. SQLite has no GRANT system, so read-only is enforced by
opening the connection in `mode=ro` (any write attempt raises at the driver level)
in addition to the SQL-level validator rejecting non-SELECT statements."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "payroll.db"


def get_readonly_connection() -> sqlite3.Connection:
    uri = f"file:{DB_PATH.as_posix()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def run_query(sql: str, max_rows: int = 500) -> list[dict]:
    conn = get_readonly_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchmany(max_rows)
        return [dict(zip(cols, row)) for row in rows]
    finally:
        conn.close()
