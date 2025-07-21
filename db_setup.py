import pandas as pd
import sqlite3
import os

# Check if CSV files exist
files = ["ad_sales_metrics.csv", "total_sales_metrics.csv", "eligibility.csv"]
for file in files:
    if not os.path.exists(file):
        print(f"Error: {file} not found! Please place it in the project folder.")
        exit()

# Load datasets into Pandas DataFrames
df_ads = pd.read_csv("ad_sales_metrics.csv")
df_total = pd.read_csv("total_sales_metrics.csv")
df_eligibility = pd.read_csv("eligibility.csv")

# Create SQLite database
conn = sqlite3.connect("ecommerce.db")

# Write dataframes to SQL tables
df_ads.to_sql("ad_sales_metrics", conn, if_exists="replace", index=False)
df_total.to_sql("total_sales_metrics", conn, if_exists="replace", index=False)
df_eligibility.to_sql("eligibility", conn, if_exists="replace", index=False)

conn.close()
print("Database 'ecommerce.db' created with 3 tables: ad_sales_metrics, total_sales_metrics, eligibility.")
