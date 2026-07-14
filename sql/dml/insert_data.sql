-- =============================================================================
-- insert_data.sql
-- Loads processed CSV files into the star schema tables via PostgreSQL COPY.
-- Run this AFTER create_tables.sql and AFTER running the Python ETL pipeline.
-- Adjust the file paths to your absolute path if needed.
-- =============================================================================

-- NOTE: The Python script load_to_postgres.py does this automatically.
-- Use these COPY commands only for manual / psql-based loading.

-- Load order matters: dimensions first, then fact (FK constraints).

\COPY dim_date       FROM 'data/processed/dim_date.csv'       CSV HEADER;
\COPY dim_customers  FROM 'data/processed/dim_customers.csv'  CSV HEADER;
\COPY dim_products   FROM 'data/processed/dim_products.csv'   CSV HEADER;
\COPY dim_sellers    FROM 'data/processed/dim_sellers.csv'    CSV HEADER;
\COPY fact_orders    FROM 'data/processed/fact_orders.csv'    CSV HEADER;

-- Verify row counts
SELECT 'dim_date'      AS tbl, COUNT(*) AS rows FROM dim_date
UNION ALL
SELECT 'dim_customers',        COUNT(*)          FROM dim_customers
UNION ALL
SELECT 'dim_products',         COUNT(*)          FROM dim_products
UNION ALL
SELECT 'dim_sellers',          COUNT(*)          FROM dim_sellers
UNION ALL
SELECT 'fact_orders',          COUNT(*)          FROM fact_orders
ORDER BY tbl;
