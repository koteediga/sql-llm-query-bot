from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
import uvicorn
import os
from db_utils import run_query
from nl_sql_agent import answer_question

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

@app.get("/ask")
def ask_question(question: str = Query(..., description="Natural language question")):
    """
    Example: http://127.0.0.1:8000/ask?question=What is my total sales?
    """
    return answer_question(question)

@app.get("/chart")
def get_sales_chart():
    """
    Bonus: Generate a daily sales chart and return as an image.
    """
    from charts import generate_sales_chart
    img_path = generate_sales_chart()
    return FileResponse(img_path)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
