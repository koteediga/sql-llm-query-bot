# main.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from db_utils import run_query
from llm_agent import answer_question  

app = FastAPI(title="E-commerce SQL LLM API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Welcome to the E-commerce Query API"}

@app.get("/query")
def query_database(sql: str = Query(..., description="SQL SELECT to execute")):
    if not sql.strip().lower().startswith("select"):
        return {"error": "Only SELECT queries allowed."}
    try:
        return {"query": sql, "result": run_query(sql)}
    except Exception as e:
        return {"error": str(e), "query": sql}

@app.get("/ask")
def ask(question: str = Query(..., description="Ask a data question")):
    return {"question": question, **answer_question(question)}

@app.get("/chart")
def chart():
    rows = run_query(
        "SELECT date, SUM(total_sales) AS sales FROM total_sales_metrics GROUP BY date ORDER BY date;"
    )
    if not rows:
        return {"error": "No data found."}

    dates = [r[0] for r in rows]
    sales = [r[1] for r in rows]

    plt.figure(figsize=(8, 4))
    plt.plot(dates, sales, marker="o")
    plt.title("Daily Total Sales")
    plt.xlabel("Date")
    plt.ylabel("Sales")
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
