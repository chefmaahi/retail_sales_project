# Real-Time Sales Performance Analytics Dashboard
### Complete Tableau Build Guide

**Author:** Mahadev Kishan Gurram  
**Published on Tableau Public:** [Real-Time Sales Performance Analytics Dashboard](https://public.tableau.com/app/profile/mahadev.kishan.gurram/viz/Realtimesalesperformanceanalyticsdashboardforretailbusiness/Real-TimeSalesPerformanceAnalyticsDashboard?publish=yes)  
**Tableau Version:** 2026.2  
**Platform:** Tableau Desktop (Mac) → Published to Tableau Public  
**Dashboard Size:** 1366 × 4068 px (Range / Responsive)  
**Global Font:** Times New Roman | Background Color: `#ffffff` (white)

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Data Sources](#2-data-sources)
3. [Calculated Fields](#3-calculated-fields)
4. [Worksheets — Configuration Reference](#4-worksheets--configuration-reference)
5. [Dashboard Assembly — Top to Bottom](#5-dashboard-assembly--top-to-bottom)
6. [Filters Applied](#6-filters-applied)
7. [Interactivity & Actions](#7-interactivity--actions)
8. [Publishing to Tableau Public](#8-publishing-to-tableau-public)

---

## 1. Project Overview

This dashboard delivers a comprehensive real-time view of retail sales performance across six analytical dimensions:

- **KPI Summary Row** — Revenue, Profit, Units Sold, AOV, Conversion Rate, Profit Margin
- **Revenue & Profit Trends** — Monthly line charts with dual-axis analysis
- **Product Category Analysis** — Revenue and conversion breakdowns
- **Customer Demographics** — Age group and gender-based spend analysis
- **Regional Performance** — Revenue by region and region-category matrix
- **Forecasting & Seasonality** — Predictive revenue line and seasonal heatmaps

---

## 2. Data Sources

The workbook is powered by **9 CSV flat files** connected as separate data sources. All connections use UTF-8 encoding with comma separator and locale `en_IN` (Indian Rupee `₹`).

| # | Data Source Name | Key Fields |
|---|---|---|
| 01 | `01_sales_transactions.csv` | `transaction_id`, `customer_id`, `date`, `product_category`, `quantity`, `price_per_unit`, `total_amount`, `profit`, `profit_margin_pct`, `region`, `gender`, `age`, `age_group`, `month`, `month_name`, `quarter`, `week`, `year`, `day_name`, `is_weekend` |
| 02 | `02_monthly_kpis.csv` | `year_month`, `total_revenue`, `total_orders`, `total_quantity`, `avg_order_value`, `unique_customers`, `profit_margin_pct` |
| 03 | `03_category_performance.csv` | `year_month`, `category`, `revenue`, `orders`, `avg_price` |
| 04 | `04_customer_demographics.csv` | `customer_id`, `gender`, `age`, `age_group`, `total_orders`, `total_spent`, `avg_order_value`, `last_purchase_date` |
| 05 | `05_forecasts.csv` | `year_month`, `date`, `model`, `predicted_revenue`, `lower_ci`, `upper_ci`, `slope`, `intercept` |
| 06 | `06_seasonality_heatmap.csv` | `year`, `month`, `month_name`, `category`, `revenue`, `orders` |
| 07 | `07_region_performance.csv` | `year_month`, `region_name`, `revenue`, `orders`, `profit`, `avg_order_value` |
| 08 | `08_region_category.csv` | `region_name`, `category`, `revenue`, `orders`, `profit`, `avg_order_value` |
| 09 | `09_statistical_analysis.csv` | `month`, `month_name`, `region_name`, `revenue`, `orders`, `avg_order_value`, `seasonal_index`, `trend` |

> **Tip:** Each data source has a Hyper extract embedded in the `.twbx`. When refreshing locally, re-point file paths under **Data > Edit Data Source**.

---

## 3. Calculated Fields

### Data Source: `01_sales_transactions`  *(Primary — used in most sheets)*

| Field Name | Formula | Description |
|---|---|---|
| **KPI - Total Revenue** | `SUM([total_amount])` | Aggregate revenue across all transactions |
| **KPI - Total Profit** | `SUM([profit])` | Aggregate profit value |
| **KPI - Profit Margin %** | `SUM([profit]) / SUM([total_amount]) * 100` | Profit as percentage of revenue |
| **KPI - Avg Order Value** | `SUM([total_amount]) / COUNT([transaction_id])` | Mean spend per transaction |
| **KPI - Total Customers** | `COUNTD([customer_id])` | Distinct customers count |
| **KPI - Units Sold** | `SUM([quantity])` | Total units sold |
| **KPI - Conversion Rate %** | `COUNTD([customer_id]) / TOTAL(COUNTD([customer_id])) * 100` | Table-calc: each segment's share of all customers |

### Data Source: `03_category_performance`

| Field Name | Formula | Description |
|---|---|---|
| **KPI - Conversion Rate %** | `SUM([orders]) / TOTAL(SUM([orders])) * 100` | Category's share of total orders (table calc across rows) |

### Data Source: `04_customer_demographics`

| Field Name | Formula | Description |
|---|---|---|
| **Age Group Conversion** | `SUM([total_orders]) / TOTAL(SUM([total_orders])) * 100` | Age group's share of all orders (table calc across rows) |

> **Note on Table Calculations:** Fields using `TOTAL()` are table-scoped. Ensure the **Compute Using** setting is set to **Table (Across)** or **Specific Dimensions** as appropriate for each sheet.

---

## 4. Worksheets — Configuration Reference

### Sheet 1 — `TOTAL REVENUE` *(KPI Card)*
| Property | Value |
|---|---|
| **Data Source** | `01_sales_transactions` |
| **Mark Type** | Automatic (Text) |
| **Measure on Text** | `KPI - Total Revenue` (formatted as ₹) |
| **Purpose** | Big-number KPI tile |
| **Filters** | Date (Year, Quarter, Month), Region, Product Category, Age Group, Gender, Month Name |

### Sheet 2 — `TOTAL PROFIT` *(KPI Card)*
| Property | Value |
|---|---|
| **Data Source** | `01_sales_transactions` |
| **Mark Type** | Automatic (Text) |
| **Measure on Text** | `KPI - Total Profit` |
| **Filters** | Same as TOTAL REVENUE |

### Sheet 3 — `TOTAL UNITS SOLD` *(KPI Card)*
| Property | Value |
|---|---|
| **Data Source** | `01_sales_transactions` |
| **Mark Type** | Automatic (Text) |
| **Measure on Text** | `KPI - Units Sold` |
| **Filters** | Same as TOTAL REVENUE |

### Sheet 4 — `AVG ORDER VALUE` *(KPI Card)*
| Property | Value |
|---|---|
| **Data Source** | `02_monthly_kpis` / `01_sales_transactions` |
| **Mark Type** | Automatic (Text) |
| **Measure on Text** | `KPI - Avg Order Value` |
| **Filters** | Action filter on Year Month |

### Sheet 5 — `CONVERSION RATE` *(KPI Card)*
| Property | Value |
|---|---|
| **Data Source** | `03_category_performance` |
| **Mark Type** | Automatic (Text) |
| **Measure on Text** | `KPI - Conversion Rate %` |
| **Filters** | Action (Category), Action (Year Month) |

### Sheet 6 — `PROFIT MARGIN` *(KPI Card)*
| Property | Value |
|---|---|
| **Data Source** | `01_sales_transactions` |
| **Mark Type** | Automatic (Text) |
| **Measure on Text** | `KPI - Profit Margin %` |
| **Filters** | Same as TOTAL REVENUE |

---

### Sheet 7 — `Revenue Trend Line`
| Property | Value |
|---|---|
| **Data Source** | `01_sales_transactions` |
| **Columns** | `Date` (truncated to Month) |
| **Rows** | `SUM(total_amount)` |
| **Mark Type** | Line (auto) |
| **Color / Detail** | Optional: Product Category for multi-line |
| **Filters** | Date (Year/Quarter/Month), Region, Product Category, Age Group, Gender, Month Name — plus Action filters |

### Sheet 8 — `TOTAL REVENUE & PROFIT ANALYSIS`
| Property | Value |
|---|---|
| **Data Source** | `01_sales_transactions` |
| **Columns** | `Date` (truncated to Month) |
| **Rows** | `KPI - Total Revenue` + `KPI - Total Profit` (dual axis or combined expression) |
| **Mark Type** | Line (auto) |
| **Filters** | Same as Revenue Trend Line |

### Sheet 9 — `Revenue by Product Category`
| Property | Value |
|---|---|
| **Data Source** | `01_sales_transactions` |
| **Columns** | `SUM(total_amount)` |
| **Rows** | `Product Category` |
| **Mark Type** | Bar (horizontal) |
| **Color** | Product Category |
| **Filters** | Date (Year/Quarter/Month), Region, Age Group, Gender, Month Name — plus Action filters |

### Sheet 10 — `Conversion Rate by Category`
| Property | Value |
|---|---|
| **Data Source** | `03_category_performance` |
| **Columns** | `KPI - Conversion Rate %` |
| **Rows** | `Category` |
| **Mark Type** | Bar |
| **Compute Using** | Category (table across rows) |
| **Filters** | Action (Category), Action (Year Month), Category |

### Sheet 11 — `Profit Margin by Category`
| Property | Value |
|---|---|
| **Data Source** | `01_sales_transactions` |
| **Columns** | `KPI - Profit Margin %` |
| **Rows** | `Product Category` |
| **Mark Type** | Bar |
| **Filters** | Date, Region, Product Category |

### Sheet 12 — `Heatmap` *(Seasonality by Category)*
| Property | Value |
|---|---|
| **Data Source** | `06_seasonality_heatmap` |
| **Columns** | `Month Name` |
| **Rows** | `Category` |
| **Mark Type** | Square |
| **Color** | `SUM(Revenue)` — sequential color palette |
| **Filters** | Action (Category) |

### Sheet 13 — `Forecast Line`
| Property | Value |
|---|---|
| **Data Source** | `05_forecasts` |
| **Columns** | `Year Month` |
| **Rows** | `SUM(Predicted Revenue)` |
| **Mark Type** | Line |
| **Detail / Color** | `Model` (to show multiple forecast models) |
| **Filters** | Date (Year/Quarter/Month), Model |
| **Note** | Use `Lower CI` and `Upper CI` as reference band for confidence interval shading |

### Sheet 14 — `Age Group Bar`
| Property | Value |
|---|---|
| **Data Source** | `04_customer_demographics` |
| **Columns** | `Age Group` |
| **Rows** | `SUM(Total Spent)` |
| **Mark Type** | Bar |
| **Filters** | Region, Action (Age Group), Action (Gender) |

### Sheet 15 — `Conversion Rate by Age Group`
| Property | Value |
|---|---|
| **Data Source** | `04_customer_demographics` |
| **Columns** | `Age Group Conversion` |
| **Rows** | `Age Group` |
| **Mark Type** | Bar |
| **Compute Using** | Age Group (table across rows) |
| **Filters** | Region, Action (Age Group, Gender) |

### Sheet 16 — `Amount Spent by Gender`
| Property | Value |
|---|---|
| **Data Source** | `04_customer_demographics` |
| **Mark Type** | Pie |
| **Angle / Size** | `SUM(Total Spent)` |
| **Color** | `Gender` |
| **Filters** | Region, Action (Age Group), Action (Age Group, Gender) |

### Sheet 17 — `Revenue by Region`
| Property | Value |
|---|---|
| **Data Source** | `07_region_performance` |
| **Columns** | `SUM(Revenue)` |
| **Rows** | `Region Name` |
| **Mark Type** | Bar |
| **Filters** | Action-driven from Region selector |

### Sheet 18 — `Region by Category`
| Property | Value |
|---|---|
| **Data Source** | `08_region_category` |
| **Columns** | `Category` |
| **Rows** | `Region Name` |
| **Mark Type** | Square (cross-tab heatmap) |
| **Color** | `SUM(Revenue)` |

### Sheet 19 — `Seasonality by Region`
| Property | Value |
|---|---|
| **Data Source** | `09_statistical_analysis` |
| **Columns** | `Month Name` |
| **Rows** | `Region Name` |
| **Mark Type** | Square |
| **Color** | `SUM(Revenue)` or `Seasonal Index` |
| **Filters** | Trend (to filter by growth/decline regions) |

---

## 5. Dashboard Assembly — Top to Bottom

The dashboard is a single scrollable vertical canvas at **1366 px wide × 4068 px tall** using **Range** sizing mode. Below is the layout from top to bottom based on Y-coordinates extracted from the workbook.

---

### Row 1 — Header / Title Banner  
*(Y ≈ 0)*  
- Full-width text object: **"Real-Time Sales Performance Analytics Dashboard"**
- Background: dark color (e.g., `#1a1a2e` or matching brand color)
- White text, bold, centered
- Fixed height: ~80 px

---

### Row 2 — Global Filter Bar  
*(Y ≈ 1000–2300)*  
Horizontal strip of filter controls exposed on the dashboard:
- **Date Range** — Year / Quarter / Month filter (from `01_sales_transactions`)
- **Region** — Dropdown or multi-select
- **Product Category** — Multi-select
- **Gender** — Radio or dropdown
- **Age Group** — Multi-select

> Add each via **Dashboard > Filters** from any sheet that carries the filter. Use **Apply to Worksheets > All Using This Data Source** for global coverage.

---

### Row 3 — KPI Cards Strip  
*(Y ≈ 23,356)*  
Six equally-spaced KPI cards in one horizontal row:

| Position | Sheet | Metric |
|---|---|---|
| 1st (leftmost) | `TOTAL REVENUE` | ₹ Total Revenue |
| 2nd | `TOTAL PROFIT` | ₹ Total Profit |
| 3rd | `PROFIT MARGIN` | Profit Margin % |
| 4th | `AVG ORDER VALUE` | Avg Order Value ₹ |
| 5th | `CONVERSION RATE` | Conversion Rate % |
| 6th (rightmost) | `TOTAL UNITS SOLD` | Total Units Sold |

Each card: ~14,641 px wide (workbook units), fixed height ~2,884 px.  
Style: no border, white background, bold large number, subtitle label below.

---

### Row 4 — Demographics: Age Group & Gender  
*(Y ≈ 4,498–20,385)*  

| Left Panel (60%) | Right Panel (40%) |
|---|---|
| `Age Group Bar` — horizontal bar: Total Spent by Age Group | `Amount Spent by Gender` — Pie chart: share of spend by gender |
| `Conversion Rate by Age Group` — horizontal bar below | (gender pie stacked below age bar) |

---

### Row 5 — Revenue by Product Category  
*(Y ≈ 29,585)*  
Full-width horizontal bar chart (`Revenue by Product Category`) showing revenue for each product category.  
Width: ~84,187 units. Legend floats to the right.

---

### Row 6 — Conversion Rate by Category  
*(Y ≈ 36,332)*  
Full-width bar chart (`Conversion Rate by Category`) — shows each category's percentage share of total orders.  
Width: ~84,187 units. Small legend/label floats right.

---

### Row 7 — Seasonality Heatmap (Category × Month)  
*(Y ≈ 43,253)*  
Full-width square-mark heatmap (`Heatmap`):  
- Rows: Product Category  
- Columns: Month Name (Jan–Dec)  
- Color: Revenue intensity (sequential palette, e.g. Blue → Orange)  
Width: ~95,168 units.

---

### Row 8 — Revenue Trend Line  
*(Y ≈ 51,182)*  
Full-width line chart (`Revenue Trend Line`):  
- X-axis: Date (by Month)  
- Y-axis: SUM(Total Amount)  
- Shows monthly revenue trend over time  
Width: ~95,168 units.

---

### Row 9 — Total Revenue & Profit Analysis  
*(Y ≈ 59,573)*  
Full-width dual line/area chart (`TOTAL REVENUE & PROFIT ANALYSIS`):  
- X-axis: Date (by Month)  
- Y-axis: Revenue + Profit overlaid  
- Dual measure comparison  
Width: ~95,168 units. Small legend floats upper right.

---

### Row 10 — Forecast Line  
*(Y ≈ 67,907)*  
Full-width line chart (`Forecast Line`):  
- X-axis: Year Month  
- Y-axis: Predicted Revenue  
- Color: Model (to distinguish forecast models)  
- Confidence interval reference band using Lower CI / Upper CI  
Width: ~95,168 units.

---

### Row 11 — Revenue by Region  
*(Y ≈ 76,932)*  
Horizontal bar chart (`Revenue by Region`):  
- Columns: SUM(Revenue)  
- Rows: Region Name  
Width: ~76,867 units. Legend floats to the right (~10,249 units wide).

---

### Row 12 — Region by Category Matrix  
*(Y ≈ 84,631)*  
Cross-tab heatmap (`Region by Category`):  
- Rows: Region Name  
- Columns: Category  
- Color: Revenue (sequential)  
Width: ~84,187 units.

---

### Row 13 — Seasonality by Region  
*(Y ≈ 92,013)*  
Full-width square-mark heatmap (`Seasonality by Region`):  
- Rows: Region Name  
- Columns: Month Name  
- Color: Revenue / Seasonal Index  
Width: ~95,168 units.

---

## 6. Filters Applied

### Global Dashboard Filters (Exposed as Controls)

| Filter Field | Data Source | Applied To |
|---|---|---|
| Date — Year (`yr:date`) | `01_sales_transactions` | All main KPI and trend sheets |
| Date — Quarter (`qr:date`) | `01_sales_transactions` | All main KPI and trend sheets |
| Date — Month (`mn:date`) | `01_sales_transactions` | All main KPI and trend sheets |
| Region | `01_sales_transactions` | Revenue Trend, KPI cards, Demographics |
| Product Category | `01_sales_transactions` | Revenue Trend, KPI cards, Profit Margin |
| Gender | `01_sales_transactions` | KPI cards, Demographics |
| Age Group | `01_sales_transactions` | KPI cards, Demographics |
| Month Name | `01_sales_transactions` | Revenue Trend, KPI cards |
| Model | `05_forecasts` | Forecast Line |
| Trend | `09_statistical_analysis` | Seasonality by Region |

### Sheet-Level Action Filters (Cross-Sheet Interactivity)

| Source Sheet | Triggers Filter On | Target Sheets |
|---|---|---|
| `Age Group Bar` | Age Group, Gender | `Amount Spent by Gender`, `Conversion Rate by Age Group`, KPI cards |
| `Amount Spent by Gender` | Gender, Age Group | `Age Group Bar`, `Conversion Rate by Age Group` |
| `Conversion Rate by Category` | Category, Year Month | `CONVERSION RATE`, `TOTAL REVENUE`, `Heatmap` |
| `Revenue by Product Category` | Product Category | `TOTAL REVENUE`, Profit Margin, Trend sheets |
| `Revenue by Region` | Region | Demographics, KPI cards |

> **How to set up Action Filters in Tableau:**  
> Dashboard menu → Actions → Add Action → Filter  
> Set Source Sheet, Target Sheets, and which fields to filter on.  
> Use **Select** as the run action trigger and **Show all values** on deselect.

---

## 7. Interactivity & Actions

| Action Type | Trigger | Behavior |
|---|---|---|
| Filter Action | Click Age Group bar | Filters gender pie, conversion rate, and KPI cards |
| Filter Action | Click Gender slice (pie) | Filters age group and conversion rate charts |
| Filter Action | Click Category bar | Filters conversion rate, heatmap, and KPI tiles |
| Filter Action | Click Region bar | Filters demographics and regional cross-tab |
| Highlight Action | Hover on any mark | Highlights corresponding marks across linked sheets |
| URL Action *(optional)* | Click KPI tile | Can link to detailed report tab or external URL |

---

## 8. Publishing to Tableau Public

1. **Clean up** — Remove any unused sheets. Hide all individual worksheets (right-click tab → Hide).
2. **File > Save to Tableau Public As...** — Sign in with your Tableau Public account.
3. Name it: `Real time sales performance analytics dashboard for retail business`
4. Under **Workbook Details**, add a description, tags (e.g. `retail`, `sales`, `dashboard`, `kpi`).
5. Set visibility to **Public**.
6. After publish, the URL will be:  
   `https://public.tableau.com/app/profile/mahadev.kishan.gurram/viz/Realtimesalesperformanceanalyticsdashboardforretailbusiness/Real-TimeSalesPerformanceAnalyticsDashboard`

> **Tip:** Embed the published dashboard in a portfolio site using the Tableau Public embed code (Share → Embed Code).

---

## Quick Rebuild Checklist

- [ ] Connect all 9 CSV files as separate data sources
- [ ] Set locale to `en_IN` and currency to `₹` for all sources
- [ ] Create all 10 calculated fields listed in Section 3
- [ ] Build 19 worksheets per Section 4 configuration
- [ ] Assemble dashboard — 1366 px wide, Range sizing
- [ ] Add 6 KPI cards in horizontal strip (Row 3)
- [ ] Add all global filters (Section 6) and expose on dashboard
- [ ] Configure all cross-sheet action filters (Section 7)
- [ ] Apply consistent font (Times New Roman) and background (#ffffff)
- [ ] Publish to Tableau Public and verify the live link

---

*Guide generated from workbook analysis of `Real time sales performance analytics dashboard for retail business.twbx` — Tableau 2026.2 build 20262.26.0603.1643*

