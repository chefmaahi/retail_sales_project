"""
Analytics Module — Retail Sales KPIs with Region + Statistical Analysis
"""

import sqlite3
import pandas as pd
import numpy as np
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "data", "db", "retail_sales.db")

def get_conn():
    return sqlite3.connect(DB_PATH)

# ── KPI 1: Revenue Summary ────────────────────────────────────────
def kpi_revenue_summary():
    conn = get_conn()
    row = conn.execute("""
        SELECT SUM(total_amount), COUNT(*), AVG(total_amount),
               COUNT(DISTINCT customer_id), SUM(quantity), SUM(profit)
        FROM fact_sales
    """).fetchone()
    conn.close()
    keys = ["total_revenue","total_orders","avg_order_value",
            "unique_customers","total_units_sold","estimated_profit"]
    return dict(zip(keys, row))

# ── KPI 2: Monthly Revenue ────────────────────────────────────────
def kpi_monthly_revenue():
    conn = get_conn()
    df = pd.read_sql("""
        SELECT year_month, total_revenue, total_orders, avg_order_value,
               unique_customers, total_profit,
               LAG(total_revenue) OVER (ORDER BY year_month) AS prev_revenue,
               ROUND((total_revenue - LAG(total_revenue) OVER (ORDER BY year_month))
                     / LAG(total_revenue) OVER (ORDER BY year_month) * 100, 2) AS mom_growth_pct
        FROM agg_monthly_kpis ORDER BY year_month
    """, conn)
    conn.close()
    return df

# ── KPI 3: Category Revenue ───────────────────────────────────────
def kpi_category_revenue():
    conn = get_conn()
    df = pd.read_sql("""
        SELECT p.category, SUM(f.total_amount) AS revenue,
               COUNT(*) AS orders, AVG(f.price_per_unit) AS avg_price,
               ROUND(SUM(f.total_amount)*100.0/(SELECT SUM(total_amount) FROM fact_sales),2) AS revenue_share_pct
        FROM fact_sales f JOIN dim_products p ON f.product_id=p.product_id
        GROUP BY p.category ORDER BY revenue DESC
    """, conn)
    conn.close()
    return df

# ── KPI 4: Region Revenue (NEW) ───────────────────────────────────
def kpi_region_revenue():
    conn = get_conn()
    df = pd.read_sql("""
        SELECT r.region_name,
               SUM(f.total_amount)  AS revenue,
               COUNT(*)             AS orders,
               SUM(f.profit)        AS profit,
               AVG(f.total_amount)  AS avg_order_value,
               COUNT(DISTINCT f.customer_id) AS unique_customers,
               ROUND(SUM(f.total_amount)*100.0/(SELECT SUM(total_amount) FROM fact_sales),2) AS revenue_share_pct
        FROM fact_sales f
        JOIN dim_region r ON f.region_id = r.region_id
        GROUP BY r.region_name ORDER BY revenue DESC
    """, conn)
    conn.close()
    return df

# ── KPI 5: Region × Category (NEW) ───────────────────────────────
def kpi_region_category():
    conn = get_conn()
    df = pd.read_sql("""
        SELECT r.region_name, p.category,
               SUM(f.total_amount) AS revenue,
               COUNT(*)            AS orders,
               AVG(f.total_amount) AS avg_order_value
        FROM fact_sales f
        JOIN dim_region   r ON f.region_id  = r.region_id
        JOIN dim_products p ON f.product_id = p.product_id
        GROUP BY r.region_name, p.category
        ORDER BY r.region_name, revenue DESC
    """, conn)
    conn.close()
    return df

# ── KPI 6: Region × Month (NEW) ──────────────────────────────────
def kpi_region_monthly():
    conn = get_conn()
    df = pd.read_sql("""
        SELECT r.region_name, d.year, d.month, d.month_name,
               SUM(f.total_amount) AS revenue,
               COUNT(*)            AS orders
        FROM fact_sales f
        JOIN dim_region r ON f.region_id = r.region_id
        JOIN dim_date   d ON f.date_key  = d.date_key
        GROUP BY r.region_name, d.year, d.month, d.month_name
        ORDER BY r.region_name, d.year, d.month
    """, conn)
    conn.close()
    return df

# ── KPI 7: Gender Revenue ─────────────────────────────────────────
def kpi_gender_revenue():
    conn = get_conn()
    df = pd.read_sql("""
        SELECT c.gender, SUM(f.total_amount) AS revenue,
               COUNT(*) AS orders, AVG(c.age) AS avg_age
        FROM fact_sales f JOIN dim_customers c ON f.customer_id=c.customer_id
        GROUP BY c.gender
    """, conn)
    conn.close()
    return df

# ── KPI 8: Age Group Revenue ──────────────────────────────────────
def kpi_age_group_revenue():
    conn = get_conn()
    df = pd.read_sql("""
        SELECT c.age_group, SUM(f.total_amount) AS revenue,
               COUNT(*) AS orders, AVG(f.total_amount) AS avg_order_value
        FROM fact_sales f JOIN dim_customers c ON f.customer_id=c.customer_id
        GROUP BY c.age_group ORDER BY c.age_group
    """, conn)
    conn.close()
    return df

# ── KPI 9: Seasonality ────────────────────────────────────────────
def kpi_seasonality():
    conn = get_conn()
    df = pd.read_sql("""
        SELECT d.month_name, d.month, SUM(f.total_amount) AS revenue, COUNT(*) AS orders
        FROM fact_sales f JOIN dim_date d ON f.date_key=d.date_key
        GROUP BY d.month, d.month_name ORDER BY d.month
    """, conn)
    conn.close()
    return df

# ── KPI 10: Repeat Buyers ─────────────────────────────────────────
def kpi_repeat_buyers():
    conn = get_conn()
    total    = conn.execute("SELECT COUNT(DISTINCT customer_id) FROM fact_sales").fetchone()[0]
    repeat   = conn.execute("""
        SELECT COUNT(*) FROM (
            SELECT customer_id FROM fact_sales GROUP BY customer_id HAVING COUNT(*)>1)
    """).fetchone()[0]
    conn.close()
    return {"total_customers": total, "repeat_buyers": repeat,
            "repeat_rate_pct": round(repeat/total*100,2),
            "one_time_buyers": total - repeat}

# ════════════════════════════════════════════════════════════════
# STATISTICAL ANALYSIS MODULE
# ════════════════════════════════════════════════════════════════

def statistical_trend_analysis():
    """Linear trend, growth rate, volatility per region and overall."""
    conn = get_conn()
    df = pd.read_sql("""
        SELECT d.year, d.month, r.region_name, SUM(f.total_amount) AS revenue
        FROM fact_sales f
        JOIN dim_date   d ON f.date_key  = d.date_key
        JOIN dim_region r ON f.region_id = r.region_id
        WHERE d.year = 2023
        GROUP BY d.year, d.month, r.region_name
        ORDER BY d.month
    """, conn)
    conn.close()

    results = {}
    # Overall
    overall = df.groupby("month")["revenue"].sum().values
    x = np.arange(len(overall))
    b = np.cov(x, overall, ddof=1)[0,1] / np.var(x, ddof=1)
    a = np.mean(overall) - b * np.mean(x)
    results["Overall"] = {
        "slope":   round(b, 2),
        "trend":   "Upward" if b > 0 else "Downward",
        "mean":    round(np.mean(overall), 2),
        "std":     round(np.std(overall), 2),
        "cv_pct":  round(np.std(overall)/np.mean(overall)*100, 2),
        "peak_month":   int(np.argmax(overall) + 1),
        "trough_month": int(np.argmin(overall) + 1),
    }
    # Per region
    for region in df["region_name"].unique():
        rdf = df[df["region_name"] == region].sort_values("month")
        y   = rdf["revenue"].values
        xr  = np.arange(len(y))
        br  = np.cov(xr, y, ddof=1)[0,1] / np.var(xr, ddof=1) if len(y) > 1 else 0
        ar  = np.mean(y) - br * np.mean(xr)
        results[region] = {
            "slope":   round(br, 2),
            "trend":   "Upward" if br > 0 else "Downward",
            "mean":    round(np.mean(y), 2),
            "std":     round(np.std(y), 2),
            "cv_pct":  round(np.std(y)/np.mean(y)*100, 2) if np.mean(y) > 0 else 0,
            "peak_month":   int(rdf["month"].iloc[np.argmax(y)]),
            "trough_month": int(rdf["month"].iloc[np.argmin(y)]),
        }
    return results

def statistical_seasonality():
    """Seasonal index per month: month_avg / overall_avg * 100."""
    conn = get_conn()
    df = pd.read_sql("""
        SELECT d.month, d.month_name, SUM(f.total_amount) AS revenue
        FROM fact_sales f JOIN dim_date d ON f.date_key=d.date_key
        WHERE d.year=2023
        GROUP BY d.month, d.month_name ORDER BY d.month
    """, conn)
    conn.close()
    overall_avg = df["revenue"].mean()
    df["seasonal_index"] = (df["revenue"] / overall_avg * 100).round(2)
    df["classification"] = df["seasonal_index"].apply(
        lambda x: "Peak" if x >= 120 else ("Trough" if x <= 80 else "Normal"))
    return df

def statistical_region_comparison():
    """Statistical comparison across regions."""
    conn = get_conn()
    df = pd.read_sql("""
        SELECT r.region_name, d.month, SUM(f.total_amount) AS revenue
        FROM fact_sales f
        JOIN dim_region r ON f.region_id = r.region_id
        JOIN dim_date   d ON f.date_key  = d.date_key
        WHERE d.year = 2023
        GROUP BY r.region_name, d.month
        ORDER BY r.region_name, d.month
    """, conn)
    conn.close()
    stats = []
    for region in df["region_name"].unique():
        rdf = df[df["region_name"] == region]
        rev = rdf["revenue"].values
        stats.append({
            "region":       region,
            "total_revenue":round(rev.sum(), 2),
            "mean_monthly": round(rev.mean(), 2),
            "std":          round(rev.std(), 2),
            "min_revenue":  round(rev.min(), 2),
            "max_revenue":  round(rev.max(), 2),
            "cv_pct":       round(rev.std()/rev.mean()*100, 2),
            "growth_slope": round(np.polyfit(np.arange(len(rev)), rev, 1)[0], 2),
        })
    return pd.DataFrame(stats).sort_values("total_revenue", ascending=False)

def print_all_kpis():
    print("\n" + "="*60)
    print("  RETAIL SALES KPI REPORT (with Region)")
    print("="*60)

    print("\n📊 REVENUE SUMMARY")
    for k,v in kpi_revenue_summary().items():
        print(f"   {k:<25} {v:,.2f}" if isinstance(v,float) else f"   {k:<25} {v:,}")

    print("\n🗺️  REGION REVENUE")
    print(kpi_region_revenue().to_string(index=False))

    print("\n🗺️  REGION × CATEGORY")
    print(kpi_region_category().to_string(index=False))

    print("\n🛍️  CATEGORY REVENUE")
    print(kpi_category_revenue().to_string(index=False))

    print("\n📈 STATISTICAL TREND ANALYSIS")
    for region, stats in statistical_trend_analysis().items():
        print(f"\n  {region}:")
        for k,v in stats.items():
            print(f"    {k:<20} {v}")

    print("\n📅 SEASONALITY INDEX")
    print(statistical_seasonality().to_string(index=False))

    print("\n📊 REGION STATISTICAL COMPARISON")
    print(statistical_region_comparison().to_string(index=False))

if __name__ == "__main__":
    print_all_kpis()
