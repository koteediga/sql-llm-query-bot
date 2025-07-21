from metrics import get_total_sales, get_roas, get_highest_cpc_product
from db_utils import run_query

def answer_question(question: str):
    q = question.lower()

    if "total sales" in q:
        return {"total_sales": get_total_sales()}
    elif "roas" in q or "return on ad spend" in q:
        return {"roas": get_roas()}
    elif "highest cpc" in q or "cost per click" in q:
        return {"highest_cpc": get_highest_cpc_product()}
    else:
        return {"error": "I couldn't understand your question. Please ask about total sales, RoAS, or highest CPC."}
