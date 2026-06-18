# Tableau Dashboard Setup Guide
# File: tableau/TABLEAU_GUIDE.md

## Overview
Six CSV data sources are pre-exported for Tableau. Connect them and
build the four dashboards described below.

---

## Data Sources (connect in order)
| File | Use For |
|------|---------|
| `01_sales_transactions.csv` | Main transaction-level analysis |
| `02_monthly_kpis.csv` | Trend & KPI scorecards |
| `03_category_performance.csv` | Category breakdown |
| `04_customer_demographics.csv` | Customer analysis |
| `05_forecasts.csv` | Forecast chart overlay |
| `06_seasonality_heatmap.csv` | Heatmap calendar |

---

## Dashboard 1 — Executive KPI Overview
**Sheets to build:**
1. **KPI Scorecards** — 4 BANs (big numbers):
   - Total Revenue → `SUM([Total Amount])`
   - Total Orders → `COUNT([Transaction Id])`
   - Avg Order Value → `AVG([Total Amount])`
   - Est. Profit → `SUM([Profit])`

2. **Revenue Trend Line** — Line chart
   - Columns: `[Date]` (Month granularity)
   - Rows: `SUM([Total Amount])`
   - Add Reference Line: Average

3. **Revenue by Category** — Horizontal bar
   - Rows: `[Product Category]`
   - Columns: `SUM([Total Amount])`
   - Color: `[Product Category]`

**Filters to add:** Year, Quarter, Product Category
**Dashboard size:** 1200 × 800px

---

## Dashboard 2 — Sales Trends & Seasonality
**Sheets to build:**
1. **Month-over-Month Line Chart**
   - Data: `02_monthly_kpis.csv`
   - Dual axis: Revenue + Orders
   - Mark MoM growth as annotation

2. **Seasonality Heatmap** (use `06_seasonality_heatmap.csv`)
   - Columns: `[Month Name]`
   - Rows: `[Category]`
   - Color: `SUM([Revenue])` (sequential palette — blue)
   - Label: `SUM([Revenue])`

3. **Weekend vs Weekday Bar**
   - Filter: `[Is Weekend]`
   - Columns: `[Day Name]`
   - Rows: `SUM([Total Amount])`

**Filters:** Year, Category
**Layout:** Tiled, 2 cols

---

## Dashboard 3 — Customer Insights
**Sheets to build:**
1. **Gender Revenue Donut**
   - Data: `01_sales_transactions.csv`
   - Dimensions: `[Gender]`
   - Measure: `SUM([Total Amount])`
   - Mark type: Pie

2. **Age Group Revenue Bar**
   - Rows: `[Age Group]`
   - Columns: `SUM([Total Amount])`
   - Color: `[Gender]` (stacked)

3. **Customer Scatter (RFM)**
   - Data: `04_customer_demographics.csv`
   - X: `[Total Orders]`
   - Y: `[Total Spent]`
   - Size: `[Avg Order Value]`
   - Color: `[Gender]`
   - Tooltip: Customer ID, Age Group

**Filters:** Gender, Age Group, Product Category

---

## Dashboard 4 — Forecasting
**Sheets to build:**
1. **Historical + Forecast Line**
   - Data: Blend `02_monthly_kpis.csv` + `05_forecasts.csv`
   - Historic: `[Total Revenue]` — solid blue line
   - Forecast: `[Predicted Revenue]` — dashed orange line
   - CI band: `[Lower Ci]` / `[Upper Ci]` — shaded area

2. **Model Comparison Bar**
   - Data: `05_forecasts.csv`
   - Columns: `[Year Month]`
   - Rows: `[Predicted Revenue]`
   - Color: `[Model]`

3. **Trend Indicator**
   - Show slope: +$144.90/month
   - Display peak month (May) and trough (September)

---

## Applying Filters (Step-by-Step)
1. Right-click the filter pill → **Apply to Worksheets → All Using This Data Source**
2. On dashboard, drag the filter to a floating pane
3. For date filter: use **Relative Date → Last N Months** for rolling view
4. For category: use **Multiple Values (dropdown)**
5. For region: if region data is added later, use **Quick Filter → Checkbox**

---

## Performance Optimization Tips
- Use **Extracts (.hyper)** instead of live CSV connections for >100K rows
- Pre-aggregate in SQL before importing (already done — use `agg_*` tables)
- Limit mark count per view to <5,000 — use LOD expressions to aggregate
- Cache dashboards with **Tableau Server Refresh Schedules** (hourly/daily)
- Use **Context Filters** (right-click → Add to Context) on high-cardinality fields
- Avoid calculated fields with nested IFs — pre-compute in Python/SQL

---

## LOD (Level-of-Detail) Expressions Cheat Sheet
```
# Revenue share per category
{FIXED [Product Category] : SUM([Total Amount])} / {SUM([Total Amount])}

# Customer lifetime value
{FIXED [Customer Id] : SUM([Total Amount])}

# Monthly rank
RANK(SUM([Total Amount]))  -- use in Table Calc
```

---

## Publishing to Tableau Server / Tableau Public
1. Server → Publish Workbook
2. Set data source to **Extract** and schedule daily refresh
3. Set permissions: View-only for stakeholders, Edit for analysts
4. Embed URL: `https://public.tableau.com/views/<workbook-name>`
