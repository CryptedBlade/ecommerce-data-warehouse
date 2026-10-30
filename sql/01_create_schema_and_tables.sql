-- Star schema for the Olist e-commerce warehouse (PostgreSQL)
-- Run inside the database ecommerce_analytics_dw

CREATE SCHEMA IF NOT EXISTS dw;

CREATE TABLE dw.dim_customers (
    customer_key             INTEGER PRIMARY KEY,
    customer_unique_id       VARCHAR(32) NOT NULL UNIQUE,
    customer_city            VARCHAR(100),
    customer_state           CHAR(2),
    customer_zip_code_prefix CHAR(5),
    latitude                 DOUBLE PRECISION,
    longitude                DOUBLE PRECISION
);

CREATE TABLE dw.dim_products (
    product_key              INTEGER PRIMARY KEY,
    product_id               VARCHAR(32) NOT NULL UNIQUE,
    product_category_name    VARCHAR(100),
    product_category_english VARCHAR(100),
    product_photos_qty       SMALLINT,
    product_weight_g         NUMERIC(10,1),
    product_length_cm        NUMERIC(8,1),
    product_height_cm        NUMERIC(8,1),
    product_width_cm         NUMERIC(8,1),
    product_category         VARCHAR(100),
    product_volume_cm3       NUMERIC(12,1)
);

CREATE TABLE dw.dim_sellers (
    seller_key               INTEGER PRIMARY KEY,
    seller_id                VARCHAR(32) NOT NULL UNIQUE,
    seller_city              VARCHAR(100),
    seller_state             CHAR(2),
    seller_zip_code_prefix   CHAR(5),
    latitude                 DOUBLE PRECISION,
    longitude                DOUBLE PRECISION
);

CREATE TABLE dw.dim_date (
    date_key                 INTEGER PRIMARY KEY,
    date                     DATE NOT NULL UNIQUE,
    year                     SMALLINT,
    quarter                  CHAR(2),
    month_number             SMALLINT,
    month_name               VARCHAR(3),
    year_month               CHAR(7),
    day_of_week_number       SMALLINT,
    day_name                 VARCHAR(3),
    is_weekend               BOOLEAN
);

CREATE TABLE dw.fact_orders (
    order_id                      VARCHAR(32) PRIMARY KEY,
    customer_key                  INTEGER NOT NULL REFERENCES dw.dim_customers (customer_key),
    date_key                      INTEGER NOT NULL REFERENCES dw.dim_date (date_key),
    order_status                  VARCHAR(20) NOT NULL,
    is_revenue_order              BOOLEAN NOT NULL,
    is_delivered                  BOOLEAN NOT NULL,
    order_purchase_timestamp      TIMESTAMP,
    order_approved_at             TIMESTAMP,
    order_delivered_carrier_date  TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP,
    delivery_days                 NUMERIC(6,1),
    delay_days                    SMALLINT,
    is_late                       BOOLEAN,
    items_count                   SMALLINT,
    order_price                   NUMERIC(10,2),
    order_freight                 NUMERIC(10,2),
    total_payment_value           NUMERIC(10,2),
    payment_methods_used          SMALLINT,
    max_installments              SMALLINT,
    main_payment_type             VARCHAR(20),
    review_score                  SMALLINT,
    has_comment                   BOOLEAN
);

CREATE TABLE dw.fact_order_items (
    order_id          VARCHAR(32) NOT NULL REFERENCES dw.fact_orders (order_id),
    order_item_id     SMALLINT NOT NULL,
    customer_key      INTEGER NOT NULL REFERENCES dw.dim_customers (customer_key),
    product_key       INTEGER NOT NULL REFERENCES dw.dim_products (product_key),
    seller_key        INTEGER NOT NULL REFERENCES dw.dim_sellers (seller_key),
    date_key          INTEGER NOT NULL REFERENCES dw.dim_date (date_key),
    order_status      VARCHAR(20) NOT NULL,
    is_revenue_order  BOOLEAN NOT NULL,
    price             NUMERIC(10,2) NOT NULL,
    freight_value     NUMERIC(10,2) NOT NULL,
    item_total        NUMERIC(10,2) NOT NULL,
    PRIMARY KEY (order_id, order_item_id)
);

-- Indexes on every foreign key and on order status
CREATE INDEX idx_fact_orders_customer ON dw.fact_orders (customer_key);
CREATE INDEX idx_fact_orders_date     ON dw.fact_orders (date_key);
CREATE INDEX idx_fact_orders_status   ON dw.fact_orders (order_status);

CREATE INDEX idx_fact_items_product   ON dw.fact_order_items (product_key);
CREATE INDEX idx_fact_items_seller    ON dw.fact_order_items (seller_key);
CREATE INDEX idx_fact_items_customer  ON dw.fact_order_items (customer_key);
CREATE INDEX idx_fact_items_date      ON dw.fact_order_items (date_key);
