# ─────────────────────────────────────────────
#  llm_engine.py  –  Google Gemini Integration
# ─────────────────────────────────────────────
from __future__ import annotations   # ← fixes | None syntax on Python 3.9
import logging
import re
from openai import OpenAI
from config import (
    GEMINI_API_KEY,
    GEMINI_BASE_URL,
    GEMINI_MODEL,
    MAX_TOKENS,
    TEMPERATURE,
    TABLE_NAME,
)
logger = logging.getLogger(__name__)
def _get_client(api_key: str | None = None) -> OpenAI:
    key = api_key or GEMINI_API_KEY
    if not key:
        raise ValueError("Gemini API key is not set.")
    return OpenAI(api_key=key, base_url=GEMINI_BASE_URL)
# ── SQL Generation ────────────────────────────────────────────────────────────
SQL_SYSTEM_PROMPT = """You are an expert SQLite data analyst.
Your job is to convert a natural language question into a valid, executable SQLite SELECT query.
Rules:
1. Output ONLY the raw SQL query — no markdown fences, no explanations.
2. Always query the table: retail_sales
3. Column names: transaction_id, date, customer_id, gender, age,
   product_category, quantity, price_per_unit, total_amount
4. For date functions, use SQLite syntax: strftime('%Y', date), NOT YEAR(date).
5. String values are case-sensitive: 'Male'/'Female', 'Beauty'/'Clothing'/'Electronics'.
6. Add LIMIT 100 unless the user asks for all rows or an aggregation.
7. Never use DROP, INSERT, UPDATE, DELETE, or DDL statements.
"""
def generate_sql(
    question: str,
    context: str,
    api_key: str | None = None,
) -> tuple[str, str | None]:
    """
    Generate a SQL query from a natural language question using Gemini.
    Args:
        question: The user's natural language question.
        context:  RAG-retrieved schema/example context.
        api_key:  Optional override for the Gemini API key.
    Returns:
        (sql_query, error_message)  –  error_message is None on success.
    """
    try:
        client = _get_client(api_key)
        user_prompt = f"""
Relevant database context:
{context}
User question:
{question}
Generate the SQLite SELECT query:
"""
        response = client.chat.completions.create(
            model=GEMINI_MODEL,
            messages=[
                {"role": "system", "content": SQL_SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
        sql = response.choices[0].message.content.strip()
        # Strip accidental markdown fences
        sql = re.sub(r"```(?:sql)?", "", sql, flags=re.IGNORECASE).strip()
        sql = sql.strip("`").strip()
        return sql, None
    except Exception as e:
        logger.error(f"❌ SQL generation failed: {e}")
        return "", str(e)
# ── Insight Generation ────────────────────────────────────────────────────────
INSIGHT_SYSTEM_PROMPT = """You are a retail analytics expert.
Given a SQL query, its results, and the original user question,
provide a concise, insightful business summary in 3–5 bullet points.
Focus on patterns, trends, and actionable takeaways.
Use plain English; avoid technical jargon.
"""
def generate_insights(
    question: str,
    sql: str,
    results_preview: str,
    api_key: str | None = None,
) -> tuple[str, str | None]:
    """
    Generate business insights from query results using Gemini.
    Returns:
        (insight_text, error_message)
    """
    try:
        client = _get_client(api_key)
        user_prompt = f"""
Original question: {question}
SQL query executed:
{sql}
Query results (first rows):
{results_preview}
Provide 3-5 business insights:
"""
        response = client.chat.completions.create(
            model=GEMINI_MODEL,
            messages=[
                {"role": "system", "content": INSIGHT_SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens=512,
            temperature=0.3,
        )
        insights = response.choices[0].message.content.strip()
        return insights, None
    except Exception as e:
        logger.error(f"❌ Insight generation failed: {e}")
        return "", str(e)
