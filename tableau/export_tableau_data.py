"""
Tableau Data Prep — Export optimized CSVs for Tableau dashboards.
Each CSV corresponds to one Tableau data source / worksheet.
"""

import sqlite3
import pandas as pd
import os
import json

DB_PATH  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "db", "retail_sales.db")
OUT_DIR  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "tableau")
PROC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "processed")


def conn():
    return sqlite3.connect(DB_PATH)


def export_all():
    os.makedirs(OUT_DIR, exist_ok=True)
    exports = {}

    # ── 1. Main Fact Table (flattened) ────────────────────────────────────────
    df = pd.read_sql("""
        SELECT
            f.transaction_id,
            f.date_key                          AS date,
            d.year, d.quarter, d.month, d.month_name,
            d.week, d.day_name, d.is_weekend,
            f.customer_id,
            c.gender, c.age, c.age_group,
            p.category                          AS product_category,
            f.quantity,
            f.price_per_unit,
            f.total_amount,
            ROUND(f.total_amount * 0.30, 2)     AS profit,
            30.0                                AS profit_margin_pct
        FROM fact_sales f
        JOIN dim_date     d ON f.date_key    = d.date_key
        JOIN dim_customers c ON f.customer_id = c.customer_id
        JOIN dim_products  p ON f.product_id  = p.product_id
        ORDER BY f.date_key
    """, conn())
    path = os.path.join(OUT_DIR, "01_sales_transactions.csv")
    df.to_csv(path, index=False)
    exports["sales_transactions"] = path
    print(f"✓ Exported 01_sales_transactions.csv   ({len(df):,} rows)")

    # ── 2. Monthly KPI Trend ──────────────────────────────────────────────────
    df2 = pd.read_sql("""
        SELECT year_month, total_revenue, total_orders, avg_order_value, unique_customers, total_quantity
        FROM agg_monthly_kpis ORDER BY year_month
    """, conn())
    df2["profit"] = df2["total_revenue"] * 0.30
    df2["profit_margin_pct"] = 30.0
    path2 = os.path.join(OUT_DIR, "02_monthly_kpis.csv")
    df2.to_csv(path2, index=False)
    exports["monthly_kpis"] = path2
    print(f"✓ Exported 02_monthly_kpis.csv          ({len(df2):,} rows)")

    # ── 3. Category Performance ───────────────────────────────────────────────
    df3 = pd.read_sql("""
        SELECT year_month, category, revenue, orders, avg_price
        FROM agg_category_performance ORDER BY year_month, category
    """, conn())
    path3 = os.path.join(OUT_DIR, "03_category_performance.csv")
    df3.to_csv(path3, index=False)
    exports["category_performance"] = path3
    print(f"✓ Exported 03_category_performance.csv  ({len(df3):,} rows)")

    # ── 4. Customer Demographics ──────────────────────────────────────────────
    df4 = pd.read_sql("""
        SELECT
            c.customer_id, c.gender, c.age, c.age_group,
            COUNT(f.transaction_id)  AS total_orders,
            SUM(f.total_amount)      AS total_spent,
            AVG(f.total_amount)      AS avg_order_value,
            MAX(f.date_key)          AS last_purchase_date
        FROM dim_customers c
        JOIN fact_sales f ON c.customer_id = f.customer_id
        GROUP BY c.customer_id
    """, conn())
    path4 = os.path.join(OUT_DIR, "04_customer_demographics.csv")
    df4.to_csv(path4, index=False)
    exports["customer_demographics"] = path4
    print(f"✓ Exported 04_customer_demographics.csv ({len(df4):,} rows)")

    # ── 5. Forecast Data ──────────────────────────────────────────────────────
    forecast_src = os.path.join(PROC_DIR, "forecasts.csv")
    if os.path.exists(forecast_src):
        df5 = pd.read_csv(forecast_src)
        path5 = os.path.join(OUT_DIR, "05_forecasts.csv")
        df5.to_csv(path5, index=False)
        exports["forecasts"] = path5
        print(f"✓ Exported 05_forecasts.csv             ({len(df5):,} rows)")

    # ── 6. Seasonality Heatmap Data ───────────────────────────────────────────
    df6 = pd.read_sql("""
        SELECT
            d.year, d.month, d.month_name,
            p.category,
            SUM(f.total_amount) AS revenue,
            COUNT(*)            AS orders
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        JOIN dim_products p ON f.product_id = p.product_id
        GROUP BY d.year, d.month, d.month_name, p.category
        ORDER BY d.year, d.month
    """, conn())
    path6 = os.path.join(OUT_DIR, "06_seasonality_heatmap.csv")
    df6.to_csv(path6, index=False)
    exports["seasonality"] = path6
    print(f"✓ Exported 06_seasonality_heatmap.csv   ({len(df6):,} rows)")

    print(f"\n✅ All Tableau source files saved to: {OUT_DIR}/")
    return exports


if __name__ == "__main__":
    export_all()
