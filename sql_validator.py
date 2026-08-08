# ─────────────────────────────────────────────
#  sql_validator.py  –  SQL Safety & Syntax
# ─────────────────────────────────────────────
import re
import sqlparse
from sqlparse.sql import Statement
from sqlparse.tokens import Keyword, DDL, DML

from config import TABLE_NAME


# Blocked keywords that must never appear in a generated query
BLOCKED_KEYWORDS = {
    "DROP", "DELETE", "INSERT", "UPDATE", "TRUNCATE",
    "ALTER", "CREATE", "REPLACE", "ATTACH", "DETACH",
}

# Columns that must exist in the table
VALID_COLUMNS = {
    "transaction_id", "date", "customer_id", "gender", "age",
    "product_category", "quantity", "price_per_unit", "total_amount",
}


def validate_sql(sql: str) -> tuple[bool, str]:
    """
    Validate a generated SQL query for safety and correctness.

    Returns:
        (is_valid: bool, message: str)
    """
    if not sql or not sql.strip():
        return False, "SQL query is empty."

    sql_upper = sql.upper()

    # 1. Block dangerous statements
    for kw in BLOCKED_KEYWORDS:
        pattern = r"\b" + kw + r"\b"
        if re.search(pattern, sql_upper):
            return False, f"Dangerous keyword detected: {kw}"

    # 2. Must be a SELECT
    parsed = sqlparse.parse(sql)
    if not parsed:
        return False, "Could not parse SQL."

    stmt: Statement = parsed[0]
    first_dml = next(
        (t for t in stmt.flatten() if t.ttype in (DML,)), None
    )
    if first_dml is None or first_dml.value.upper() != "SELECT":
        return False, "Only SELECT statements are allowed."

    # 3. Must reference the correct table
    if TABLE_NAME.lower() not in sql.lower():
        return (
            False,
            f"Query must reference the table '{TABLE_NAME}'. "
            "Check that the LLM used the correct table name.",
        )

    # 4. Light syntax check via sqlparse round-trip
    try:
        reformatted = sqlparse.format(sql, reindent=False, keyword_case="upper")
        if not reformatted.strip():
            return False, "SQL appears malformed after parsing."
    except Exception as e:
        return False, f"SQL parse error: {e}"

    return True, "✅ SQL is valid."


def format_sql(sql: str) -> str:
    """Return a prettily formatted version of the SQL query."""
    try:
        return sqlparse.format(
            sql,
            reindent=True,
            keyword_case="upper",
            identifier_case="lower",
            strip_comments=True,
        )
    except Exception:
        return sql
