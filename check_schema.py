from db_utils import get_table_schema

print("ad_sales_metrics:")
print(get_table_schema("ad_sales_metrics"))
print("\n")

print("total_sales_metrics:")
print(get_table_schema("total_sales_metrics"))
print("\n")

print("eligibility:")
print(get_table_schema("eligibility"))
print("\n")
