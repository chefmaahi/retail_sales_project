"""
Test Suite — Retail Sales Project
Tests ETL data quality, analytics correctness, and forecast sanity.
Run with:  python3 -m pytest tests/ -v
"""

import sqlite3
import pandas as pd
import numpy as np
import os
import sys
import unittest

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "db", "retail_sales.db")
RAW_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "raw", "retail_sales_dataset.csv")
PROC_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "data", "processed", "cleaned_sales.csv")


class TestETLDataQuality(unittest.TestCase):
    """Validate the cleaned and loaded data."""

    @classmethod
    def setUpClass(cls):
        cls.conn = sqlite3.connect(DB_PATH)
        cls.df_raw  = pd.read_csv(RAW_PATH)
        cls.df_proc = pd.read_csv(PROC_PATH)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_no_duplicate_transactions(self):
        """fact_sales must have no duplicate transaction_ids."""
        count = self.conn.execute(
            "SELECT COUNT(*) - COUNT(DISTINCT transaction_id) FROM fact_sales"
        ).fetchone()[0]
        self.assertEqual(count, 0, "Duplicate transaction_ids found in fact_sales")

    def test_no_null_totals(self):
        """total_amount must not be NULL in fact_sales."""
        nulls = self.conn.execute(
            "SELECT COUNT(*) FROM fact_sales WHERE total_amount IS NULL"
        ).fetchone()[0]
        self.assertEqual(nulls, 0)

    def test_positive_amounts(self):
        """All monetary values must be positive."""
        neg = self.conn.execute(
            "SELECT COUNT(*) FROM fact_sales WHERE total_amount <= 0 OR quantity <= 0"
        ).fetchone()[0]
        self.assertEqual(neg, 0)

    def test_row_count_preserved(self):
        """Processed row count should equal raw (no unexpected drops for this clean dataset)."""
        raw_count  = len(self.df_raw)
        proc_count = len(self.df_proc)
        self.assertEqual(raw_count, proc_count,
                         f"Row count mismatch: raw={raw_count}, processed={proc_count}")

    def test_date_range_valid(self):
        """All dates should be in expected range 2023-01-01 to 2024-12-31."""
        result = self.conn.execute(
            "SELECT MIN(date_key), MAX(date_key) FROM fact_sales"
        ).fetchone()
        self.assertGreaterEqual(result[0], "2023-01-01")
        self.assertLessEqual(result[1], "2024-12-31")

    def test_dim_tables_populated(self):
        """All dimension tables must have data."""
        for table in ["dim_date", "dim_customers", "dim_products"]:
            count = self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            self.assertGreater(count, 0, f"{table} is empty")

    def test_referential_integrity(self):
        """fact_sales must not have orphan foreign keys."""
        orphan_dates = self.conn.execute("""
            SELECT COUNT(*) FROM fact_sales f
            LEFT JOIN dim_date d ON f.date_key = d.date_key
            WHERE d.date_key IS NULL
        """).fetchone()[0]
        self.assertEqual(orphan_dates, 0, "Orphan date_keys in fact_sales")

        orphan_custs = self.conn.execute("""
            SELECT COUNT(*) FROM fact_sales f
            LEFT JOIN dim_customers c ON f.customer_id = c.customer_id
            WHERE c.customer_id IS NULL
        """).fetchone()[0]
        self.assertEqual(orphan_custs, 0, "Orphan customer_ids in fact_sales")

    def test_product_categories(self):
        """Only expected product categories should exist."""
        expected = {"Beauty", "Clothing", "Electronics"}
        actual = {row[0] for row in
                  self.conn.execute("SELECT DISTINCT category FROM dim_products")}
        self.assertEqual(expected, actual)

    def test_age_range(self):
        """Customer ages should be between 18 and 64."""
        result = self.conn.execute(
            "SELECT MIN(age), MAX(age) FROM dim_customers"
        ).fetchone()
        self.assertGreaterEqual(result[0], 18)
        self.assertLessEqual(result[1], 64)


class TestAnalyticsModule(unittest.TestCase):
    """Validate KPI calculations."""

    @classmethod
    def setUpClass(cls):
        cls.conn = sqlite3.connect(DB_PATH)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_total_revenue_matches_sum(self):
        """agg_monthly_kpis total revenue should sum to fact_sales total."""
        agg_total  = self.conn.execute(
            "SELECT SUM(total_revenue) FROM agg_monthly_kpis").fetchone()[0]
        fact_total = self.conn.execute(
            "SELECT SUM(total_amount) FROM fact_sales").fetchone()[0]
        self.assertAlmostEqual(agg_total, fact_total, places=2,
                               msg="Monthly KPI total revenue doesn't match fact_sales")

    def test_category_shares_sum_to_100(self):
        """Category revenue shares should sum to ~100%."""
        total = self.conn.execute("SELECT SUM(total_amount) FROM fact_sales").fetchone()[0]
        cat_sum = self.conn.execute("""
            SELECT SUM(f.total_amount) FROM fact_sales f
            JOIN dim_products p ON f.product_id = p.product_id
        """).fetchone()[0]
        self.assertAlmostEqual(total, cat_sum, places=2)

    def test_avg_order_value_in_range(self):
        """Average order value should be between 25 and 2000."""
        avg = self.conn.execute(
            "SELECT AVG(total_amount) FROM fact_sales").fetchone()[0]
        self.assertGreater(avg, 25)
        self.assertLess(avg, 2000)

    def test_12_months_in_kpis(self):
        """Should have 12 full months of 2023 + partial 2024."""
        count = self.conn.execute(
            "SELECT COUNT(*) FROM agg_monthly_kpis WHERE year_month LIKE '2023-%'"
        ).fetchone()[0]
        self.assertEqual(count, 12)


class TestForecastingModule(unittest.TestCase):
    """Validate forecast outputs."""

    FORECAST_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "processed", "forecasts.csv"
    )

    def test_forecast_file_exists(self):
        self.assertTrue(os.path.exists(self.FORECAST_PATH), "forecasts.csv not found")

    def test_forecast_positive_values(self):
        df = pd.read_csv(self.FORECAST_PATH)
        self.assertTrue((df["predicted_revenue"] > 0).all(),
                        "Forecast has non-positive revenue values")

    def test_forecast_models_present(self):
        df = pd.read_csv(self.FORECAST_PATH)
        models = set(df["model"].unique())
        expected = {"Moving Average (3M)", "Linear Regression", "Seasonal Naive", "Ensemble"}
        self.assertEqual(expected, models)

    def test_ensemble_ci_bounds(self):
        """Ensemble lower_ci must always be below upper_ci."""
        df = pd.read_csv(self.FORECAST_PATH)
        ensemble = df[df["model"] == "Ensemble"]
        self.assertTrue((ensemble["lower_ci"] < ensemble["upper_ci"]).all())


class TestTableauExports(unittest.TestCase):
    """Validate Tableau CSV exports."""

    TABLEAU_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tableau"
    )

    def test_all_csv_files_exist(self):
        expected_files = [
            "01_sales_transactions.csv",
            "02_monthly_kpis.csv",
            "03_category_performance.csv",
            "04_customer_demographics.csv",
            "05_forecasts.csv",
            "06_seasonality_heatmap.csv",
        ]
        for fname in expected_files:
            path = os.path.join(self.TABLEAU_DIR, fname)
            self.assertTrue(os.path.exists(path), f"Missing: {fname}")

    def test_transactions_csv_shape(self):
        df = pd.read_csv(os.path.join(self.TABLEAU_DIR, "01_sales_transactions.csv"))
        self.assertEqual(len(df), 1000)
        self.assertIn("total_amount", df.columns)
        self.assertIn("product_category", df.columns)


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    for cls in [TestETLDataQuality, TestAnalyticsModule,
                TestForecastingModule, TestTableauExports]:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


class TestRegionFeature(unittest.TestCase):
    """Validate region data and exports."""

    @classmethod
    def setUpClass(cls):
        cls.conn = sqlite3.connect(DB_PATH)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_three_regions_exist(self):
        regions = {r[0] for r in
                   self.conn.execute("SELECT region_name FROM dim_region")}
        self.assertEqual(regions, {"Andhra Pradesh", "Karnataka", "Goa"})

    def test_all_transactions_have_region(self):
        nulls = self.conn.execute(
            "SELECT COUNT(*) FROM fact_sales WHERE region_id IS NULL"
        ).fetchone()[0]
        self.assertEqual(nulls, 0)

    def test_region_revenue_sums_match(self):
        region_total = self.conn.execute(
            "SELECT SUM(revenue) FROM agg_region_performance").fetchone()[0]
        fact_total   = self.conn.execute(
            "SELECT SUM(total_amount) FROM fact_sales").fetchone()[0]
        self.assertAlmostEqual(region_total, fact_total, places=1)

    def test_region_csv_files_exist(self):
        TABLEAU_DIR = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tableau")
        for fname in ["07_region_performance.csv",
                      "08_region_category.csv",
                      "09_statistical_analysis.csv"]:
            self.assertTrue(os.path.exists(os.path.join(TABLEAU_DIR, fname)),
                            f"Missing: {fname}")

    def test_region_column_in_transactions_csv(self):
        TABLEAU_DIR = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tableau")
        df = pd.read_csv(os.path.join(TABLEAU_DIR, "01_sales_transactions.csv"))
        self.assertIn("region", df.columns)
        self.assertEqual(set(df["region"].unique()),
                         {"Andhra Pradesh", "Karnataka", "Goa"})

    def test_statistical_analysis_has_seasonal_index(self):
        TABLEAU_DIR = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tableau")
        df = pd.read_csv(os.path.join(TABLEAU_DIR, "09_statistical_analysis.csv"))
        self.assertIn("seasonal_index", df.columns)
        self.assertIn("trend", df.columns)
        self.assertTrue((df["seasonal_index"] > 0).all())
