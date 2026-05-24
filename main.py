"""
SALES DATA PIPELINE — main runner
==================================
Run this single file to execute all 4 steps in sequence.
Each step is kept in its own file for clarity and easy debugging.

Usage:
    python main.py
"""

import os
import time

def run_step(number, name, module_path):
    print(f"\n{'='*60}")
    print(f"  STEP {number}: {name}")
    print(f"{'='*60}")
    start = time.time()
    import importlib.util, sys
    base_dir = os.path.dirname(os.path.abspath(__file__))
    module_path = os.path.join(base_dir, module_path)
    spec = importlib.util.spec_from_file_location(f"step{number}", module_path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    elapsed = round(time.time() - start, 2)
    print(f"\n  ✓ Completed in {elapsed}s")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  DELOITTE SALES DATA PIPELINE")
    print("  ETL + SQL Analysis + Dashboard")
    print("="*60)

    steps = [
        (1, "Generate raw data",          "Generating Data S1.py"),
        (2, "ETL — clean & load to SQL",  "Etl_Pipwline S2.py"),
        (3, "SQL KPI analysis",           "Sql_Analysis S3.py"),
        (4, "Build dashboard",            "Dashboard S4.py"),
    ]

    total_start = time.time()
    for num, name, path in steps:
        run_step(num, name, path)

    total = round(time.time() - total_start, 2)
    print(f"\n{'='*60}")
    print(f"  ALL STEPS COMPLETE in {total}s")
    print(f"  Dashboard saved to: output/sales_dashboard.png")
    print(f"  Audit log saved to: docs/etl_audit_log.txt")
    print(f"{'='*60}\n")
