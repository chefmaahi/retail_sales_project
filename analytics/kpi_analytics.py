"""
Analytics Module — Retail Sales KPIs & Aggregations
Runs SQL queries against the SQLite warehouse and returns DataFrames.
"""

import sqlite3
import pandas as pd
import numpy as np
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "data", "db", "retail_sales.db")


def get_conn():
    return sqlite3.connect(DB_PATH)


# ── KPI 1: Revenue Summary ────────────────────────────────────────────────────
def kpi_revenue_summary() -> dict:
    """Total revenue, avg order value, total orders, total customers."""
    conn = get_conn()
    row = conn.execute("""
        SELECT
            SUM(total_amount)                    AS total_revenue,
            COUNT(*)                             AS total_orders,
            AVG(total_amount)                    AS avg_order_value,
            COUNT(DISTINCT customer_id)          AS unique_customers,
            SUM(quantity)                        AS total_units_sold,
            SUM(total_amount) * 0.30             AS estimated_profit
        FROM fact_sales
    """).fetchone()
    conn.close()
    keys = ["total_revenue","total_orders","avg_order_value",
            "unique_customers","total_units_sold","estimated_profit"]
    return dict(zip(keys, row))


# ── KPI 2: Revenue by Month ───────────────────────────────────────────────────
def kpi_monthly_revenue() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql("""
        SELECT
            year_month,
            total_revenue,
            total_orders,
            avg_order_value,
            unique_customers,
            LAG(total_revenue) OVER (ORDER BY year_month) AS prev_revenue,
            ROUND((total_revenue - LAG(total_revenue) OVER (ORDER BY year_month))
                  / LAG(total_revenue) OVER (ORDER BY year_month) * 100, 2)
                AS mom_growth_pct
        FROM agg_monthly_kpis
        ORDER BY year_month
    """, conn)
    conn.close()
    return df


# ── KPI 3: Revenue by Category ────────────────────────────────────────────────
def kpi_category_revenue() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql("""
        SELECT
            p.category,
            SUM(f.total_amount)          AS revenue,
            COUNT(*)                     AS orders,
            AVG(f.price_per_unit)        AS avg_price,
            ROUND(SUM(f.total_amount) * 100.0 /
                  (SELECT SUM(total_amount) FROM fact_sales), 2)
                AS revenue_share_pct
        FROM fact_sales f
        JOIN dim_products p ON f.product_id = p.product_id
        GROUP BY p.category
        ORDER BY revenue DESC
    """, conn)
    conn.close()
    return df


# ── KPI 4: Revenue by Gender ──────────────────────────────────────────────────
def kpi_gender_revenue() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql("""
        SELECT
            c.gender,
            SUM(f.total_amount) AS revenue,
            COUNT(*)            AS orders,
            AVG(c.age)          AS avg_age
        FROM fact_sales f
        JOIN dim_customers c ON f.customer_id = c.customer_id
        GROUP BY c.gender
    """, conn)
    conn.close()
    return df


# ── KPI 5: Revenue by Age Group ───────────────────────────────────────────────
def kpi_age_group_revenue() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql("""
        SELECT
            c.age_group,
            SUM(f.total_amount)         AS revenue,
            COUNT(*)                    AS orders,
            AVG(f.total_amount)         AS avg_order_value
        FROM fact_sales f
        JOIN dim_customers c ON f.customer_id = c.customer_id
        GROUP BY c.age_group
        ORDER BY c.age_group
    """, conn)
    conn.close()
    return df


# ── KPI 6: Seasonality — Month-over-Month ────────────────────────────────────
def kpi_seasonality() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql("""
        SELECT
            d.month_name,
            d.month,
            SUM(f.total_amount) AS revenue,
            COUNT(*)            AS orders
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        GROUP BY d.month, d.month_name
        ORDER BY d.month
    """, conn)
    conn.close()
    return df


# ── KPI 7: Weekend vs Weekday ─────────────────────────────────────────────────
def kpi_weekend_vs_weekday() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql("""
        SELECT
            CASE WHEN d.is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_type,
            SUM(f.total_amount) AS revenue,
            COUNT(*)            AS orders,
            AVG(f.total_amount) AS avg_order_value
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        GROUP BY d.is_weekend
    """, conn)
    conn.close()
    return df


# ── KPI 8: Top Products by Revenue ───────────────────────────────────────────
def kpi_top_products(n: int = 10) -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql(f"""
        SELECT
            p.category,
            p.price_per_unit,
            SUM(f.total_amount)  AS revenue,
            SUM(f.quantity)      AS units_sold,
            COUNT(*)             AS orders
        FROM fact_sales f
        JOIN dim_products p ON f.product_id = p.product_id
        GROUP BY p.category, p.price_per_unit
        ORDER BY revenue DESC
        LIMIT {n}
    """, conn)
    conn.close()
    return df


# ── KPI 9: Customer Segment Analysis ─────────────────────────────────────────
def kpi_customer_segments() -> pd.DataFrame:
    """RFM-lite: recency, frequency, monetary per customer (top 20)."""
    conn = get_conn()
    df = pd.read_sql("""
        SELECT
            f.customer_id,
            c.gender,
            c.age_group,
            COUNT(*)                        AS frequency,
            SUM(f.total_amount)             AS monetary,
            MAX(f.date_key)                 AS last_purchase,
            AVG(f.total_amount)             AS avg_order_value
        FROM fact_sales f
        JOIN dim_customers c ON f.customer_id = c.customer_id
        GROUP BY f.customer_id
        ORDER BY monetary DESC
        LIMIT 20
    """, conn)
    conn.close()
    return df


# ── KPI 10: Conversion Proxy — Repeat Buyers ──────────────────────────────────
def kpi_repeat_buyers() -> dict:
    conn = get_conn()
    total_customers = conn.execute(
        "SELECT COUNT(DISTINCT customer_id) FROM fact_sales").fetchone()[0]
    repeat_customers = conn.execute("""
        SELECT COUNT(*) FROM (
            SELECT customer_id FROM fact_sales
            GROUP BY customer_id HAVING COUNT(*) > 1
        )""").fetchone()[0]
    conn.close()
    return {
        "total_customers":   total_customers,
        "repeat_buyers":     repeat_customers,
        "repeat_rate_pct":   round(repeat_customers / total_customers * 100, 2),
        "one_time_buyers":   total_customers - repeat_customers,
    }


# ── Print all KPIs ─────────────────────────────────────────────────────────────
def print_all_kpis():
    print("\n" + "=" * 60)
    print("  RETAIL SALES KPI REPORT")
    print("=" * 60)

    summary = kpi_revenue_summary()
    print(f"\n📊 REVENUE SUMMARY")
    for k, v in summary.items():
        print(f"   {k:<25} {v:,.2f}" if isinstance(v, float) else f"   {k:<25} {v:,}")

    print(f"\n📅 MONTHLY REVENUE")
    print(kpi_monthly_revenue().to_string(index=False))

    print(f"\n🛍️  CATEGORY REVENUE")
    print(kpi_category_revenue().to_string(index=False))

    print(f"\n👥 GENDER REVENUE")
    print(kpi_gender_revenue().to_string(index=False))

    print(f"\n🔄 REPEAT BUYER ANALYSIS")
    for k, v in kpi_repeat_buyers().items():
        print(f"   {k:<25} {v}")

    print(f"\n📅 SEASONALITY (by Month)")
    print(kpi_seasonality().to_string(index=False))


if __name__ == "__main__":
    print_all_kpis()
