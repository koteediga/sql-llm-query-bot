import os
from db_utils import run_query, list_tables, get_table_schema
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()  # This line loads .env file into environment

# Ensure your API key is set in the environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set.")

genai.configure(api_key=GEMINI_API_KEY)

def build_schema_prompt():
    """Return all tables and columns for prompt context."""
    tables = list_tables()
    schema_lines = []
    for tup in tables:
        table = tup[0]
        columns = get_table_schema(table)
        col_names = [row[1] for row in columns]
        schema_lines.append(f"Table: {table} ({', '.join(col_names)})")
    return "\n".join(schema_lines)

def get_sql_from_llm(question: str, schema_prompt: str):
    system_prompt = (
        f"You are an expert SQL assistant. Here is the database schema:\n{schema_prompt}\n"
        "Write the optimal SQLite query for the user prompt below, and output ONLY the SQL:"
    )
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([system_prompt, question])
    return response.text.strip().strip("`")  # handle possible markdown/code blocks

def answer_question(question: str):
    schema = build_schema_prompt()
    sql = get_sql_from_llm(question, schema)
    try:
        result = run_query(sql)
        return {"question": question, "sql": sql, "result": result}
    except Exception as e:
        return {"question": question, "sql": sql, "error": str(e)}
