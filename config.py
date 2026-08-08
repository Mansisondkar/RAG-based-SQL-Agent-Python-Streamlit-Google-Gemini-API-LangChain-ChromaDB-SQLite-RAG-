# ─────────────────────────────────────────────
#  config.py  –  Central Configuration
# ─────────────────────────────────────────────
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
# ── Paths ──────────────────────────────────────
BASE_DIR   = Path(__file__).parent
DATA_DIR   = BASE_DIR                          # CSV lives here
DB_PATH    = BASE_DIR / "retail_sales.db"
CHROMA_DIR = BASE_DIR / "chroma_store"
CSV_PATH   = BASE_DIR / "retail_sales_dataset.csv"
# ── Database ────────────────────────────────────
TABLE_NAME = "retail_sales"
# ── Groq LLM (100% FREE — no quota issues) ────────────────────
# ── RAG ─────────────────────────────────────────
EMBEDDING_MODEL       = "all-MiniLM-L6-v2"
CHROMA_COLLECTION     = "retail_schema_context"
TOP_K_RESULTS         = 5
# ── Schema Metadata (used to build RAG context) ─
SCHEMA_DESCRIPTION = """
Table: retail_sales
Columns:
  - transaction_id  : INTEGER  – Unique identifier for each transaction
  - date            : TEXT     – Date of the transaction (YYYY-MM-DD)
  - customer_id     : TEXT     – Unique customer identifier (e.g. CUST001)
  - gender          : TEXT     – Customer gender (Male / Female)
  - age             : INTEGER  – Customer age in years
  - product_category: TEXT     – Product category (Beauty / Clothing / Electronics)
  - quantity        : INTEGER  – Number of units purchased
  - price_per_unit  : REAL     – Price of one unit in USD
  - total_amount    : REAL     – Total transaction value (quantity × price_per_unit)
Sample rows:
  (1, '2023-11-24', 'CUST001', 'Male',   34, 'Beauty',      3, 50,  150)
  (2, '2023-02-27', 'CUST002', 'Female', 26, 'Clothing',    2, 500, 1000)
  (3, '2023-01-13', 'CUST003', 'Male',   50, 'Electronics', 1, 30,  30)
"""
# ── RAG knowledge chunks ─────────────────────────
RAG_CHUNKS = [
    {
        "id": "schema_overview",
        "text": SCHEMA_DESCRIPTION,
        "metadata": {"type": "schema", "table": TABLE_NAME},
    },
    {
        "id": "date_usage",
        "text": (
            "The 'date' column stores dates in YYYY-MM-DD format. "
            "Use strftime('%Y', date) to extract the year, "
            "strftime('%m', date) for month, "
            "strftime('%Y-%m', date) for year-month grouping. "
            "Example: SELECT strftime('%Y-%m', date) AS month, SUM(total_amount) FROM retail_sales GROUP BY month;"
        ),
        "metadata": {"type": "usage", "topic": "dates"},
    },
    {
        "id": "aggregation_examples",
        "text": (
            "Common aggregation queries on retail_sales:\n"
            "- Total revenue: SELECT SUM(total_amount) FROM retail_sales;\n"
            "- Revenue by category: SELECT product_category, SUM(total_amount) AS revenue FROM retail_sales GROUP BY product_category;\n"
            "- Average order value: SELECT AVG(total_amount) FROM retail_sales;\n"
            "- Top customers: SELECT customer_id, SUM(total_amount) AS total FROM retail_sales GROUP BY customer_id ORDER BY total DESC LIMIT 10;"
        ),
        "metadata": {"type": "example", "topic": "aggregation"},
    },
    {
        "id": "filter_examples",
        "text": (
            "Filtering examples on retail_sales:\n"
            "- Filter by gender: WHERE gender = 'Female'\n"
            "- Filter by category: WHERE product_category = 'Electronics'\n"
            "- Filter by age range: WHERE age BETWEEN 20 AND 35\n"
            "- Filter by date range: WHERE date BETWEEN '2023-01-01' AND '2023-06-30'\n"
            "- Filter by amount: WHERE total_amount > 500"
        ),
        "metadata": {"type": "example", "topic": "filtering"},
    },
    {
        "id": "gender_category_analysis",
        "text": (
            "Gender-based analysis: SELECT gender, COUNT(*) AS transactions, SUM(total_amount) AS revenue "
            "FROM retail_sales GROUP BY gender;\n"
            "Category preferences by gender: SELECT gender, product_category, COUNT(*) AS cnt "
            "FROM retail_sales GROUP BY gender, product_category ORDER BY gender, cnt DESC;"
        ),
        "metadata": {"type": "example", "topic": "gender_analysis"},
    },
    {
        "id": "age_group_analysis",
        "text": (
            "Age-group analysis using CASE:\n"
            "SELECT CASE WHEN age < 25 THEN 'Under 25' WHEN age BETWEEN 25 AND 40 THEN '25-40' "
            "WHEN age BETWEEN 41 AND 60 THEN '41-60' ELSE 'Over 60' END AS age_group, "
            "COUNT(*) AS transactions, SUM(total_amount) AS revenue "
            "FROM retail_sales GROUP BY age_group ORDER BY revenue DESC;"
        ),
        "metadata": {"type": "example", "topic": "age_analysis"},
    },
    {
        "id": "monthly_trends",
        "text": (
            "Monthly sales trends query:\n"
            "SELECT strftime('%Y-%m', date) AS month, SUM(total_amount) AS monthly_revenue, "
            "COUNT(*) AS num_transactions FROM retail_sales GROUP BY month ORDER BY month;"
        ),
        "metadata": {"type": "example", "topic": "trends"},
    },
    {
        "id": "product_performance",
        "text": (
            "Product category performance:\n"
            "SELECT product_category, COUNT(*) AS total_orders, SUM(quantity) AS total_units_sold, "
            "SUM(total_amount) AS total_revenue, AVG(price_per_unit) AS avg_price "
            "FROM retail_sales GROUP BY product_category ORDER BY total_revenue DESC;"
        ),
        "metadata": {"type": "example", "topic": "product_performance"},
    },
    {
        "id": "sql_rules",
        "text": (
            "IMPORTANT SQL rules for retail_sales SQLite database:\n"
            "1. Always use exact column names: transaction_id, date, customer_id, gender, age, "
            "product_category, quantity, price_per_unit, total_amount.\n"
            "2. String comparisons are case-sensitive; use exact case: 'Male', 'Female', "
            "'Beauty', 'Clothing', 'Electronics'.\n"
            "3. Use SQLite-compatible functions (strftime, NOT DATE_FORMAT).\n"
            "4. Always add LIMIT clause for large result sets.\n"
            "5. Use table name: retail_sales (not retail_sales_dataset)."
        ),
        "metadata": {"type": "rules", "topic": "sql_rules"},
    },
]