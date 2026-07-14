"""
eda_and_visualizations.py
Exploratory Data Analysis + charts using processed data.
Saves charts to dashboard/screenshots/
Run AFTER etl_pipeline.py
"""

import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

PROC_DIR   = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'dashboard', 'screenshots')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Load data ─────────────────────────────────────────────────────────────────
print("Loading processed data...")
fact      = pd.read_csv(f'{PROC_DIR}/fact_orders.csv')
dim_date  = pd.read_csv(f'{PROC_DIR}/dim_date.csv')
dim_prod  = pd.read_csv(f'{PROC_DIR}/dim_products.csv')
dim_cust  = pd.read_csv(f'{PROC_DIR}/dim_customers.csv')

fact = fact.merge(dim_date[['date_key','year','month','quarter']], on='date_key', how='left')
fact = fact.merge(dim_prod[['product_key','product_category_name']], on='product_key', how='left')
fact = fact.merge(dim_cust[['customer_key','customer_state']], on='customer_key', how='left')

plt.style.use('seaborn-v0_8-whitegrid')
COLORS = ['#534AB7','#1D9E75','#D85A30','#3B8BD4','#EF9F27','#D4537E','#639922','#E24B4A']


# ── Chart 1: Monthly Revenue Trend ───────────────────────────────────────────
print("Chart 1: Monthly revenue trend...")
monthly = (fact.groupby(['year','month'])['revenue']
           .sum().reset_index()
           .sort_values(['year','month']))
monthly['period'] = monthly['year'].astype(str) + '-' + monthly['month'].astype(str).str.zfill(2)

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(range(len(monthly)), monthly['revenue'], color=COLORS[0], linewidth=2.5, marker='o', markersize=5)
ax.fill_between(range(len(monthly)), monthly['revenue'], alpha=0.12, color=COLORS[0])
ax.set_title('Monthly Revenue Trend', fontsize=15, fontweight='bold', pad=12)
ax.set_xlabel('Month', fontsize=11)
ax.set_ylabel('Revenue (BRL)', fontsize=11)
ax.set_xticks(range(0, len(monthly), 3))
ax.set_xticklabels(monthly['period'].iloc[::3], rotation=45, ha='right', fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'R${x/1000:.0f}K'))
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/01_monthly_revenue.png', dpi=150, bbox_inches='tight')
plt.close()

# ── Chart 2: Top 10 Categories by Revenue ────────────────────────────────────
print("Chart 2: Top categories...")
cat_rev = (fact.groupby('product_category_name')['revenue']
           .sum().nlargest(10).reset_index()
           .sort_values('revenue'))

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(cat_rev['product_category_name'], cat_rev['revenue'],
               color=COLORS[0], alpha=0.85, edgecolor='white', linewidth=0.5)
for bar in bars:
    w = bar.get_width()
    ax.text(w * 1.01, bar.get_y() + bar.get_height() / 2,
            f'R${w/1000:.0f}K', va='center', fontsize=9, color='#444')
ax.set_title('Top 10 Product Categories by Revenue', fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Total Revenue (BRL)', fontsize=11)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'R${x/1000:.0f}K'))
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/02_top_categories.png', dpi=150, bbox_inches='tight')
plt.close()

# ── Chart 3: Order Status Distribution ───────────────────────────────────────
print("Chart 3: Order status distribution...")
status_counts = fact['order_status'].value_counts()
fig, ax = plt.subplots(figsize=(7, 5))
wedges, texts, autotexts = ax.pie(
    status_counts.values, labels=status_counts.index,
    autopct='%1.1f%%', startangle=140,
    colors=COLORS[:len(status_counts)],
    pctdistance=0.82, labeldistance=1.08)
for t in autotexts:
    t.set_fontsize(9)
ax.set_title('Order Status Distribution', fontsize=14, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/03_order_status.png', dpi=150, bbox_inches='tight')
plt.close()

# ── Chart 4: Delivery Days vs Review Score ────────────────────────────────────
print("Chart 4: Delivery vs review score...")
bins   = [0, 3, 7, 14, 100]
labels = ['Express\n(≤3d)', 'Fast\n(4-7d)', 'Standard\n(8-14d)', 'Slow\n(15d+)']
fact['delivery_tier'] = pd.cut(fact['delivery_days'], bins=bins, labels=labels)
tier_review = fact.groupby('delivery_tier')['avg_review_score'].mean()

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(tier_review.index, tier_review.values,
              color=[COLORS[1],COLORS[0],COLORS[4],COLORS[7]],
              alpha=0.85, edgecolor='white', linewidth=0.5)
ax.axhline(y=4.0, color='gray', linestyle='--', linewidth=1.2, alpha=0.7, label='4.0 threshold')
for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 0.02,
            f'{h:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax.set_title('Avg Review Score by Delivery Speed', fontsize=14, fontweight='bold', pad=12)
ax.set_ylabel('Average Review Score', fontsize=11)
ax.set_ylim(0, 5.2)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/04_delivery_vs_review.png', dpi=150, bbox_inches='tight')
plt.close()

# ── Chart 5: Late Delivery Rate by State (Top 15) ────────────────────────────
print("Chart 5: Late delivery by state...")
state_late = (fact.groupby('customer_state')
              .agg(total=('is_late','count'), late=('is_late','sum'))
              .assign(late_pct=lambda x: 100 * x['late'] / x['total'])
              .nlargest(15, 'late_pct')
              .sort_values('late_pct'))

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(state_late.index, state_late['late_pct'],
               color=COLORS[7], alpha=0.85, edgecolor='white', linewidth=0.5)
for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.3, bar.get_y() + bar.get_height()/2,
            f'{w:.1f}%', va='center', fontsize=9)
ax.set_title('Late Delivery Rate by State (Top 15)', fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Late Delivery Rate (%)', fontsize=11)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/05_late_delivery_by_state.png', dpi=150, bbox_inches='tight')
plt.close()

# ── Chart 6: Payment Type GMV Share ──────────────────────────────────────────
print("Chart 6: Payment type GMV...")
pay_gmv = fact.groupby('payment_type')['payment_value'].sum().dropna()
fig, ax = plt.subplots(figsize=(7, 5))
ax.pie(pay_gmv.values, labels=pay_gmv.index, autopct='%1.1f%%',
       startangle=90, colors=COLORS[:len(pay_gmv)], pctdistance=0.80)
ax.set_title('GMV Share by Payment Type', fontsize=14, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/06_payment_type_gmv.png', dpi=150, bbox_inches='tight')
plt.close()

# ── Summary stats ─────────────────────────────────────────────────────────────
print("\n── Summary Statistics ──────────────────────────────────────────")
print(f"  Total Revenue:       R${fact['revenue'].sum():,.0f}")
print(f"  Total Orders:        {fact['order_id'].nunique():,}")
print(f"  Avg Order Value:     R${fact['payment_value'].mean():.2f}")
print(f"  Avg Review Score:    {fact['avg_review_score'].mean():.2f}")
print(f"  Late Delivery Rate:  {fact['is_late'].mean()*100:.1f}%")
print(f"  Unique Customers:    {fact['customer_key'].nunique():,}")
print(f"  Unique Products:     {fact['product_key'].nunique():,}")
print(f"\nCharts saved to: {OUTPUT_DIR}")
