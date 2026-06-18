-- ============================================================
-- Retail Sales Relational Database Schema (with Region)
-- ============================================================

-- Dimension: Region
CREATE TABLE IF NOT EXISTS dim_region (
    region_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    region_name TEXT NOT NULL UNIQUE,
    state       TEXT,
    country     TEXT DEFAULT 'India'
);

-- Dimension: Customers
CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id TEXT PRIMARY KEY,
    gender      TEXT CHECK(gender IN ('Male', 'Female', 'Other')),
    age         INTEGER CHECK(age BETWEEN 0 AND 120),
    age_group   TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension: Products / Categories
CREATE TABLE IF NOT EXISTS dim_products (
    product_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    category        TEXT NOT NULL,
    price_per_unit  REAL NOT NULL CHECK(price_per_unit > 0),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension: Date
CREATE TABLE IF NOT EXISTS dim_date (
    date_key    TEXT PRIMARY KEY,
    year        INTEGER,
    quarter     INTEGER,
    month       INTEGER,
    month_name  TEXT,
    week        INTEGER,
    day_of_week INTEGER,
    day_name    TEXT,
    is_weekend  INTEGER
);

-- Fact: Sales Transactions
CREATE TABLE IF NOT EXISTS fact_sales (
    transaction_id  INTEGER PRIMARY KEY,
    date_key        TEXT REFERENCES dim_date(date_key),
    customer_id     TEXT REFERENCES dim_customers(customer_id),
    product_id      INTEGER REFERENCES dim_products(product_id),
    region_id       INTEGER REFERENCES dim_region(region_id),
    quantity        INTEGER NOT NULL CHECK(quantity > 0),
    price_per_unit  REAL NOT NULL,
    total_amount    REAL NOT NULL,
    profit          REAL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Aggregation: Monthly KPIs
CREATE TABLE IF NOT EXISTS agg_monthly_kpis (
    year_month       TEXT PRIMARY KEY,
    total_revenue    REAL,
    total_orders     INTEGER,
    avg_order_value  REAL,
    unique_customers INTEGER,
    total_quantity   INTEGER,
    total_profit     REAL
);

-- Aggregation: Category Performance
CREATE TABLE IF NOT EXISTS agg_category_performance (
    year_month TEXT,
    category   TEXT,
    revenue    REAL,
    orders     INTEGER,
    avg_price  REAL,
    PRIMARY KEY (year_month, category)
);

-- Aggregation: Region Performance (NEW)
CREATE TABLE IF NOT EXISTS agg_region_performance (
    year_month  TEXT,
    region_name TEXT,
    revenue     REAL,
    orders      INTEGER,
    profit      REAL,
    avg_order_value REAL,
    PRIMARY KEY (year_month, region_name)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_fact_date     ON fact_sales(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_customer ON fact_sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_fact_product  ON fact_sales(product_id);
CREATE INDEX IF NOT EXISTS idx_fact_region   ON fact_sales(region_id);
CREATE INDEX IF NOT EXISTS idx_dim_date_year ON dim_date(year, month);
CREATE INDEX IF NOT EXISTS idx_dim_prod_cat  ON dim_products(category);
