from db_utils import run_query

def get_total_sales():
    sql = "SELECT SUM(total_sales) as total_sales FROM total_sales_metrics;"
    result = run_query(sql)
    return result[0][0] if result else 0

def get_roas():
    # RoAS = Total Ad Sales / Total Ad Spend
    sql = """
    SELECT 
        (SELECT SUM(ad_sales) FROM ad_sales_metrics) /
        (SELECT SUM(ad_spend) FROM ad_sales_metrics) AS roas;
    """
    result = run_query(sql)
    return result[0][0] if result else 0

def get_highest_cpc_product():
    # CPC = ad_spend / clicks
    sql = """
    SELECT item_id, 
           CASE WHEN clicks > 0 THEN (ad_spend * 1.0 / clicks) ELSE 0 END AS cpc
    FROM ad_sales_metrics
    ORDER BY cpc DESC
    LIMIT 1;
    """
    result = run_query(sql)
    return {"item_id": result[0][0], "cpc": result[0][1]} if result else {}
