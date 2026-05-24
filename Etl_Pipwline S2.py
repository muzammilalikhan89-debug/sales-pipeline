"""
STEP 2 — ETL PIPELINE (Extract → Transform → Load)
====================================================
This is the most important skill for a Deloitte Data Analyst.
Real client data is always messy. Your job is to clean it and load it
into a structured database (here: SQLite, same concepts as SQL Server).

What this teaches:
- Pandas data cleaning (the core of a data analyst's job)
- Handling nulls, duplicates, case inconsistencies
- Loading into a relational database using SQL
- Writing audit logs (critical in consulting — you must document every change)
"""

import pandas as pd
import sqlite3
import os

DB_PATH  = "sales_warehouse.db"
CSV_PATH = "raw_sales_data.csv"
LOG_PATH = "etl_audit_log.txt"

# ── AUDIT LOG SETUP ─────────────────────────────────────────────────────────
log_lines = []
def log(msg):
    print(msg)
    log_lines.append(msg)

log("=" * 60)
log("ETL PIPELINE — Deloitte Sales Data Warehouse")
log("=" * 60)

# ── EXTRACT ──────────────────────────────────────────────────────────────────
log("\n[EXTRACT] Loading raw CSV...")
df = pd.read_csv(CSV_PATH)
log(f"  Rows loaded     : {len(df)}")
log(f"  Columns         : {list(df.columns)}")
log(f"  Missing values  :\n{df.isnull().sum().to_string()}")

original_count = len(df)

# ── TRANSFORM ────────────────────────────────────────────────────────────────
log("\n[TRANSFORM] Cleaning data...")

# 1. Remove rows with invalid dates
bad_dates = df[df["date"] == "N/A"].shape[0]
df = df[df["date"] != "N/A"].copy()
df["date"] = pd.to_datetime(df["date"])
log(f"  Removed {bad_dates} rows with invalid dates")

# 2. Drop rows with missing amount
missing_amounts = df["amount_eur"].isna().sum()
df = df.dropna(subset=["amount_eur"])
log(f"  Removed {missing_amounts} rows with missing amount")

# 3. Remove negative amounts (data entry errors) — flag them first
negative_amounts = (df["amount_eur"] < 0).sum()
df = df[df["amount_eur"] >= 0]
log(f"  Removed {negative_amounts} rows with negative amounts")

# 4. Standardise text columns — Title Case, strip whitespace
df["sales_rep"] = df["sales_rep"].fillna("Unknown").str.strip().str.title()
df["status"]    = df["status"].fillna("Unknown").str.strip().str.title()
df["notes"]     = df["notes"].fillna("").str.strip()

# 5. Deduplicate (keep first occurrence)
before_dedup = len(df)
df = df.drop_duplicates(subset=["transaction_id"])
after_dedup  = len(df)
log(f"  Removed {before_dedup - after_dedup} duplicate transaction IDs")

# 6. Add derived columns useful for reporting
df["year"]    = df["date"].dt.year
df["month"]   = df["date"].dt.month
df["quarter"] = df["date"].dt.quarter
df["month_name"] = df["date"].dt.strftime("%b")

log(f"\n  Final clean rows : {len(df)}  (started with {original_count})")
log(f"  Rows removed     : {original_count - len(df)}")

# ── LOAD INTO SQLITE DATABASE ────────────────────────────────────────────────
log("\n[LOAD] Writing to SQLite database (equivalent to SQL Server in production)...")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create the fact table
cursor.execute("DROP TABLE IF EXISTS fact_sales")
cursor.execute("""
    CREATE TABLE fact_sales (
        transaction_id TEXT PRIMARY KEY,
        date           TEXT,
        sales_rep      TEXT,
        region         TEXT,
        category       TEXT,
        amount_eur     REAL,
        status         TEXT,
        notes          TEXT,
        year           INTEGER,
        month          INTEGER,
        quarter        INTEGER,
        month_name     TEXT
    )
""")

# Also create an aggregated summary table (Data Warehouse concept: "fact" vs "aggregate")
cursor.execute("DROP TABLE IF EXISTS agg_monthly_region")
cursor.execute("""
    CREATE TABLE agg_monthly_region (
        year       INTEGER,
        month      INTEGER,
        quarter    INTEGER,
        region     TEXT,
        category   TEXT,
        total_revenue REAL,
        num_deals     INTEGER,
        avg_deal_size REAL
    )
""")

df.to_sql("fact_sales", conn, if_exists="replace", index=False)

agg = (df.groupby(["year", "month", "quarter", "region", "category"])
         .agg(total_revenue=("amount_eur", "sum"),
              num_deals=("transaction_id", "count"),
              avg_deal_size=("amount_eur", "mean"))
         .reset_index())
agg["total_revenue"]  = agg["total_revenue"].round(2)
agg["avg_deal_size"]  = agg["avg_deal_size"].round(2)
agg.to_sql("agg_monthly_region", conn, if_exists="replace", index=False)

conn.commit()
conn.close()

log(f"  fact_sales table          : {len(df)} rows")
log(f"  agg_monthly_region table  : {len(agg)} rows")
log(f"  Database saved to         : {DB_PATH}")

# ── WRITE AUDIT LOG ──────────────────────────────────────────────────────────
with open(LOG_PATH, "w") as f:
    f.write("\n".join(log_lines))
log(f"\n[AUDIT] Log written to: {LOG_PATH}")
log("\nETL COMPLETE ✓")
