"""
etl_pipeline.py
Full ETL: load raw CSVs → clean → feature-engineer → write processed CSVs.
Run AFTER generate_sample_data.py (or after downloading the Kaggle dataset).
"""

import os
import pandas as pd
import numpy as np

RAW_DIR  = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
PROC_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
os.makedirs(PROC_DIR, exist_ok=True)


# ── 1. LOAD ──────────────────────────────────────────────────────────────────
print("Loading raw data...")

date_cols = ['order_purchase_timestamp', 'order_approved_at',
             'order_delivered_carrier_date', 'order_delivered_customer_date',
             'order_estimated_delivery_date']

orders    = pd.read_csv(f'{RAW_DIR}/olist_orders_dataset.csv',       parse_dates=date_cols)
items     = pd.read_csv(f'{RAW_DIR}/olist_order_items_dataset.csv')
customers = pd.read_csv(f'{RAW_DIR}/olist_customers_dataset.csv')
products  = pd.read_csv(f'{RAW_DIR}/olist_products_dataset.csv')
sellers   = pd.read_csv(f'{RAW_DIR}/olist_sellers_dataset.csv')
payments  = pd.read_csv(f'{RAW_DIR}/olist_order_payments_dataset.csv')
reviews   = pd.read_csv(f'{RAW_DIR}/olist_order_reviews_dataset.csv')

print(f"  orders:    {len(orders):,}")
print(f"  items:     {len(items):,}")
print(f"  customers: {len(customers):,}")
print(f"  products:  {len(products):,}")


# ── 2. CLEAN ─────────────────────────────────────────────────────────────────
print("\nCleaning data...")

# Orders: fill missing delivered date with estimated
orders['order_delivered_customer_date'] = orders['order_delivered_customer_date'].fillna(
    orders['order_estimated_delivery_date'])

# Duplicate removal
before = len(orders)
orders.drop_duplicates(subset='order_id', inplace=True)
items.drop_duplicates(inplace=True)
print(f"  Duplicate orders removed: {before - len(orders)}")

# Products: fill missing category + numeric columns
products['product_category_name'] = products['product_category_name'].fillna('unknown')
num_cols = ['product_weight_g','product_length_cm','product_height_cm','product_width_cm']
products[num_cols] = products[num_cols].fillna(products[num_cols].median())

# Prices: remove negative or zero prices
items = items[items['price'] > 0].copy()
items = items[items['freight_value'] >= 0].copy()


# ── 3. FEATURE ENGINEERING ───────────────────────────────────────────────────
print("Engineering features...")

# Revenue & profit
items['revenue'] = items['price'] + items['freight_value']
items['profit']  = (items['price'] * 0.15).round(2)   # assumed 15% margin

# Delivery metrics
orders['delivery_days'] = (
    orders['order_delivered_customer_date'] -
    orders['order_purchase_timestamp']).dt.days

orders['is_late'] = (
    orders['order_delivered_customer_date'] >
    orders['order_estimated_delivery_date']).astype(int)

# Date dimension columns
orders['year']       = orders['order_purchase_timestamp'].dt.year
orders['month']      = orders['order_purchase_timestamp'].dt.month
orders['quarter']    = orders['order_purchase_timestamp'].dt.quarter
orders['week']       = orders['order_purchase_timestamp'].dt.isocalendar().week.astype(int)
orders['day_of_week']= orders['order_purchase_timestamp'].dt.dayofweek
orders['is_weekend'] = (orders['day_of_week'] >= 5).astype(int)
orders['date_key']   = orders['order_purchase_timestamp'].dt.strftime('%Y%m%d').astype(int)


# ── 4. BUILD DIMENSION TABLES ────────────────────────────────────────────────
print("Building dimension tables...")

# dim_customers
dim_customers = customers.copy()
dim_customers.insert(0, 'customer_key', range(1, len(dim_customers) + 1))

# dim_sellers
dim_sellers = sellers.copy()
dim_sellers.insert(0, 'seller_key', range(1, len(dim_sellers) + 1))

# dim_products
dim_products = products[['product_id','product_category_name',
                          'product_weight_g','product_photos_qty']].copy()
dim_products.insert(0, 'product_key', range(1, len(dim_products) + 1))

# dim_date  (one row per calendar day in the data range)
all_dates = pd.date_range(
    start=orders['order_purchase_timestamp'].min().date(),
    end=orders['order_purchase_timestamp'].max().date(),
    freq='D'
)
dim_date = pd.DataFrame({
    'date_key':    all_dates.strftime('%Y%m%d').astype(int),
    'full_date':   all_dates.date,
    'year':        all_dates.year,
    'quarter':     all_dates.quarter,
    'month':       all_dates.month,
    'week':        all_dates.isocalendar().week.astype(int),
    'day_of_week': all_dates.dayofweek,
    'is_weekend':  (all_dates.dayofweek >= 5).astype(int),
    'month_name':  all_dates.strftime('%B'),
    'quarter_name':['Q' + str(q) for q in all_dates.quarter],
})


# ── 5. BUILD FACT TABLE ──────────────────────────────────────────────────────
print("Building fact table...")

# Average review per order
avg_reviews = (reviews.groupby('order_id')['review_score']
               .mean().round(2).reset_index()
               .rename(columns={'review_score': 'avg_review_score'}))

# Total payment per order
total_payments = (payments.groupby('order_id')
                  .agg(payment_value=('payment_value','sum'),
                       payment_type=('payment_type','first'),
                       payment_installments=('payment_installments','max'))
                  .reset_index())

# Merge items → orders → reviews → payments
fact = (items
    .merge(orders[['order_id','customer_id','order_status',
                   'delivery_days','is_late','date_key',
                   'year','month','quarter']], on='order_id', how='left')
    .merge(avg_reviews,   on='order_id', how='left')
    .merge(total_payments, on='order_id', how='left')
)

# Resolve surrogate keys
cust_map    = dim_customers.set_index('customer_id')['customer_key']
prod_map    = dim_products.set_index('product_id')['product_key']
seller_map  = dim_sellers.set_index('seller_id')['seller_key']

fact['customer_key'] = fact['customer_id'].map(cust_map)
fact['product_key']  = fact['product_id'].map(prod_map)
fact['seller_key']   = fact['seller_id'].map(seller_map)

# Final fact columns
fact_final = fact[[
    'order_id','customer_key','product_key','seller_key','date_key',
    'revenue','freight_value','profit','payment_value','payment_type',
    'payment_installments','avg_review_score','delivery_days','is_late','order_status'
]].copy()
fact_final.insert(0, 'order_item_key', range(1, len(fact_final) + 1))


# ── 6. EXPORT ────────────────────────────────────────────────────────────────
print("\nSaving processed files...")
fact_final.to_csv(   f'{PROC_DIR}/fact_orders.csv',    index=False)
dim_customers.to_csv(f'{PROC_DIR}/dim_customers.csv',  index=False)
dim_products.to_csv( f'{PROC_DIR}/dim_products.csv',   index=False)
dim_sellers.to_csv(  f'{PROC_DIR}/dim_sellers.csv',    index=False)
dim_date.to_csv(     f'{PROC_DIR}/dim_date.csv',       index=False)

print("\nProcessed files:")
for f in os.listdir(PROC_DIR):
    path = os.path.join(PROC_DIR, f)
    df_  = pd.read_csv(path)
    print(f"  {f:30s}  {len(df_):,} rows  x  {df_.shape[1]} cols")

print("\nETL pipeline complete!")
