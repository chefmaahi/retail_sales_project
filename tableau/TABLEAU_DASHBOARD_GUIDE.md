# Real-Time Sales Performance Analytics Dashboard
## Complete Tableau Build Guide

**Dashboard URL:** https://public.tableau.com/app/profile/mahadev.kishan.gurram/viz/Realtimesalesperformanceanalyticsdashboard/Dashboard1?publish=yes

---

## Data Sources Used

| File | Used For |
|------|---------|
| `01_sales_transactions.csv` | KPI scorecards, Revenue trend, Spending by Age/Gender |
| `02_monthly_kpis.csv` | Monthly Sales Revenue chart |
| `03_category_performance.csv` | Conversion Rate by Category, Category Analysis by Month |
| `04_customer_demographics.csv` | Conversion Rate by Age Group, Gender pie chart |
| `05_forecasts.csv` | Revenue Forecast chart |

---

## Calculated Fields

Create all these via **Analysis → Create Calculated Field**

### From `01_sales_transactions.csv`

**KPI - Total Revenue**
```
SUM([Total Amount])
```

**KPI - Total Profit**
```
SUM([Profit])
```

**KPI - Profit Margin %**
```
SUM([Profit]) / SUM([Total Amount]) * 100
```

**KPI - Avg Order Value**
```
SUM([Total Amount]) / COUNT([Transaction Id])
```

**KPI - Total Customers**
```
COUNTD([Customer Id])
```

**KPI - Units Sold**
```
SUM([Quantity])
```

**KPI - Conversion Rate**
```
COUNTD([Customer Id]) / { FIXED : COUNTD([Customer Id]) } * 100
```

### From `03_category_performance.csv`

**Category Conversion Rate**
```
SUM([Orders]) / TOTAL(SUM([Orders])) * 100
```
→ Compute Using: **Category**

### From `04_customer_demographics.csv`

**Age Group Conversion**
```
SUM([Total Orders]) / TOTAL(SUM([Total Orders])) * 100
```
→ Compute Using: **Age Group**

---

## Sheet 1 — Spending Analysis by Age Group and Gender

**Data Source:** `01_sales_transactions.csv`

1. Columns: `[Age Group]`
2. Rows: `SUM([Total Amount])`
3. Drag `[Gender]` → **Color** mark card
4. Mark type: **Bar** → change to **Stacked Bar**
5. Drag `SUM([Total Amount])` → **Label** mark card
6. Right-click label → Format → Currency → 0 decimals
7. Title: `Spending Analysis by Age Group and Gender`

---

## Sheet 2 — Total Amount Spent by Gender (Pie + Donut)

**Data Source:** `01_sales_transactions.csv`

**Left Pie — Gender split:**
1. Mark type: **Pie**
2. Drag `[Gender]` → **Color**
3. Drag `SUM([Total Amount])` → **Angle**
4. Drag `SUM([Total Amount])` → **Label**
5. Format labels as Currency

**Right Pie — Age Group split:**
1. Duplicate the sheet
2. Replace `[Gender]` with `[Age Group]` on Color
3. Place both pies side by side on dashboard

---

## Sheet 3 — Conversion Rate by Age Group

**Data Source:** `04_customer_demographics.csv`

1. Rows: `[Age Group]`
2. Columns: `[Age Group Conversion]`
3. Mark type: **Bar**
4. Right-click pill → **Edit Table Calculation** → Compute Using: **Age Group**
5. Drag `[Age Group]` → **Color**
6. Drag `[Age Group Conversion]` → **Label**
7. Right-click x-axis → **Edit Axis** → Fixed: 10 to 24
8. Title: `Conversion Rate by Age Group`

**Expected values:**
| Age Group | Conversion Rate |
|-----------|----------------|
| 45-54 | 22.5% |
| 55+ | 21.6% |
| 35-44 | 20.7% |
| 25-34 | 20.3% |
| 18-24 | 14.9% |

---

## Sheet 4 — KPI Scorecards (6 BAN cards)

**Data Source:** `01_sales_transactions.csv`

For each KPI create a separate sheet:

| Sheet Name | Field | Format |
|------------|-------|--------|
| Total Revenue | `KPI - Total Revenue` | Currency $456,000 |
| Total Profit | `KPI - Total Profit` | Currency $136,800 |
| Profit Margin | `KPI - Profit Margin %` | Number 30.0% |
| Avg Order Value | `KPI - Avg Order Value` | Currency $476.69 |
| Conversion Rate | `KPI - Conversion Rate` | Number 100 |
| Total Units Sold | `KPI - Units Sold` | Number 2,514 |

**For each sheet:**
1. Mark type → **Text**
2. Drag the KPI field → **Text** mark card
3. Click **Text** mark → increase font to **28pt Bold**
4. Double-click title → type the KPI name in CAPS
5. **Format → Shading** → Dark background to match dashboard theme

---

## Sheet 5 — Conversion Rate by Category

**Data Source:** `03_category_performance.csv`

1. Rows: `[Category]`
2. Columns: `[Category Conversion Rate]`
3. Mark type: **Bar**
4. Right-click pill → **Edit Table Calculation** → Compute Using: **Category**
5. Drag `[Category]` → **Color**
6. Drag `[Category Conversion Rate]` → **Label**
7. Right-click x-axis → Fixed: 0 to 40
8. Title: `Conversion Rate by Category`

**Expected values:**
| Category | Conversion Rate |
|----------|----------------|
| Electronics | 34.2% |
| Clothing | 35.1% |
| Beauty | 30.7% |

---

## Sheet 6 — Revenue by Product Category

**Data Source:** `01_sales_transactions.csv`

1. Rows: `[Product Category]`
2. Columns: `SUM([Total Amount])`
3. Mark type: **Bar**
4. Drag `[Product Category]` → **Color**
5. Drag `SUM([Total Amount])` → **Label** → Format as Currency
6. Right-click x-axis → Edit Axis → title `Revenue ($)` → Fixed: 0 to 200,000
7. Sort: descending by Revenue
8. Title: `Revenue by Product Category`

**Expected values:**
| Category | Revenue |
|----------|---------|
| Electronics | $156,905 |
| Clothing | $155,580 |
| Beauty | $143,515 |

---

## Sheet 7 — Total Revenue & Profit Analysis (Dual Axis)

**Data Source:** `01_sales_transactions.csv`

1. Columns: `[Date]` → right-click → **Month**
2. Rows: `KPI - Total Revenue`
3. Drag `KPI - Total Profit` → Rows (second pill)
4. Right-click right axis → **Dual Axis** → **Synchronize Axis**
5. For Revenue mark: type **Line**, color dark green
6. For Profit mark: type **Area**, color light green, opacity 60%
7. Title: `Total Revenue & Profit Analysis`

---

## Sheet 8 — Monthly Sales Revenue

**Data Source:** `01_sales_transactions.csv`

1. Columns: `[Date]` → right-click → **Month Name**
2. Rows: `SUM([Total Amount])`
3. Mark type: **Line** with **Circle** markers
4. Drag `SUM([Total Amount])` → **Label**
5. Format labels as Currency
6. Title: `Monthly Sales Revenue`

**Peak:** May $53,150 | **Trough:** September $23,620

---

## Sheet 9 — Revenue Forecast

**Data Source:** `05_forecasts.csv`

1. Columns: `[Year Month]`
2. Rows: `SUM([Predicted Revenue])`
3. Filter `[Model]` → select **Ensemble** only
4. Drag `[Model]` → **Color**
5. Add reference lines for `[Upper Ci]` and `[Lower Ci]`:
   - **Analytics pane** → drag **Reference Line** → choose Avg Upper CI / Avg Lower CI
6. Mark type: **Line**
7. Title: `Revenue Forecast`

**6-month forecast values:**
| Month | Predicted |
|-------|-----------|
| 2024-01 | $38,776 |
| 2024-02 | $41,192 |
| 2024-03 | $36,844 |
| 2024-04 | $38,268 |
| 2024-05 | $44,701 |
| 2024-06 | $39,383 |

---

## Sheet 10 — Category Analysis by Month (Heatmap)

**Data Source:** `06_seasonality_heatmap.csv`

1. Columns: `[Month Name]`
2. Rows: `[Category]`
3. Mark type: **Square**
4. Drag `SUM([Revenue])` → **Color** → Blue sequential palette
5. Drag `SUM([Revenue])` → **Label** → Format as Currency, 0 decimals
6. Order months: right-click Month Name → **Sort** → Manual → Jan to Dec
7. Title: `Category Analysis by Month`

---

## Dashboard Assembly

**Dashboard size:** Fixed 1400 × 2800px (tall scroll layout)

**Layout top to bottom:**
```
┌─────────────────────────────────────────────────┐
│     Real-Time Sales Performance Analytics       │  ← Title (red text, dark bg)
├───────────────────────┬─────────────────────────┤
│ Spending by Age/Gender│  Total Spent by Gender  │  ← Row 1
├───────────────────────┴─────────────────────────┤
│           Conversion Rate by Age Group          │  ← Row 2
├──────────┬──────────┬──────────┬────────────────┤
│ Revenue  │  Profit  │ Margin % │  AOV  │ Conv │Units│ ← Row 3: KPI Cards
├──────────┴──────────┴──────────┴────────────────┤
│           Conversion Rate by Category           │  ← Row 4
├─────────────────────────────────────────────────┤
│           Revenue by Product Category           │  ← Row 5
├─────────────────────────────────────────────────┤
│         Total Revenue & Profit Analysis         │  ← Row 6
├─────────────────────────────────────────────────┤
│              Monthly Sales Revenue              │  ← Row 7
├─────────────────────────────────────────────────┤
│                Revenue Forecast                 │  ← Row 8
├─────────────────────────────────────────────────┤
│            Category Analysis by Month           │  ← Row 9
└─────────────────────────────────────────────────┘
```

**Formatting:**
- Background: **#1a1a2e** (dark navy) for all sheets and dashboard
- Title font: **Red/Orange bold** on dark background
- All chart backgrounds: **#16213e** (slightly lighter navy)
- Border: subtle dark border on each chart container

---

## Filters Added

Right-click each filter → **Apply to Worksheets → All Using Related Data Sources**

- `[Product Category]` → Dropdown
- `[Date]` → Relative date slider
- `[Gender]` → Checkbox
- `[Age Group]` → Checkbox
