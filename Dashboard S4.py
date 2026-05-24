"""
STEP 4 — DASHBOARD (Power BI-style charts in Python)
=====================================================
In a real project you'd connect Power BI directly to the SQL Server database.
Here we generate the same charts in Python — identical concepts, same data.

What this teaches:
- Visualising KPIs clearly for client presentations
- Choosing the right chart type for each business question
- Exporting a multi-panel dashboard as a PDF-ready image
"""

import pandas as pd
import sqlite3
import os

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.gridspec import GridSpec
except ImportError as exc:
    raise ImportError(
        "matplotlib is required to run this dashboard script. "
        "Install it with `pip install matplotlib`."
    ) from exc

DB_PATH  = "sales_warehouse.db"
OUT_PATH = "sales_dashboard.png"

conn = sqlite3.connect(DB_PATH)

# ── Load KPI data ────────────────────────────────────────────────────────────
region_df = pd.read_csv("kpi_by_region.csv")
monthly   = pd.read_csv("kpi_monthly.csv")
reps      = pd.read_csv("kpi_top_reps.csv")
winrate   = pd.read_csv("kpi_win_rate.csv")
qoq       = pd.read_csv("kpi_qoq_growth.csv").dropna()

# Summary KPIs
total_rev = pd.read_sql_query(
    "SELECT ROUND(SUM(amount_eur),0) AS rev FROM fact_sales WHERE status='Closed Won'", conn
).iloc[0,0]
total_deals = pd.read_sql_query(
    "SELECT COUNT(*) AS n FROM fact_sales WHERE status='Closed Won'", conn
).iloc[0,0]
avg_deal = pd.read_sql_query(
    "SELECT ROUND(AVG(amount_eur),0) AS avg FROM fact_sales WHERE status='Closed Won'", conn
).iloc[0,0]
conn.close()

# ── COLOUR PALETTE (Deloitte-inspired) ──────────────────────────────────────
BLUE    = "#1B4F8A"
LBLUE   = "#4A8FD4"
TEAL    = "#1D9E75"
AMBER   = "#EF9F27"
CORAL   = "#D85A30"
GRAY    = "#888780"
LGRAY   = "#F1EFE8"
WHITE   = "#FFFFFF"

REGION_COLORS   = [BLUE, LBLUE, TEAL, AMBER, CORAL]
CATEGORY_COLORS = [TEAL, BLUE, AMBER, CORAL, GRAY]

# ── LAYOUT ───────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(18, 13), facecolor=WHITE)
fig.suptitle("Sales Performance Dashboard — FY2023/2024", fontsize=18,
             fontweight="bold", color=BLUE, y=0.97)

gs = GridSpec(3, 3, figure=fig, hspace=0.55, wspace=0.38,
              top=0.92, bottom=0.06, left=0.06, right=0.97)

# ── KPI CARDS (top row) ───────────────────────────────────────────────────────
def kpi_card(ax, value, label, color):
    ax.set_facecolor(LGRAY)
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.axis("off")
    ax.text(0.5, 0.65, value, ha="center", va="center",
            fontsize=22, fontweight="bold", color=color)
    ax.text(0.5, 0.25, label, ha="center", va="center",
            fontsize=11, color=GRAY)
    for spine in ax.spines.values():
        spine.set_edgecolor(color); spine.set_linewidth(2)

ax_k1 = fig.add_subplot(gs[0, 0])
ax_k2 = fig.add_subplot(gs[0, 1])
ax_k3 = fig.add_subplot(gs[0, 2])
kpi_card(ax_k1, f"€{total_rev/1e6:.2f}M",  "Total Revenue (Won)",  BLUE)
kpi_card(ax_k2, f"{int(total_deals)}",      "Deals Closed",         TEAL)
kpi_card(ax_k3, f"€{avg_deal/1e3:.1f}K",   "Avg Deal Size",        AMBER)

# ── CHART 1: Revenue by region (horizontal bar) ──────────────────────────────
ax1 = fig.add_subplot(gs[1, 0])
bars = ax1.barh(region_df["region"], region_df["total_revenue"] / 1e3,
                color=REGION_COLORS, edgecolor="none", height=0.6)
ax1.set_xlabel("Revenue (€K)", fontsize=9, color=GRAY)
ax1.set_title("Revenue by Region", fontsize=11, fontweight="bold", color=BLUE, pad=8)
ax1.tick_params(colors=GRAY, labelsize=9)
for bar, val in zip(bars, region_df["total_revenue"] / 1e3):
    ax1.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
             f"€{val:.0f}K", va="center", fontsize=8, color=GRAY)
ax1.spines[["top","right","left"]].set_visible(False)
ax1.set_facecolor(WHITE)

# ── CHART 2: Monthly revenue trend (line chart) ──────────────────────────────
ax2 = fig.add_subplot(gs[1, 1:])
m23 = monthly[monthly["year"] == 2023].sort_values("month")
m24 = monthly[monthly["year"] == 2024].sort_values("month")
months_lbl = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
ax2.plot(range(1,13), [m23[m23["month"]==i]["monthly_revenue"].values[0]/1e3
                        if i in m23["month"].values else None for i in range(1,13)],
         color=BLUE, linewidth=2.2, marker="o", markersize=5, label="2023")
ax2.plot(range(1,13), [m24[m24["month"]==i]["monthly_revenue"].values[0]/1e3
                        if i in m24["month"].values else None for i in range(1,13)],
         color=TEAL, linewidth=2.2, marker="s", markersize=5, label="2024")
ax2.set_xticks(range(1,13)); ax2.set_xticklabels(months_lbl, fontsize=8, color=GRAY)
ax2.set_ylabel("Revenue (€K)", fontsize=9, color=GRAY)
ax2.set_title("Monthly Revenue Trend — 2023 vs 2024", fontsize=11,
              fontweight="bold", color=BLUE, pad=8)
ax2.legend(fontsize=9, framealpha=0)
ax2.tick_params(colors=GRAY, labelsize=9)
ax2.spines[["top","right"]].set_visible(False)
ax2.set_facecolor(WHITE)
ax2.grid(axis="y", linestyle="--", alpha=0.3, color=GRAY)

# ── CHART 3: Win rate by category (donut-style bar) ──────────────────────────
ax3 = fig.add_subplot(gs[2, 0])
wr = winrate.sort_values("win_rate_pct")
colors_bar = [TEAL if v >= 50 else AMBER if v >= 40 else CORAL for v in wr["win_rate_pct"]]
ax3.barh(wr["category"], wr["win_rate_pct"], color=colors_bar, height=0.5, edgecolor="none")
ax3.axvline(50, color=GRAY, linestyle="--", linewidth=1, alpha=0.5)
ax3.set_xlabel("Win Rate (%)", fontsize=9, color=GRAY)
ax3.set_title("Win Rate by Category", fontsize=11, fontweight="bold", color=BLUE, pad=8)
ax3.tick_params(colors=GRAY, labelsize=9)
for i, (_, row) in enumerate(wr.iterrows()):
    ax3.text(row["win_rate_pct"] + 0.5, i, f"{row['win_rate_pct']}%", va="center", fontsize=8, color=GRAY)
ax3.spines[["top","right","left"]].set_visible(False)
ax3.set_facecolor(WHITE)

# ── CHART 4: Top reps (bar chart) ─────────────────────────────────────────────
ax4 = fig.add_subplot(gs[2, 1])
rep_colors = [BLUE if i == 0 else LBLUE for i in range(len(reps))]
ax4.bar(range(len(reps)), reps["total_revenue"] / 1e3,
        color=rep_colors, edgecolor="none", width=0.6)
ax4.set_xticks(range(len(reps)))
short_names = [n.split()[0] for n in reps["sales_rep"]]
ax4.set_xticklabels(short_names, fontsize=8, color=GRAY, rotation=20)
ax4.set_ylabel("Revenue (€K)", fontsize=9, color=GRAY)
ax4.set_title("Top Sales Reps", fontsize=11, fontweight="bold", color=BLUE, pad=8)
ax4.tick_params(colors=GRAY, labelsize=9)
ax4.spines[["top","right"]].set_visible(False)
ax4.set_facecolor(WHITE)

# ── CHART 5: QoQ growth ──────────────────────────────────────────────────────
ax5 = fig.add_subplot(gs[2, 2])
labels = [f"Q{int(r.quarter)}\n{int(r.year)}" for _, r in qoq.iterrows()]
bar_colors = [TEAL if v >= 0 else CORAL for v in qoq["qoq_growth_pct"]]
ax5.bar(range(len(qoq)), qoq["qoq_growth_pct"], color=bar_colors, edgecolor="none", width=0.6)
ax5.axhline(0, color=GRAY, linewidth=0.8)
ax5.set_xticks(range(len(qoq))); ax5.set_xticklabels(labels, fontsize=8, color=GRAY)
ax5.set_ylabel("Growth (%)", fontsize=9, color=GRAY)
ax5.set_title("Quarter-over-Quarter Growth", fontsize=11, fontweight="bold", color=BLUE, pad=8)
ax5.tick_params(colors=GRAY, labelsize=9)
ax5.spines[["top","right"]].set_visible(False)
ax5.set_facecolor(WHITE)

# ── SAVE ──────────────────────────────────────────────────────────────────────
plt.savefig(OUT_PATH, dpi=150, bbox_inches="tight", facecolor=WHITE)
print(f"Dashboard saved to: {OUT_PATH}")
try:
    os.startfile(OUT_PATH)
    print("Opened dashboard image in the default viewer.")
except OSError:
    print("Could not open the image automatically. Please open it manually.")
