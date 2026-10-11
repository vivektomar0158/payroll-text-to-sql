"""Validates LLM-generated SQL before it ever touches the read-only connection:
SELECT-only, single statement, table/column allow-list, and an enforced row cap.
"""
import re
import sqlglot
from sqlglot import exp

from app.schema import ALLOWED_TABLES, ALLOWED_COLUMNS

MAX_ROWS = 500


class SQLValidationError(Exception):
    pass


def validate_and_cap(sql: str) -> str:
    sql = sql.strip().rstrip(";")
    if ";" in sql:
        raise SQLValidationError("Multiple statements are not allowed.")

    try:
        parsed = sqlglot.parse_one(sql, dialect="sqlite")
    except Exception as e:
        raise SQLValidationError(f"SQL failed to parse: {e}")

    if not isinstance(parsed, exp.Select):
        raise SQLValidationError("Only SELECT statements are allowed.")

    forbidden = (exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create, exp.Alter)
    for node in parsed.walk():
        n = node[0] if isinstance(node, tuple) else node
        if isinstance(n, forbidden):
            raise SQLValidationError(f"Statement contains a forbidden operation: {type(n).__name__}")

    tables = {t.name.lower() for t in parsed.find_all(exp.Table)}
    unknown = tables - ALLOWED_TABLES
    if unknown:
        raise SQLValidationError(f"Query references unknown table(s): {unknown}")

    for col in parsed.find_all(exp.Column):
        col_name = col.name.lower()
        if col_name == "*":
            continue
        known = any(col_name in cols for cols in ALLOWED_COLUMNS.values())
        if not known:
            raise SQLValidationError(f"Query references unknown column: {col_name}")

    existing_limit = parsed.args.get("limit")
    if existing_limit is None:
        parsed = parsed.limit(MAX_ROWS)
    else:
        limit_val = int(existing_limit.expression.this)
        if limit_val > MAX_ROWS:
            parsed.set("limit", exp.Limit(expression=exp.Literal.number(MAX_ROWS)))

    return parsed.sql(dialect="sqlite")
