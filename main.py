from fastapi import FastAPI, Query
from db_utils import run_query
import uvicorn

app = FastAPI(title="E-commerce SQL LLM API")

@app.get("/")
def home():
    return {"message": "Welcome to the E-commerce Query API"}

@app.get("/query")
def query_database(sql: str = Query(..., description="SQL query to execute")):
    """
    Example: http://127.0.0.1:8000/query?sql=SELECT * FROM ad_sales_metrics LIMIT 5;
    """
    try:
        result = run_query(sql)
        return {"query": sql, "result": result}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
