# ─────────────────────────────────────────────
#  database.py  –  SQLite Setup from CSV/Excel
# ─────────────────────────────────────────────
from __future__ import annotations   # ← fixes | None syntax on Python 3.9
import sqlite3
import pandas as pd
from pathlib import Path
import logging
from config import DB_PATH, CSV_PATH, TABLE_NAME

logger = logging.getLogger(__name__)


def _read_file(file_path: Path) -> pd.DataFrame:
    """
    Auto-detect file type and read into DataFrame.
    Supports: .csv, .xlsx, .xls, .xlsm
    """
    ext = file_path.suffix.lower()

    if ext == ".csv":
        return pd.read_csv(file_path)

    elif ext in [".xlsx", ".xls", ".xlsm"]:
        # Read first sheet by default
        return pd.read_excel(file_path, sheet_name=0)

    else:
        raise ValueError(
            f"Unsupported file type: '{ext}'. "
            "Please use .csv, .xlsx, or .xls"
        )


def load_csv_to_sqlite(csv_path: Path = CSV_PATH, db_path: Path = DB_PATH) -> bool:
    """
    Load a CSV or Excel file into a SQLite database (idempotent).
    Auto-detects file format based on extension.
    """
    try:
        df = _read_file(Path(csv_path))

        # Normalize column names → snake_case
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace(r"[^a-z0-9_]", "_", regex=True)  # remove special chars
        )

        conn = sqlite3.connect(str(db_path))
        df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
        conn.commit()
        conn.close()

        logger.info(
            f"✅ Loaded {len(df)} rows × {len(df.columns)} cols "
            f"from '{Path(csv_path).name}' into '{TABLE_NAME}' → {db_path}"
        )
        return True

    except Exception as e:
        logger.error(f"❌ Failed to load file: {e}")
        return False


def get_connection() -> sqlite3.Connection:
    """Return a live SQLite connection."""
    if not Path(DB_PATH).exists():
        load_csv_to_sqlite()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row        # dict-like rows
    return conn


def execute_query(sql: str) -> tuple[list[dict], list[str], str | None]:
    """
    Execute a SELECT query.

    Returns:
        rows    – list of dicts
        columns – list of column names
        error   – error message string or None
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [d[0] for d in cursor.description] if cursor.description else []
        rows    = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return rows, columns, None
    except Exception as e:
        return [], [], str(e)


def get_table_info() -> dict:
    """Return schema info about the retail_sales table."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
        cols = cursor.fetchall()
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        count = cursor.fetchone()[0]
        conn.close()

        columns = [{"name": c[1], "type": c[2]} for c in cols]
        return {"table": TABLE_NAME, "row_count": count, "columns": columns}
    except Exception as e:
        return {"error": str(e)}
