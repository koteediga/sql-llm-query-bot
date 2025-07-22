"""
llm_agent.py

Natural-language → SQL agent for the E-commerce DB.
Uses Gemini (if API key available) + reliable rule-based fallbacks
for required assignment questions (Total Sales, RoAS, Highest CPC, etc.).
"""

import os
import re
from typing import Optional, Dict, Any, List, Tuple

from db_utils import run_query, list_tables, get_table_schema

# ------------------------------------------------------------
# Optional .env support (safe no-op if python-dotenv not installed)
# ------------------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ------------------------------------------------------------
# Gemini API config
# ------------------------------------------------------------
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
USE_LLM = bool(API_KEY)

if USE_LLM:
    import google.generativeai as genai
    genai.configure(api_key=API_KEY)
    _model = genai.GenerativeModel("gemini-1.5-flash")
else:
    print("[llm_agent] WARNING: No Gemini key found. Running in rule-based mode only.")


# ------------------------------------------------------------
# Schema builder (fresh from DB each call so always in sync)
# ------------------------------------------------------------
def _build_schema_text() -> str:
    lines = []
    for (tname,) in list_tables():
        cols = get_table_schema(tname)
        col_txt = ", ".join([c[1] for c in cols])  # index 1 = column name
        lines.append(f"{tname}({col_txt})")
    return "\n".join(lines)


# ------------------------------------------------------------
# Few-shot prompt examples (help guide Gemini)
# ------------------------------------------------------------
FEW_SHOT = """
Example:
Q: What is my total sales?
SQL:
SELECT SUM(total_sales) AS total_sales FROM total_sales_metrics;

Example:
Q: Calculate the RoAS.
-- RoAS = SUM(ad_sales) / SUM(ad_spend)
SQL:
SELECT SUM(ad_sales)*1.0 / NULLIF(SUM(ad_spend),0) AS roas
FROM ad_sales_metrics;

Example:
Q: Which product had the highest CPC?
-- CPC = ad_spend / clicks
SQL:
SELECT item_id,
       MAX(CASE WHEN clicks>0 THEN ad_spend*1.0/clicks END) AS max_cpc
FROM ad_sales_metrics
GROUP BY item_id
ORDER BY max_cpc DESC
LIMIT 1;
"""


PROMPT = """You are an expert SQLite analyst. Write ONE valid SELECT query.
Rules:
- Use the schema exactly as given.
- Use SUM/AVG/COUNT when totals requested.
- Use NULLIF(x,0) in divisions to avoid divide-by-zero.
- No comments or explanations in final output.
- Output ONLY SQL (no backticks).

Schema:
{schema}

{few_shot}

Question: {question}

SQL:
"""


# ------------------------------------------------------------
# Rule-based shortcuts (fast & guaranteed for demo)
# ------------------------------------------------------------
def _shortcut(question: str) -> Optional[str]:
    q = question.lower()

    # Total sales grouped?
    if "total sales" in q and ("per" in q or "by" in q):
        return (
            "SELECT item_id, SUM(total_sales) AS total_sales "
            "FROM total_sales_metrics GROUP BY item_id ORDER BY total_sales DESC;"
        )

    # Total sales overall
    if "total sales" in q:
        return "SELECT SUM(total_sales) AS total_sales FROM total_sales_metrics;"

    # RoAS
    if "roas" in q or "return on ad spend" in q:
        return (
            "SELECT SUM(ad_sales)*1.0/NULLIF(SUM(ad_spend),0) AS roas "
            "FROM ad_sales_metrics;"
        )

    # Highest CPC
    if "cpc" in q or "cost per click" in q:
        return (
            "SELECT item_id, MAX(CASE WHEN clicks>0 THEN ad_spend*1.0/clicks END) AS max_cpc "
            "FROM ad_sales_metrics GROUP BY item_id ORDER BY max_cpc DESC LIMIT 1;"
        )

    # Top impressions
    if "impressions" in q and "top" in q:
        return (
            "SELECT item_id, SUM(impressions) AS total_impressions "
            "FROM ad_sales_metrics GROUP BY item_id ORDER BY total_impressions DESC LIMIT 5;"
        )

    # Eligible products
    if "eligible" in q and ("products" in q or "items" in q):
        return "SELECT item_id FROM eligibility WHERE eligibility = 1;"

    return None


# ------------------------------------------------------------
# Gemini call + cleaning
# ------------------------------------------------------------
def _call_gemini(prompt: str) -> str:
    resp = _model.generate_content(prompt)
    return (resp.text or "").strip()


def _clean_sql(text: str) -> str:
    s = text.strip()
    s = re.sub(r"^```sql", "", s, flags=re.I).strip()
    s = re.sub(r"^```", "", s).strip()
    s = re.sub(r"```$", "", s).strip()
    # first statement only
    if ";" in s:
        s = s.split(";")[0].strip()
    if not s.endswith(";"):
        s += ";"
    return s


def _safe(sql: str) -> bool:
    s = sql.strip().lower()
    if not s.startswith("select"):
        return False
    banned = ["insert", "update", "delete", "drop", "alter", "attach", "pragma", "--", "/*"]
    return not any(b in s for b in banned)


# ------------------------------------------------------------
# Public: generate SQL
# ------------------------------------------------------------
def generate_sql(question: str) -> str:
    # 1. shortcuts
    s = _shortcut(question)
    if s:
        return s

    # 2. Gemini
    if USE_LLM:
        schema = _build_schema_text()
        prompt = PROMPT.format(schema=schema, few_shot=FEW_SHOT, question=question)
        raw = _call_gemini(prompt)
        return _clean_sql(raw)

    # 3. Fallback (no key, no rule)
    return "SELECT 'LLM not configured; ask about total sales, RoAS, or CPC.' AS message;"


# ------------------------------------------------------------
# Public: answer_question
# ------------------------------------------------------------
def answer_question(question: str) -> Dict[str, Any]:
    sql = generate_sql(question)

    if not _safe(sql):
        return {"sql": sql, "error": "Unsafe or non-SELECT SQL generated."}

    try:
        rows = run_query(sql)
    except Exception as e:
        return {"sql": sql, "error": str(e)}

    return {
        "sql": sql,
        "rows": rows,
        "summary": _summary(question, rows),
        "used_gemini": USE_LLM,
    }


# ------------------------------------------------------------
# Simple summarizer for nicer frontend output
# ------------------------------------------------------------
def _summary(question: str, rows: List[Tuple]) -> str:
    if not rows:
        return "No data."
    q = question.lower()

    if "total sales" in q and len(rows[0]) == 1:
        return f"Total sales = {rows[0][0]}"
    if "roas" in q:
        return f"RoAS = {rows[0][0]}"
    if "cpc" in q:
        r = rows[0]
        return f"Item {r[0]} highest CPC = {r[1]}" if len(r) > 1 else f"CPC row: {r}"
    return f"First row: {rows[0]}"
