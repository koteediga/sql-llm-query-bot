import os
import google.generativeai as genai
from db_utils import run_query

# Load API Key
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "Gemini API key not found. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable."
    )

genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-1.5-flash"  # You can switch to pro if available
model = genai.GenerativeModel(MODEL_NAME)

# Database schema for reference
SCHEMA = """
Tables:
1. ad_sales_metrics(date TEXT, item_id INTEGER, ad_sales REAL, impressions INTEGER, ad_spend REAL, clicks INTEGER, units_sold INTEGER)
2. total_sales_metrics(date TEXT, item_id INTEGER, total_sales REAL, total_units_ordered INTEGER)
3. eligibility(eligibility_datetime_utc TEXT, item_id INTEGER, eligibility INTEGER, message TEXT)
"""

PROMPT_TEMPLATE = """You are an expert data analyst. Convert the user question into a SINGLE valid SQLite SELECT query.

Rules:
- Use only the tables and columns from the schema.
- Use aggregates like SUM, AVG when totals are requested.
- Use NULLIF to prevent division by zero (e.g., ad_spend/NULLIF(clicks, 0)).
- Output ONLY the SQL query without explanation or extra text.

Schema:
{schema}

Question: {question}

SQL:
"""

def question_to_sql(question: str) -> str:
    prompt = PROMPT_TEMPLATE.format(schema=SCHEMA, question=question)
    response = model.generate_content(prompt)
    sql = response.text.strip()

    # Clean up any code fences
    if sql.startswith("```"):
        sql = sql.strip("`").replace("sql", "").strip()

    # Ensure single statement ending with ;
    if ";" not in sql:
        sql += ";"
    return sql

def answer_question(question: str):
    try:
        sql = question_to_sql(question)
        if not sql.lower().startswith("select"):
            return {"error": "Generated SQL is not a SELECT query.", "sql": sql}
        result = run_query(sql)
        return {"question": question, "sql": sql, "answer": result}
    except Exception as e:
        return {"error": str(e), "question": question}
