## 📊 Live Tableau Dashboard
🔗 [Real-time Sales Performance Analytics Dashboard](https://public.tableau.com/app/profile/mahadev.kishan.gurram/viz/Realtimesalesperformanceanalyticsdashboard/Real-TimeSalesPerformanceAnalyticsDashboard?publish=yes


# 🛒 Real-Time Sales Performance Analytics Dashboard for Retail Businesses
MCA Major Project — Chandigarh University

Student: GURRAM MAHADEV KISHAN
UID: CUOL725165
Course: 23ONMCR-753 — Major Project
Supervisor: Mr. Anurag Goel 

A complete retail sales analytics pipeline covering relational database
design, ETL processing, KPI analytics, sales forecasting, and Tableau
dashboard preparation.

---

## 📁 Project Structure

```
retail_sales_project/
├── main.py                        ← Run everything with one command
├── requirements.txt
├── data/
│   ├── raw/
│   │   └── retail_sales_dataset.csv     ← Original 1,000-row dataset
│   ├── processed/
│   │   ├── cleaned_sales.csv            ← Post-ETL cleaned data
│   │   ├── forecasts.csv                ← 6-month forecast output
│   │   └── trend_analysis.json          ← Statistical trend summary
│   └── db/
│       ├── schema.sql                   ← Relational DB schema (star schema)
│       └── retail_sales.db              ← SQLite warehouse (auto-generated)
├── etl/
│   └── etl_pipeline.py                 ← Extract → Clean → Transform → Load
├── analytics/
│   └── kpi_analytics.py                ← 10 KPI functions via SQL
├── forecasting/
│   └── forecast_models.py              ← 4 models + trend analysis
├── tableau/
│   ├── TABLEAU_GUIDE.md                ← Dashboard build guide
│   ├── export_tableau_data.py          ← CSV exporter
│   └── 01_sales_transactions.csv       ← (auto-generated)
│   └── 02_monthly_kpis.csv             ← (auto-generated)
│   └── 03_category_performance.csv     ← (auto-generated)
│   └── 04_customer_demographics.csv    ← (auto-generated)
│   └── 05_forecasts.csv                ← (auto-generated)
│   └── 06_seasonality_heatmap.csv      ← (auto-generated)
├── tests/
│   └── test_project.py                 ← 19 unit tests (ETL, KPI, Forecast, Tableau)
├── reports/
│   └── analytical_report.md            ← Full insights report
└── docs/
```

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/chefmaahi/retail-sales-analytics.git
cd retail-sales-analytics

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the entire pipeline
python3 main.py
```

That's it. The pipeline runs all 5 steps automatically.

---

## 🗃️ Database Schema (Star Schema)

```
dim_date ──────────┐
dim_customers ─────┤──► fact_sales ◄── dim_products
                   │
                   └── agg_monthly_kpis
                   └── agg_category_performance
```

| Table | Purpose |
|-------|---------|
| `fact_sales` | Core transaction fact table |
| `dim_date` | Date dimension (year, quarter, month, week, weekend flag) |
| `dim_customers` | Customer dimension (gender, age, age_group) |
| `dim_products` | Product/category dimension |
| `agg_monthly_kpis` | Pre-aggregated monthly KPIs |
| `agg_category_performance` | Pre-aggregated category × month |

---

## 📊 KPIs Tracked

- **Revenue:** Total, by category, by gender, by age group, by month
- **Profit:** Estimated at 30% margin
- **Avg Order Value:** Overall and segment-level
- **Seasonality:** Peak (May) and trough (September) identification
- **Customer Retention:** Repeat-buyer rate
- **Trend:** Linear regression slope (+$144.90/month)

---

## 🔮 Forecasting Models

| Model | Method |
|-------|--------|
| Moving Average | 3-month rolling window |
| Linear Regression | OLS trend extrapolation |
| Seasonal Naive | Same month last year |
| **Ensemble** | Average of all 3 with ±10% CI |

---

## 📈 Tableau Dashboards

See `tableau/TABLEAU_GUIDE.md` for step-by-step build instructions.

 **Real-Time Sales Performance Analytics Dashboard for Retail Businesses:**
1. **Executive KPI Overview** — Total Revenue, Total Profit, Profit Margin, AVG Order value, Conversion Rate, Total Units Sold.
2. **Revenue by Product Category** — heatmap and Horizental bar chart.
3. **Customer Insights by Gender and Age Group** — Spending Analysis by Age Group and Gender, Total Amount Spent by Gender, Conversion Rate by Age Group.
4. **Forecasting** —  predicted Revenue for next 6 months with upper CI and Lower CI.

---

## ✅ Tests

```bash
python3 -m pytest tests/ -v
# OR
python3 tests/test_project.py
```

19 tests covering: ETL data quality, referential integrity, KPI
correctness, forecast sanity, and Tableau export completeness.

---

## 📋 Dataset

| Field | Description |
|-------|-------------|
| Transaction ID | Unique transaction identifier |
| Date | Transaction date (2023-01-01 to 2024-01-01) |
| Customer ID | Unique customer identifier |
| Gender | Male / Female |
| Age | Customer age (18–64) |
| Product Category | Beauty / Clothing / Electronics |
| Quantity | Units purchased (1–4) |
| Price per Unit | Unit price ($25–$500) |
| Total Amount | quantity × price |

---

## 🔑 Key Findings

- **$456K total revenue** | **$136.8K estimated profit**
- **May** is the peak month; **September** is the trough
- Revenue grows at **+$144.90/month** on average
- Electronics leads by revenue; Clothing leads by orders
- Female customers contribute 51% of revenue
- **0% repeat purchase rate** → loyalty program opportunity

---

## 🛠️ Tech Stack

- **Python 3.12** — ETL, analytics, forecasting, testing
- **SQLite** — Lightweight warehouse (swap for PostgreSQL in production)
- **pandas / numpy** — Data processing
- **SQL** — Aggregation and KPI queries
- **Tableau** — Dashboard visualization
- **unittest** — Test framework

---

=======
# retail_sales_project
Real-Time Sales Performance Analytics Dashboard for Retail Businesses — MCA Major Project, Chandigarh University
>>>>>>> b30f81b26f0478203cafd686caf3e2727af46bb0
