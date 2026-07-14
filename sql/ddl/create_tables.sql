-- =============================================================================
-- create_tables.sql
-- Star schema DDL for the e-commerce data warehouse
-- Target: PostgreSQL 14+
-- =============================================================================

-- Drop existing tables (safe re-run)
DROP TABLE IF EXISTS fact_orders    CASCADE;
DROP TABLE IF EXISTS dim_customers  CASCADE;
DROP TABLE IF EXISTS dim_products   CASCADE;
DROP TABLE IF EXISTS dim_sellers    CASCADE;
DROP TABLE IF EXISTS dim_date       CASCADE;


-- ── Dimension: Date ───────────────────────────────────────────────────────────
CREATE TABLE dim_date (
    date_key        INT          PRIMARY KEY,
    full_date       DATE         NOT NULL,
    year            SMALLINT     NOT NULL,
    quarter         SMALLINT     NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    month           SMALLINT     NOT NULL CHECK (month   BETWEEN 1 AND 12),
    week            SMALLINT     NOT NULL,
    day_of_week     SMALLINT     NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
    is_weekend      BOOLEAN      NOT NULL DEFAULT FALSE,
    month_name      VARCHAR(12),
    quarter_name    CHAR(2)
);


-- ── Dimension: Customers ──────────────────────────────────────────────────────
CREATE TABLE dim_customers (
    customer_key        SERIAL       PRIMARY KEY,
    customer_id         VARCHAR(64)  NOT NULL UNIQUE,
    customer_unique_id  VARCHAR(64),
    customer_zip_code_prefix VARCHAR(10),
    customer_city       VARCHAR(100),
    customer_state      CHAR(2)
);


-- ── Dimension: Products ───────────────────────────────────────────────────────
CREATE TABLE dim_products (
    product_key             SERIAL      PRIMARY KEY,
    product_id              VARCHAR(64) NOT NULL UNIQUE,
    product_category_name   VARCHAR(100),
    product_weight_g        NUMERIC(10,2),
    product_photos_qty      SMALLINT
);


-- ── Dimension: Sellers ────────────────────────────────────────────────────────
CREATE TABLE dim_sellers (
    seller_key          SERIAL      PRIMARY KEY,
    seller_id           VARCHAR(64) NOT NULL UNIQUE,
    seller_zip_code_prefix VARCHAR(10),
    seller_city         VARCHAR(100),
    seller_state        CHAR(2)
);


-- ── Fact: Orders ──────────────────────────────────────────────────────────────
CREATE TABLE fact_orders (
    order_item_key          SERIAL       PRIMARY KEY,
    order_id                VARCHAR(64)  NOT NULL,
    customer_key            INT          REFERENCES dim_customers(customer_key),
    product_key             INT          REFERENCES dim_products(product_key),
    seller_key              INT          REFERENCES dim_sellers(seller_key),
    date_key                INT          REFERENCES dim_date(date_key),
    revenue                 NUMERIC(10,2),
    freight_value           NUMERIC(10,2),
    profit                  NUMERIC(10,2),
    payment_value           NUMERIC(10,2),
    payment_type            VARCHAR(30),
    payment_installments    SMALLINT,
    avg_review_score        NUMERIC(3,2),
    delivery_days           SMALLINT,
    is_late                 BOOLEAN      DEFAULT FALSE,
    order_status            VARCHAR(30)
);


-- ── Performance Indexes ───────────────────────────────────────────────────────
CREATE INDEX idx_fact_date_key     ON fact_orders(date_key);
CREATE INDEX idx_fact_customer_key ON fact_orders(customer_key);
CREATE INDEX idx_fact_product_key  ON fact_orders(product_key);
CREATE INDEX idx_fact_seller_key   ON fact_orders(seller_key);
CREATE INDEX idx_fact_order_id     ON fact_orders(order_id);
CREATE INDEX idx_fact_order_status ON fact_orders(order_status);
CREATE INDEX idx_fact_is_late      ON fact_orders(is_late);
CREATE INDEX idx_dim_date_year_month ON dim_date(year, month);
CREATE INDEX idx_dim_cust_state    ON dim_customers(customer_state);
CREATE INDEX idx_dim_prod_cat      ON dim_products(product_category_name);
CREATE INDEX idx_dim_seller_state  ON dim_sellers(seller_state);

COMMENT ON TABLE fact_orders IS 'Central fact table — grain: one row per order line item';
COMMENT ON TABLE dim_date     IS 'Date dimension — one row per calendar day';
