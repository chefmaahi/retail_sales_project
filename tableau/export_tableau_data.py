"""
Tableau Data Prep — Export optimized CSVs including Region data.
"""

import sqlite3, pandas as pd, os

DB_PATH  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "db", "retail_sales.db")
OUT_DIR  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tableau")
PROC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "processed")

def conn(): return sqlite3.connect(DB_PATH)

def export_all():
    os.makedirs(OUT_DIR, exist_ok=True)

    # ── 01: Main Fact Table (with Region) ────────────────────────
    df = pd.read_sql("""
        SELECT f.transaction_id,
               f.date_key                       AS date,
               d.year, d.quarter, d.month, d.month_name,
               d.week, d.day_name, d.is_weekend,
               f.customer_id, c.gender, c.age, c.age_group,
               p.category                       AS product_category,
               r.region_name                    AS region,
               f.quantity, f.price_per_unit,
               f.total_amount, f.profit,
               30.0                             AS profit_margin_pct
        FROM fact_sales f
        JOIN dim_date      d ON f.date_key   = d.date_key
        JOIN dim_customers c ON f.customer_id= c.customer_id
        JOIN dim_products  p ON f.product_id = p.product_id
        JOIN dim_region    r ON f.region_id  = r.region_id
        ORDER BY f.date_key
    """, conn())
    df.to_csv(f"{OUT_DIR}/01_sales_transactions.csv", index=False)
    print(f"✓ 01_sales_transactions.csv   ({len(df):,} rows)")

    # ── 02: Monthly KPIs ─────────────────────────────────────────
    df2 = pd.read_sql("""
        SELECT year_month, total_revenue, total_orders, avg_order_value,
               unique_customers, total_quantity, total_profit,
               30.0 AS profit_margin_pct
        FROM agg_monthly_kpis ORDER BY year_month
    """, conn())
    df2.to_csv(f"{OUT_DIR}/02_monthly_kpis.csv", index=False)
    print(f"✓ 02_monthly_kpis.csv          ({len(df2):,} rows)")

    # ── 03: Category Performance ──────────────────────────────────
    df3 = pd.read_sql("""
        SELECT year_month, category, revenue, orders, avg_price
        FROM agg_category_performance ORDER BY year_month, category
    """, conn())
    df3.to_csv(f"{OUT_DIR}/03_category_performance.csv", index=False)
    print(f"✓ 03_category_performance.csv  ({len(df3):,} rows)")

    # ── 04: Customer Demographics ─────────────────────────────────
    df4 = pd.read_sql("""
        SELECT c.customer_id, c.gender, c.age, c.age_group,
               r.region_name AS region,
               COUNT(f.transaction_id) AS total_orders,
               SUM(f.total_amount)     AS total_spent,
               AVG(f.total_amount)     AS avg_order_value,
               MAX(f.date_key)         AS last_purchase_date
        FROM dim_customers c
        JOIN fact_sales f  ON c.customer_id = f.customer_id
        JOIN dim_region r  ON f.region_id   = r.region_id
        GROUP BY c.customer_id, r.region_name
    """, conn())
    df4.to_csv(f"{OUT_DIR}/04_customer_demographics.csv", index=False)
    print(f"✓ 04_customer_demographics.csv ({len(df4):,} rows)")

    # ── 05: Forecasts ─────────────────────────────────────────────
    fc_src = os.path.join(PROC_DIR, "forecasts.csv")
    if os.path.exists(fc_src):
        df5 = pd.read_csv(fc_src)
        df5.to_csv(f"{OUT_DIR}/05_forecasts.csv", index=False)
        print(f"✓ 05_forecasts.csv             ({len(df5):,} rows)")

    # ── 06: Seasonality Heatmap ───────────────────────────────────
    df6 = pd.read_sql("""
        SELECT d.year, d.month, d.month_name, p.category,
               SUM(f.total_amount) AS revenue, COUNT(*) AS orders
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_products p ON f.product_id = p.product_id
        GROUP BY d.year, d.month, d.month_name, p.category
        ORDER BY d.year, d.month
    """, conn())
    df6.to_csv(f"{OUT_DIR}/06_seasonality_heatmap.csv", index=False)
    print(f"✓ 06_seasonality_heatmap.csv   ({len(df6):,} rows)")

    # ── 07: Region Performance (NEW) ──────────────────────────────
    df7 = pd.read_sql("""
        SELECT year_month, region_name, revenue, orders, profit, avg_order_value
        FROM agg_region_performance ORDER BY year_month, region_name
    """, conn())
    df7.to_csv(f"{OUT_DIR}/07_region_performance.csv", index=False)
    print(f"✓ 07_region_performance.csv    ({len(df7):,} rows)")

    # ── 08: Region × Category (NEW) ───────────────────────────────
    df8 = pd.read_sql("""
        SELECT r.region_name, p.category,
               SUM(f.total_amount)  AS revenue,
               COUNT(*)             AS orders,
               SUM(f.profit)        AS profit,
               AVG(f.total_amount)  AS avg_order_value
        FROM fact_sales f
        JOIN dim_region   r ON f.region_id  = r.region_id
        JOIN dim_products p ON f.product_id = p.product_id
        GROUP BY r.region_name, p.category
        ORDER BY r.region_name, revenue DESC
    """, conn())
    df8.to_csv(f"{OUT_DIR}/08_region_category.csv", index=False)
    print(f"✓ 08_region_category.csv       ({len(df8):,} rows)")

    # ── 09: Statistical Analysis (NEW) ────────────────────────────
    df9 = pd.read_sql("""
        SELECT r.region_name, d.month, d.month_name,
               SUM(f.total_amount) AS revenue,
               COUNT(*)            AS orders,
               AVG(f.total_amount) AS avg_order_value
        FROM fact_sales f
        JOIN dim_date   d ON f.date_key  = d.date_key
        JOIN dim_region r ON f.region_id = r.region_id
        WHERE d.year = 2023
        GROUP BY r.region_name, d.month, d.month_name
        ORDER BY r.region_name, d.month
    """, conn())
    # Add seasonal index per region
    for region in df9["region_name"].unique():
        mask = df9["region_name"] == region
        mean = df9.loc[mask, "revenue"].mean()
        df9.loc[mask, "seasonal_index"] = (df9.loc[mask, "revenue"] / mean * 100).round(2)
    df9["trend"] = df9["seasonal_index"].apply(
        lambda x: "Peak" if x >= 120 else ("Trough" if x <= 80 else "Normal"))
    df9.to_csv(f"{OUT_DIR}/09_statistical_analysis.csv", index=False)
    print(f"✓ 09_statistical_analysis.csv  ({len(df9):,} rows)")

    print(f"\n✅ All 9 Tableau source files saved to: {OUT_DIR}/")

if __name__ == "__main__":
    export_all()
