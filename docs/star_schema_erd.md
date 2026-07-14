# Star Schema — E-Commerce Data Warehouse

```
                    ┌─────────────────────┐
                    │      dim_date        │
                    │─────────────────────│
                    │ PK date_key          │
                    │    full_date         │
                    │    year / quarter    │
                    │    month / week      │
                    │    day_of_week       │
                    │    is_weekend        │
                    └──────────┬──────────┘
                               │
┌─────────────────┐            │           ┌─────────────────────┐
│  dim_customers  │            │           │    dim_products      │
│─────────────────│            │           │─────────────────────│
│ PK customer_key │            │           │ PK product_key       │
│    customer_id  │            │           │    product_id        │
│    city / state │            │           │    category_name     │
│    zip_code     │            │           │    weight_g          │
└────────┬────────┘            │           └──────────┬──────────┘
         │                     │                      │
         │          ┌──────────┴──────────┐           │
         └──────────►                     ◄───────────┘
                    │      fact_orders     │
                    │─────────────────────│
                    │ PK order_item_key    │
                    │ FK customer_key      │
                    │ FK product_key       │
                    │ FK seller_key        │
                    │ FK date_key          │
                    │    order_id          │
                    │    revenue           │
                    │    freight_value     │
                    │    profit            │
                    │    payment_value     │
                    │    payment_type      │
                    │    review_score      │
                    │    delivery_days     │
                    │    is_late           │
                    │    order_status      │
         ┌──────────►                     │
         │          └─────────────────────┘
┌────────┴────────┐
│  dim_sellers    │
│─────────────────│
│ PK seller_key   │
│    seller_id    │
│    city / state │
│    zip_code     │
└─────────────────┘
```

## Grain
One row per **order line item** (an order with 3 items = 3 fact rows).

## Cardinalities
- fact_orders → dim_customers : N:1
- fact_orders → dim_products  : N:1
- fact_orders → dim_sellers   : N:1
- fact_orders → dim_date      : N:1

## Why Star Schema?
- Simple joins: BI tools (Power BI, Tableau) generate efficient single-hop queries
- Aggregation performance: pre-built surrogate keys + indexes enable sub-second GROUP BY
- Extensibility: add a dim_location or dim_promotion without touching the fact table
