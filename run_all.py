"""
run_all.py
Master runner — executes the full pipeline in order.
Usage:  python run_all.py [--skip-db]
  --skip-db  : skip PostgreSQL load step (useful if only running locally with CSV)
"""

import subprocess
import sys
import os
import time

SRC = os.path.dirname(__file__)

steps = [
    ("Step 1: Generate sample data",   f"{SRC}/src/generate_sample_data.py"),
    ("Step 2: Run ETL pipeline",        f"{SRC}/src/etl_pipeline.py"),
    ("Step 3: EDA & visualizations",    f"{SRC}/src/eda_and_visualizations.py"),
]

skip_db = '--skip-db' in sys.argv
if not skip_db:
    steps.append(("Step 4: Load to PostgreSQL", f"{SRC}/src/load_to_postgres.py"))

print("=" * 60)
print("  E-Commerce Data Warehouse — Full Pipeline Runner")
print("=" * 60)

for title, script in steps:
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")
    t0 = time.time()
    result = subprocess.run([sys.executable, script], capture_output=False)
    elapsed = time.time() - t0
    if result.returncode != 0:
        print(f"\n  ERROR in {title}. Stopping.")
        sys.exit(1)
    print(f"\n  Done in {elapsed:.1f}s")

print("\n" + "=" * 60)
print("  All steps complete!")
print("  → Processed CSVs : data/processed/")
print("  → Charts         : dashboard/screenshots/")
if not skip_db:
    print("  → PostgreSQL     : ecommerce_dw database")
print("=" * 60)
