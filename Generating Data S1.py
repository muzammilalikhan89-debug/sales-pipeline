"""
STEP 1 — DATA GENERATION
========================
In a real project, this data would come from a client's ERP system, Excel exports,
or an API. Here we generate realistic messy financial transaction data to simulate that.

What this teaches:
- How to create realistic sample data
- What "raw / dirty" data looks like before cleaning
"""

import pandas as pd
import random
import csv
from datetime import datetime, timedelta

random.seed(42)

REGIONS     = ["North", "South", "East", "West", "Central"]
CATEGORIES  = ["Software", "Hardware", "Consulting", "Maintenance", "Training"]
REPS        = ["Alice Rossi", "Marco Bianchi", "Sara Conti", "Luca Ferrari",
                "giulia esposito", "MARCO BIANCHI", None, "Sara Conti"]  # duplicates + None = dirty data

def random_date(start_year=2023, end_year=2024):
    start = datetime(start_year, 1, 1)
    end   = datetime(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

rows = []
for i in range(1, 501):
    rep = random.choice(REPS)
    amount = round(random.uniform(500, 50000), 2)

    # Inject dirty data intentionally
    if random.random() < 0.03:
        amount = None          # 3% missing amounts
    if random.random() < 0.02:
        amount = -abs(amount)  # 2% negative amounts (data entry errors)

    rows.append({
        "transaction_id": f"TXN-{i:04d}",
        "date":           random_date().strftime("%Y-%m-%d") if random.random() > 0.01 else "N/A",
        "sales_rep":      rep,
        "region":         random.choice(REGIONS),
        "category":       random.choice(CATEGORIES),
        "amount_eur":     amount,
        "status":         random.choice(["Closed Won", "closed won", "Closed Lost", "Pending", None]),
        "notes":          random.choice(["", "  ", "follow up", "URGENT", None]),
    })

df = pd.DataFrame(rows)
df.to_csv("raw_sales_data.csv", index=False)
print(f"Generated {len(df)} rows of raw data.")
print(f"Sample dirty records:")
print(df[df["sales_rep"].isna() | (df["amount_eur"].isna()) | (df["date"] == "N/A")].head(5))
print(f"\nSaved to: raw_sales_data.csv")
