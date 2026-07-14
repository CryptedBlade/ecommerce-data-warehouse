# Data Dictionary — E-Commerce Data Warehouse

## fact_orders (Grain: one row per order line item)

| Column | Type | Description |
|---|---|---|
| order_item_key | INT | Surrogate primary key |
| order_id | VARCHAR | Original order identifier |
| customer_key | INT | FK → dim_customers |
| product_key | INT | FK → dim_products |
| seller_key | INT | FK → dim_sellers |
| date_key | INT | FK → dim_date (YYYYMMDD) |
| revenue | NUMERIC | price + freight_value |
| freight_value | NUMERIC | Shipping cost charged |
| profit | NUMERIC | Estimated 15% margin on price |
| payment_value | NUMERIC | Total amount paid by customer |
| payment_type | VARCHAR | credit_card / boleto / voucher / debit_card |
| payment_installments | SMALLINT | Number of installments |
| avg_review_score | NUMERIC | 1–5 stars (avg per order) |
| delivery_days | SMALLINT | Days from purchase to delivery |
| is_late | BOOLEAN | TRUE if delivered after estimated date |
| order_status | VARCHAR | delivered / shipped / canceled / processing |

## dim_customers

| Column | Type | Description |
|---|---|---|
| customer_key | INT | Surrogate PK |
| customer_id | VARCHAR | Original customer ID |
| customer_unique_id | VARCHAR | Deduped customer identifier |
| customer_zip_code_prefix | VARCHAR | First 5 digits of zip |
| customer_city | VARCHAR | Customer city |
| customer_state | CHAR(2) | Brazilian state abbreviation |

## dim_products

| Column | Type | Description |
|---|---|---|
| product_key | INT | Surrogate PK |
| product_id | VARCHAR | Original product ID |
| product_category_name | VARCHAR | Product category (Portuguese) |
| product_weight_g | NUMERIC | Weight in grams |
| product_photos_qty | SMALLINT | Number of product photos |

## dim_sellers

| Column | Type | Description |
|---|---|---|
| seller_key | INT | Surrogate PK |
| seller_id | VARCHAR | Original seller ID |
| seller_zip_code_prefix | VARCHAR | Seller zip prefix |
| seller_city | VARCHAR | Seller city |
| seller_state | CHAR(2) | Brazilian state |

## dim_date

| Column | Type | Description |
|---|---|---|
| date_key | INT | YYYYMMDD integer PK |
| full_date | DATE | Calendar date |
| year | SMALLINT | 4-digit year |
| quarter | SMALLINT | 1–4 |
| month | SMALLINT | 1–12 |
| week | SMALLINT | ISO week number |
| day_of_week | SMALLINT | 0=Monday … 6=Sunday |
| is_weekend | BOOLEAN | TRUE for Sat/Sun |
| month_name | VARCHAR | January … December |
| quarter_name | CHAR(2) | Q1 … Q4 |
