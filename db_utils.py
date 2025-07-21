import sqlite3

DB_NAME = "ecommerce.db"

def run_query(query):
    """Runs a SQL query and returns the results."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def list_tables():
    """Lists all tables in the database."""
    return run_query("SELECT name FROM sqlite_master WHERE type='table';")

def get_table_schema(table_name):
    """Returns the schema (columns) of a given table."""
    return run_query(f"PRAGMA table_info({table_name});")
