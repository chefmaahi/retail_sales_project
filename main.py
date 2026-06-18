"""
main.py — Retail Sales Analytics Pipeline (with Region)
Run this single file to execute the entire A-to-Z project.
"""

import os, sys, logging, unittest

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("main")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

def banner(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def main():
    banner("RETAIL SALES ANALYTICS PIPELINE — START")

    # Step 1: ETL
    banner("STEP 1 — ETL: Extract, Clean, Transform, Load")
    from etl.etl_pipeline import run_etl
    df = run_etl()

    # Step 2: Analytics
    banner("STEP 2 — ANALYTICS: KPI Calculation")
    from analytics.kpi_analytics import print_all_kpis
    print_all_kpis()

    # Step 3: Forecasting
    banner("STEP 3 — FORECASTING: Sales Prediction")
    from forecasting.forecast_models import run_forecasting
    run_forecasting()

    # Step 4: Tableau Export
    banner("STEP 4 — TABLEAU: Exporting Dashboard Data")
    from tableau.export_tableau_data import export_all
    export_all()

    # Step 5: Tests
    banner("STEP 5 — TESTING: Running Quality Checks")
    from tests.test_project import (
        TestETLDataQuality, TestAnalyticsModule,
        TestForecastingModule, TestTableauExports, TestRegionFeature
    )
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    for cls in [TestETLDataQuality, TestAnalyticsModule,
                TestForecastingModule, TestTableauExports, TestRegionFeature]:
        suite.addTests(loader.loadTestsFromTestCase(cls))
    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)

    # Summary
    banner("PIPELINE COMPLETE")
    print(f"""
  ✅  ETL:        1,000 rows → SQLite warehouse (with Region)
  ✅  KPIs:       Revenue, Profit, Seasonality, Region, Customer Segments
  ✅  Forecasts:  6-month ensemble (Jan–Jun 2024)
  ✅  Tableau:    9 CSV data sources exported
  ✅  Tests:      {'PASSED' if result.wasSuccessful() else 'FAILED'} ({result.testsRun} tests)

  📁 Project Output:
     data/raw/retail_sales_dataset.csv      ← Raw data (with Region)
     data/db/retail_sales.db               ← SQLite warehouse
     data/processed/cleaned_sales.csv      ← Cleaned data
     data/processed/forecasts.csv          ← All model forecasts
     tableau/01_sales_transactions.csv     ← Main Tableau source
     tableau/07_region_performance.csv     ← Region KPIs
     tableau/08_region_category.csv        ← Region × Category
     tableau/09_statistical_analysis.csv   ← Seasonality + Trends
     reports/analytical_report.md          ← Full insights report
    """)
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(main())
