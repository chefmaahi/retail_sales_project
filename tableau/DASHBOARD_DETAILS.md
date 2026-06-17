# Tableau Dashboard Documentation

## 🔗 Live Link
https://public.tableau.com/app/profile/mahadev.kishan.gurram/viz/Realtimesalesperformanceanalyticsdashboard/Dashboard1?publish=yes

## 📊 Sheets Built

| Sheet | Data Source | Chart Type | KPI Shown |
|-------|------------|------------|-----------|
| Revenue Trend | 01_sales_transactions | Line | Monthly Revenue |
| Revenue by Category | 01_sales_transactions | Bar | Revenue per Category |
| Profit Margin KPI | 01_sales_transactions | Scorecard | 30% Margin |
| Conversion Rate by Category | 03_category_performance | Bar | % share per category |
| Conversion Rate by Age Group | 04_customer_demographics | Bar | % share per age group |
| Monthly KPIs | 02_monthly_kpis | Line/Dual Axis | Revenue + Profit |
| Seasonality Heatmap | 06_seasonality_heatmap | Heatmap | Revenue by Month × Category |
| Forecast | 05_forecasts | Line | 6-month prediction |

## 📐 Calculated Fields Used

| Field Name | Formula | Purpose |
|------------|---------|---------|
| KPI - Total Revenue | `SUM([Total Amount])` | Revenue scorecard |
| KPI - Total Profit | `SUM([Profit])` | Profit scorecard |
| KPI - Profit Margin % | `SUM([Profit]) / SUM([Total Amount]) * 100` | Margin % |
| KPI - Avg Order Value | `SUM([Total Amount]) / COUNT([Transaction Id])` | AOV scorecard |
| KPI - Total Customers | `COUNTD([Customer Id])` | Customer count |
| KPI - Units Sold | `SUM([Quantity])` | Units scorecard |
| KPI - Conversion Rate % | `SUM([Orders]) / TOTAL(SUM([Orders])) * 100` | Category conversion |
| Age Group Conversion | `SUM([Total Orders]) / TOTAL(SUM([Total Orders])) * 100` | Age group conversion |
| Overall Profit Margin | `SUM([Profit]) / SUM([Total Amount]) * 100` | Margin KPI card |

## 🔑 Key KPI Values

| KPI | Value |
|-----|-------|
| Total Revenue | $456,000 |
| Total Profit | $136,800 |
| Profit Margin | 30% |
| Avg Order Value | $456 |
| Total Customers | 1,000 |
| Units Sold | 2,514 |
| Top Category | Electronics ($156,905) |
| Peak Month | May ($53,150) |
| Lowest Month | September ($23,620) |

## 🔍 Filters Applied
- Product Category
- Date (Month/Year)
- Gender
- Age Group

## ⚡ Performance Tips Applied
- Pre-aggregated CSVs used as data sources
- Fixed axis ranges to avoid auto-scaling
- Extracts recommended for large datasets