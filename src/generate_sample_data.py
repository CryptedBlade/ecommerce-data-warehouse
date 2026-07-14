"""
generate_sample_data.py
Generates realistic sample Olist-like e-commerce data for local testing.
Run this if you don't have the Kaggle dataset downloaded.
No external dependencies beyond pandas and numpy.
"""

import pandas as pd
import numpy as np
import random
import uuid
import os
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Config ───────────────────────────────────────────────────────────────────
N_CUSTOMERS   = 5_000
N_SELLERS     = 500
N_PRODUCTS    = 1_000
N_ORDERS      = 10_000
N_ORDER_ITEMS = 13_000

STATES = ['SP','RJ','MG','RS','PR','SC','BA','GO','ES','PE',
          'CE','PA','MT','MS','RN','PB','AL','MA','SE','PI',
          'TO','RO','AM','AC','AP','RR']

CITIES = ['Sao Paulo','Rio de Janeiro','Belo Horizonte','Brasilia','Salvador',
          'Fortaleza','Curitiba','Manaus','Recife','Porto Alegre','Belem',
          'Goiania','Guarulhos','Campinas','Maceio','Natal','Teresina',
          'Campo Grande','Joao Pessoa','Aracaju','Cuiaba','Macapa',
          'Porto Velho','Boa Vista','Palmas']

CATEGORIES = [
    'bed_bath_table','health_beauty','sports_leisure','computers_accessories',
    'furniture_decor','housewares','watches_gifts','telephony','toys',
    'garden_tools','auto','electronics','books_general_interest','cool_stuff',
    'perfumery','fashion_bags_accessories','stationery','small_appliances',
    'food_drink','construction_tools_safety'
]

PAYMENT_TYPES  = ['credit_card','boleto','voucher','debit_card']
ORDER_STATUSES = ['delivered','shipped','canceled','processing','invoiced']
STATUS_WEIGHTS = [0.78, 0.09, 0.05, 0.04, 0.04]

def uid():
    return str(uuid.uuid4())

def random_date(start='2016-09-01', end='2018-10-01'):
    s = datetime.strptime(start, '%Y-%m-%d')
    e = datetime.strptime(end,   '%Y-%m-%d')
    return s + timedelta(seconds=random.randint(0, int((e - s).total_seconds())))

# ── Customers ────────────────────────────────────────────────────────────────
print("Generating customers...")
customers = pd.DataFrame({
    'customer_id':               [uid() for _ in range(N_CUSTOMERS)],
    'customer_unique_id':        [uid() for _ in range(N_CUSTOMERS)],
    'customer_zip_code_prefix':  [str(random.randint(10000, 99999)) for _ in range(N_CUSTOMERS)],
    'customer_city':             [random.choice(CITIES)  for _ in range(N_CUSTOMERS)],
    'customer_state':            [random.choice(STATES)  for _ in range(N_CUSTOMERS)],
})
customers.to_csv(f'{OUTPUT_DIR}/olist_customers_dataset.csv', index=False)

# ── Sellers ──────────────────────────────────────────────────────────────────
print("Generating sellers...")
sellers = pd.DataFrame({
    'seller_id':                 [uid() for _ in range(N_SELLERS)],
    'seller_zip_code_prefix':    [str(random.randint(10000, 99999)) for _ in range(N_SELLERS)],
    'seller_city':               [random.choice(CITIES) for _ in range(N_SELLERS)],
    'seller_state':              [random.choice(STATES) for _ in range(N_SELLERS)],
})
sellers.to_csv(f'{OUTPUT_DIR}/olist_sellers_dataset.csv', index=False)

# ── Products ─────────────────────────────────────────────────────────────────
print("Generating products...")
products = pd.DataFrame({
    'product_id':                 [uid() for _ in range(N_PRODUCTS)],
    'product_category_name':      [random.choice(CATEGORIES) for _ in range(N_PRODUCTS)],
    'product_name_length':        np.random.randint(10, 60, N_PRODUCTS),
    'product_description_length': np.random.randint(50, 1000, N_PRODUCTS),
    'product_photos_qty':         np.random.randint(1, 10, N_PRODUCTS),
    'product_weight_g':           np.random.randint(50, 30000, N_PRODUCTS).astype(float),
    'product_length_cm':          np.random.randint(5, 100, N_PRODUCTS).astype(float),
    'product_height_cm':          np.random.randint(2, 80, N_PRODUCTS).astype(float),
    'product_width_cm':           np.random.randint(5, 80, N_PRODUCTS).astype(float),
})
# Inject 5% missing categories
mask = np.random.random(N_PRODUCTS) < 0.05
products.loc[mask, 'product_category_name'] = np.nan
products.to_csv(f'{OUTPUT_DIR}/olist_products_dataset.csv', index=False)

# ── Orders ───────────────────────────────────────────────────────────────────
print("Generating orders...")
order_ids      = [uid() for _ in range(N_ORDERS)]
customer_ids   = customers['customer_id'].sample(N_ORDERS, replace=True).values
purchase_dates = [random_date() for _ in range(N_ORDERS)]

approved_dates  = [d + timedelta(hours=random.uniform(0.1, 24))  for d in purchase_dates]
carrier_dates   = [d + timedelta(days=random.uniform(1, 5))      for d in approved_dates]
estimated_dates = [d + timedelta(days=random.uniform(7, 25))     for d in purchase_dates]

delivered_dates = []
for est in estimated_dates:
    if random.random() < 0.20:   # 20% late
        delivered_dates.append(est + timedelta(days=random.uniform(1, 10)))
    else:
        delivered_dates.append(est - timedelta(days=random.uniform(0, 5)))

statuses = random.choices(ORDER_STATUSES, weights=STATUS_WEIGHTS, k=N_ORDERS)

delivered_final = [
    d if s == 'delivered' else None
    for d, s in zip(delivered_dates, statuses)
]

orders = pd.DataFrame({
    'order_id':                         order_ids,
    'customer_id':                      customer_ids,
    'order_status':                     statuses,
    'order_purchase_timestamp':         purchase_dates,
    'order_approved_at':                approved_dates,
    'order_delivered_carrier_date':     carrier_dates,
    'order_delivered_customer_date':    delivered_final,
    'order_estimated_delivery_date':    estimated_dates,
})
orders.to_csv(f'{OUTPUT_DIR}/olist_orders_dataset.csv', index=False)

# ── Order Items ──────────────────────────────────────────────────────────────
print("Generating order items...")
item_order_ids   = random.choices(order_ids, k=N_ORDER_ITEMS)
item_product_ids = products['product_id'].sample(N_ORDER_ITEMS, replace=True).values
item_seller_ids  = sellers['seller_id'].sample(N_ORDER_ITEMS, replace=True).values
prices           = np.round(np.random.lognormal(mean=4.0, sigma=0.9, size=N_ORDER_ITEMS), 2)
freights         = np.round(prices * np.random.uniform(0.05, 0.30, N_ORDER_ITEMS), 2)

order_items = pd.DataFrame({
    'order_id':           item_order_ids,
    'order_item_id':      range(1, N_ORDER_ITEMS + 1),
    'product_id':         item_product_ids,
    'seller_id':          item_seller_ids,
    'shipping_limit_date':[random_date() for _ in range(N_ORDER_ITEMS)],
    'price':              prices,
    'freight_value':      freights,
})
order_items.to_csv(f'{OUTPUT_DIR}/olist_order_items_dataset.csv', index=False)

# ── Payments ─────────────────────────────────────────────────────────────────
print("Generating payments...")
payments = []
for oid in order_ids:
    ptype = random.choice(PAYMENT_TYPES)
    inst  = random.randint(1, 12) if ptype == 'credit_card' else 1
    val   = round(random.uniform(20, 800), 2)
    payments.append({
        'order_id': oid, 'payment_sequential': 1,
        'payment_type': ptype, 'payment_installments': inst,
        'payment_value': val
    })
pd.DataFrame(payments).to_csv(f'{OUTPUT_DIR}/olist_order_payments_dataset.csv', index=False)

# ── Reviews ──────────────────────────────────────────────────────────────────
print("Generating reviews...")
reviews = []
for oid in order_ids:
    if random.random() < 0.70:
        score = random.choices([1,2,3,4,5], weights=[0.08,0.07,0.10,0.25,0.50])[0]
        reviews.append({
            'review_id':              uid(),
            'order_id':               oid,
            'review_score':           score,
            'review_creation_date':   random_date(),
            'review_answer_timestamp':random_date(),
        })
pd.DataFrame(reviews).to_csv(f'{OUTPUT_DIR}/olist_order_reviews_dataset.csv', index=False)

print("\nDone! Files written to data/raw/:")
for f in sorted(os.listdir(OUTPUT_DIR)):
    path = os.path.join(OUTPUT_DIR, f)
    size = os.path.getsize(path) / 1024
    print(f"  {f:50s}  {size:6.1f} KB")
