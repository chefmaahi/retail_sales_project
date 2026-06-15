"""
Forecasting Module — Retail Sales
Implements: Linear Regression, Moving Average, Seasonal Decomposition
Outputs predictions for next 6 months.
"""

import sqlite3
import pandas as pd
import numpy as np
import os
import json
import warnings
warnings.filterwarnings("ignore")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "data", "db", "retail_sales.db")
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "data", "processed")


# ── Load monthly time-series ───────────────────────────────────────────────────
def load_monthly_ts() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        "SELECT year_month, total_revenue, total_orders FROM agg_monthly_kpis ORDER BY year_month",
        conn
    )
    conn.close()
    # Drop partial last month (2024-01 has only 2 transactions)
    df = df[df["year_month"] < "2024-01"].copy()
    df["date"] = pd.to_datetime(df["year_month"] + "-01")
    df = df.set_index("date").sort_index()
    return df


# ── 1. Moving Average Forecast ────────────────────────────────────────────────
def moving_average_forecast(df: pd.DataFrame, window: int = 3, horizon: int = 6) -> pd.DataFrame:
    """Simple N-month rolling average forecast."""
    last_values = df["total_revenue"].values[-window:]
    forecasts   = []
    values      = list(df["total_revenue"].values)

    for i in range(horizon):
        pred = np.mean(values[-window:])
        forecasts.append(pred)
        values.append(pred)

    last_date = df.index[-1]
    future_dates = pd.date_range(
        start=last_date + pd.DateOffset(months=1), periods=horizon, freq="MS"
    )
    return pd.DataFrame({
        "date":              future_dates,
        "year_month":        future_dates.strftime("%Y-%m"),
        "predicted_revenue": forecasts,
        "model":             "Moving Average (3M)",
    })


# ── 2. Linear Regression Forecast ─────────────────────────────────────────────
def linear_regression_forecast(df: pd.DataFrame, horizon: int = 6) -> pd.DataFrame:
    """OLS linear trend fitted to historical monthly revenue."""
    y = df["total_revenue"].values
    x = np.arange(len(y))

    # OLS: y = a + b*x
    b = (np.cov(x, y, ddof=1)[0, 1]) / np.var(x, ddof=1)
    a = np.mean(y) - b * np.mean(x)

    future_x    = np.arange(len(y), len(y) + horizon)
    predictions = a + b * future_x

    last_date = df.index[-1]
    future_dates = pd.date_range(
        start=last_date + pd.DateOffset(months=1), periods=horizon, freq="MS"
    )
    return pd.DataFrame({
        "date":              future_dates,
        "year_month":        future_dates.strftime("%Y-%m"),
        "predicted_revenue": predictions,
        "model":             "Linear Regression",
        "slope":             b,
        "intercept":         a,
    })


# ── 3. Seasonal Naive Forecast ─────────────────────────────────────────────────
def seasonal_naive_forecast(df: pd.DataFrame, horizon: int = 6) -> pd.DataFrame:
    """Use same month from last year as forecast (seasonal naive)."""
    df_reset = df.reset_index()
    df_reset["month"] = df_reset["date"].dt.month

    forecasts    = []
    future_dates = []
    last_date    = df.index[-1]

    for i in range(1, horizon + 1):
        future_date = last_date + pd.DateOffset(months=i)
        target_month = future_date.month
        # Find same month in history
        same_month_vals = df_reset[df_reset["month"] == target_month]["total_revenue"].values
        pred = same_month_vals[-1] if len(same_month_vals) else df["total_revenue"].mean()
        forecasts.append(pred)
        future_dates.append(future_date)

    return pd.DataFrame({
        "date":              future_dates,
        "year_month":        [d.strftime("%Y-%m") for d in future_dates],
        "predicted_revenue": forecasts,
        "model":             "Seasonal Naive",
    })


# ── 4. Ensemble (average of all models) ───────────────────────────────────────
def ensemble_forecast(df: pd.DataFrame, horizon: int = 6) -> pd.DataFrame:
    ma  = moving_average_forecast(df, horizon=horizon)
    lr  = linear_regression_forecast(df, horizon=horizon)
    sn  = seasonal_naive_forecast(df, horizon=horizon)

    ensemble = ma[["date","year_month"]].copy()
    ensemble["predicted_revenue"] = (
        ma["predicted_revenue"].values +
        lr["predicted_revenue"].values +
        sn["predicted_revenue"].values
    ) / 3
    ensemble["model"] = "Ensemble"
    ensemble["lower_ci"] = ensemble["predicted_revenue"] * 0.90   # ±10% CI
    ensemble["upper_ci"] = ensemble["predicted_revenue"] * 1.10
    return ensemble


# ── 5. Trend & Seasonality Analysis ───────────────────────────────────────────
def trend_analysis(df: pd.DataFrame) -> dict:
    y = df["total_revenue"].values
    x = np.arange(len(y))

    b = (np.cov(x, y, ddof=1)[0, 1]) / np.var(x, ddof=1)
    a = np.mean(y) - b * np.mean(x)
    yhat = a + b * x
    residuals = y - yhat

    # Coefficient of variation
    cv = np.std(y) / np.mean(y) * 100

    # Peak / trough months
    monthly = df.copy()
    monthly["month"] = monthly.index.month
    month_avg = monthly.groupby("month")["total_revenue"].mean()

    return {
        "trend_slope_per_month": round(b, 2),
        "trend_direction":       "Upward" if b > 0 else "Downward",
        "mean_revenue":          round(np.mean(y), 2),
        "std_revenue":           round(np.std(y), 2),
        "coefficient_of_variation_pct": round(cv, 2),
        "peak_month":            int(month_avg.idxmax()),
        "trough_month":          int(month_avg.idxmin()),
        "peak_revenue":          round(float(month_avg.max()), 2),
        "trough_revenue":        round(float(month_avg.min()), 2),
    }


# ── Main ───────────────────────────────────────────────────────────────────────
def run_forecasting():
    print("\n" + "=" * 60)
    print("  SALES FORECASTING REPORT")
    print("=" * 60)

    df = load_monthly_ts()
    print(f"\nHistorical data: {df.index[0].strftime('%Y-%m')} → {df.index[-1].strftime('%Y-%m')}")
    print(f"Months available: {len(df)}")

    # Trend
    trend = trend_analysis(df)
    print("\n📈 TREND ANALYSIS")
    for k, v in trend.items():
        print(f"   {k:<40} {v}")

    # Forecasts
    ma_fc  = moving_average_forecast(df)
    lr_fc  = linear_regression_forecast(df)
    sn_fc  = seasonal_naive_forecast(df)
    ens_fc = ensemble_forecast(df)

    print("\n🔮 6-MONTH FORECAST (Ensemble)")
    print(ens_fc[["year_month","predicted_revenue","lower_ci","upper_ci"]].to_string(index=False))

    # Save forecasts
    all_forecasts = pd.concat([ma_fc, lr_fc, sn_fc, ens_fc], ignore_index=True)
    out_path = os.path.join(OUT_DIR, "forecasts.csv")
    all_forecasts.to_csv(out_path, index=False)
    print(f"\n✓ Forecasts saved → {out_path}")

    # Save trend as JSON
    trend_path = os.path.join(OUT_DIR, "trend_analysis.json")
    with open(trend_path, "w") as f:
        json.dump(trend, f, indent=2)
    print(f"✓ Trend analysis saved → {trend_path}")

    return df, ens_fc, trend


if __name__ == "__main__":
    run_forecasting()
