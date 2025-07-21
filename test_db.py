from db_utils import list_tables, get_table_schema, run_query

# List all tables
print("Tables in database:")
print(list_tables())

# Get schema of a specific table
print("\nSchema of ad_sales_metrics table:")
print(get_table_schema("ad_sales_metrics"))

# Fetch first 5 rows of ad_sales_metrics
print("\nSample data from ad_sales_metrics table:")
print(run_query("SELECT * FROM ad_sales_metrics LIMIT 5;"))
