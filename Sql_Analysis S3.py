"""
STEP 3 — SQL ANALYSIS QUERIES
==============================
After loading data into the database, you write SQL to answer business questions.
This is exactly alysts do — turning raw data into KPIs for clients.

What this teaches:
- Writing real analytical SQL (GROUP BY, CTEs, window functions)
- Translating business questions into queries
- Preparing data for dashboards
"""

import sqlite3
import pandas as pd

DB_PATH = "sales_warehouse.db"
conn    = sqlite3.connect(DB_PATH)

print("=" * 60)
print("SQL ANALYSIS — Business Intelligence Queries")
print("=" * 60)

# ── QUERY 1: Total revenue by region ────────────────────────────────────────
print("\n[Q1] Total revenue by region (ranked):")
q1 = pd.read_sql_query("""
    SELECT
        region,
        ROUND(SUM(amount_eur), 2)        AS total_revenue,
        COUNT(transaction_id)            AS num_deals,
        ROUND(AVG(amount_eur), 2)        AS avg_deal_size,
        ROUND(SUM(amount_eur) * 100.0 /
              (SELECT SUM(amount_eur) FROM fact_sales WHERE status = 'Closed Won'), 1) AS pct_of_total
    FROM fact_sales
    WHERE status = 'Closed Won'
    GROUP BY region
    ORDER BY total_revenue DESC
""", conn)
print(q1.to_string(index=False))

# ── QUERY 2: Monthly revenue trend ──────────────────────────────────────────
print("\n[Q2] Monthly revenue trend (2023 vs 2024):")
q2 = pd.read_sql_query("""
    SELECT
        year,
        month,
        month_name,
        ROUND(SUM(amount_eur), 2) AS monthly_revenue,
        COUNT(transaction_id)     AS num_deals
    FROM fact_sales
    WHERE status = 'Closed Won'
    GROUP BY year, month, month_name
    ORDER BY year, month
""", conn)
print(q2.to_string(index=False))

# ── QUERY 3: Top sales reps ──────────────────────────────────────────────────
print("\n[Q3] Top 5 sales representatives by revenue:")
q3 = pd.read_sql_query("""
    SELECT
        sales_rep,
        ROUND(SUM(amount_eur), 2) AS total_revenue,
        COUNT(transaction_id)     AS deals_closed,
        ROUND(AVG(amount_eur), 2) AS avg_deal
    FROM fact_sales
    WHERE status = 'Closed Won'
    GROUP BY sales_rep
    ORDER BY total_revenue DESC
    LIMIT 5
""", conn)
print(q3.to_string(index=False))

# ── QUERY 4: Win rate by category ───────────────────────────────────────────
print("\n[Q4] Win rate by product category:")
q4 = pd.read_sql_query("""
    SELECT
        category,
        COUNT(*) AS total_deals,
        SUM(CASE WHEN status = 'Closed Won' THEN 1 ELSE 0 END) AS won,
        ROUND(SUM(CASE WHEN status = 'Closed Won' THEN 1 ELSE 0 END) * 100.0
              / COUNT(*), 1) AS win_rate_pct
    FROM fact_sales
    GROUP BY category
    ORDER BY win_rate_pct DESC
""", conn)
print(q4.to_string(index=False))

# ── QUERY 5: Quarter-over-quarter growth (window function) ───────────────────
print("\n[Q5] Quarter-over-quarter revenue growth (CTE + window function):")
q5 = pd.read_sql_query("""
    WITH quarterly AS (
        SELECT
            year,
            quarter,
            ROUND(SUM(amount_eur), 2) AS q_revenue
        FROM fact_sales
        WHERE status = 'Closed Won'
        GROUP BY year, quarter
    )
    SELECT
        year,
        quarter,
        q_revenue,
        LAG(q_revenue) OVER (ORDER BY year, quarter) AS prev_quarter_revenue,
        ROUND((q_revenue - LAG(q_revenue) OVER (ORDER BY year, quarter))
              * 100.0 / LAG(q_revenue) OVER (ORDER BY year, quarter), 1) AS qoq_growth_pct
    FROM quarterly
    ORDER BY year, quarter
""", conn)
print(q5.to_string(index=False))

# ── SAVE RESULTS FOR DASHBOARD ───────────────────────────────────────────────
q1.to_csv("kpi_by_region.csv",   index=False)
q2.to_csv("kpi_monthly.csv",     index=False)
q3.to_csv("kpi_top_reps.csv",    index=False)
q4.to_csv("kpi_win_rate.csv",    index=False)
q5.to_csv("kpi_qoq_growth.csv",  index=False)

conn.close()
print("\n[DONE] KPI tables saved as CSVs for dashboard input.")
