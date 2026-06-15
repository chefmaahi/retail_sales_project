"""
ETL Pipeline — Retail Sales Project
Extract → Clean → Transform → Load into SQLite
"""

import sqlite3
import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH   = os.path.join(BASE_DIR, "data", "raw", "retail_sales_dataset.csv")
PROC_PATH  = os.path.join(BASE_DIR, "data", "processed", "cleaned_sales.csv")
DB_PATH    = os.path.join(BASE_DIR, "data", "db", "retail_sales.db")
SCHEMA_SQL = os.path.join(BASE_DIR, "data", "db", "schema.sql")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ── EXTRACT ───────────────────────────────────────────────────────────────────
def extract(path: str) -> pd.DataFrame:
    log.info(f"Extracting from {path}")
    df = pd.read_csv(path)
    log.info(f"  Loaded {len(df):,} rows × {len(df.columns)} columns")
    return df


# ── CLEAN ─────────────────────────────────────────────────────────────────────
def clean(df: pd.DataFrame) -> pd.DataFrame:
    log.info("Cleaning data …")
    original_len = len(df)

    # Standardise column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Parse dates
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    bad_dates = df["date"].isna().sum()
    if bad_dates:
        log.warning(f"  Dropping {bad_dates} rows with unparseable dates")
        df = df.dropna(subset=["date"])

    # Remove duplicates
    dupes = df.duplicated(subset=["transaction_id"]).sum()
    if dupes:
        log.warning(f"  Removing {dupes} duplicate transaction_ids")
        df = df.drop_duplicates(subset=["transaction_id"])

    # Remove negatives / zero values
    df = df[(df["quantity"] > 0) & (df["price_per_unit"] > 0) & (df["total_amount"] > 0)]

    # Recalculate total_amount to catch any corrupted rows
    df["total_amount_check"] = df["quantity"] * df["price_per_unit"]
    mismatch = (df["total_amount"] != df["total_amount_check"]).sum()
    if mismatch:
        log.warning(f"  Fixing {mismatch} total_amount mismatches — recalculating")
        df["total_amount"] = df["total_amount_check"]
    df.drop(columns=["total_amount_check"], inplace=True)

    # Standardise categoricals
    df["gender"]           = df["gender"].str.strip().str.title()
    df["product_category"] = df["product_category"].str.strip().str.title()
    df["customer_id"]      = df["customer_id"].str.strip().str.upper()

    log.info(f"  Clean complete: {len(df):,} rows kept (dropped {original_len - len(df)})")
    return df


# ── TRANSFORM ─────────────────────────────────────────────────────────────────
def transform(df: pd.DataFrame) -> pd.DataFrame:
    log.info("Transforming data …")

    # Derived date features
    df["year"]        = df["date"].dt.year
    df["quarter"]     = df["date"].dt.quarter
    df["month"]       = df["date"].dt.month
    df["month_name"]  = df["date"].dt.strftime("%B")
    df["week"]        = df["date"].dt.isocalendar().week.astype(int)
    df["day_of_week"] = df["date"].dt.dayofweek        # 0=Mon
    df["day_name"]    = df["date"].dt.strftime("%A")
    df["is_weekend"]  = df["day_of_week"].isin([5, 6]).astype(int)
    df["date_key"]    = df["date"].dt.strftime("%Y-%m-%d")
    df["year_month"]  = df["date"].dt.strftime("%Y-%m")

    # Age groups
    bins   = [17, 24, 34, 44, 54, 120]
    labels = ["18-24", "25-34", "35-44", "45-54", "55+"]
    df["age_group"] = pd.cut(df["age"], bins=bins, labels=labels).astype(str)

    # KPI columns
    df["profit_margin_pct"] = 30.0                      # assumed 30% margin
    df["profit"]            = df["total_amount"] * 0.30

    log.info("  Transformation complete")
    return df


# ── LOAD ──────────────────────────────────────────────────────────────────────
def load(df: pd.DataFrame, db_path: str, schema_sql: str) -> None:
    log.info(f"Loading into {db_path} …")
    conn = sqlite3.connect(db_path)
    cur  = conn.cursor()

    # Apply schema
    with open(schema_sql) as f:
        cur.executescript(f.read())

    # ── dim_date ──────────────────────────────────────────────────────────────
    date_df = df[[
        "date_key","year","quarter","month","month_name",
        "week","day_of_week","day_name","is_weekend"
    ]].drop_duplicates("date_key")
    date_df.to_sql("dim_date", conn, if_exists="replace", index=False)
    log.info(f"  dim_date:      {len(date_df):,} rows")

    # ── dim_customers ─────────────────────────────────────────────────────────
    cust_df = df[["customer_id","gender","age","age_group"]].drop_duplicates("customer_id")
    cust_df.to_sql("dim_customers", conn, if_exists="replace", index=False)
    log.info(f"  dim_customers: {len(cust_df):,} rows")

    # ── dim_products ──────────────────────────────────────────────────────────
    prod_df = df[["product_category","price_per_unit"]].drop_duplicates()
    prod_df = prod_df.rename(columns={"product_category": "category"})
    prod_df.insert(0, "product_id", range(1, len(prod_df) + 1))
    prod_df.to_sql("dim_products", conn, if_exists="replace", index=False)
    # Build product_id lookup
    prod_lookup = prod_df.set_index(["category","price_per_unit"])["product_id"].to_dict()
    df["product_id"] = df.apply(
        lambda r: prod_lookup.get((r["product_category"], r["price_per_unit"]), None), axis=1
    )
    log.info(f"  dim_products:  {len(prod_df):,} rows")

    # ── fact_sales ────────────────────────────────────────────────────────────
    fact_df = df[[
        "transaction_id","date_key","customer_id","product_id",
        "quantity","price_per_unit","total_amount"
    ]]
    fact_df.to_sql("fact_sales", conn, if_exists="replace", index=False)
    log.info(f"  fact_sales:    {len(fact_df):,} rows")

    # ── agg_monthly_kpis ──────────────────────────────────────────────────────
    monthly = df.groupby("year_month").agg(
        total_revenue    = ("total_amount",   "sum"),
        total_orders     = ("transaction_id", "count"),
        avg_order_value  = ("total_amount",   "mean"),
        unique_customers = ("customer_id",    "nunique"),
        total_quantity   = ("quantity",       "sum"),
    ).reset_index()
    monthly.to_sql("agg_monthly_kpis", conn, if_exists="replace", index=False)
    log.info(f"  agg_monthly_kpis: {len(monthly):,} rows")

    # ── agg_category_performance ──────────────────────────────────────────────
    cat_perf = df.groupby(["year_month","product_category"]).agg(
        revenue   = ("total_amount",   "sum"),
        orders    = ("transaction_id", "count"),
        avg_price = ("price_per_unit", "mean"),
    ).reset_index().rename(columns={"product_category":"category"})
    cat_perf.to_sql("agg_category_performance", conn, if_exists="replace", index=False)
    log.info(f"  agg_category_performance: {len(cat_perf):,} rows")

    conn.commit()
    conn.close()
    log.info("Load complete ✓")


# ── MAIN ──────────────────────────────────────────────────────────────────────
def run_etl():
    t0 = datetime.now()
    df = extract(RAW_PATH)
    df = clean(df)
    df = transform(df)

    os.makedirs(os.path.dirname(PROC_PATH), exist_ok=True)
    df.to_csv(PROC_PATH, index=False)
    log.info(f"Processed CSV saved → {PROC_PATH}")

    load(df, DB_PATH, SCHEMA_SQL)
    elapsed = (datetime.now() - t0).total_seconds()
    log.info(f"ETL pipeline finished in {elapsed:.2f}s ✓")
    return df


if __name__ == "__main__":
    run_etl()
