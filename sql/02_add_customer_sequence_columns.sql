-- Customer sequence columns used for repeat-purchase and cohort retention measures.
-- Run AFTER the notebook has loaded dw.fact_orders. Re-run if the table is reloaded.

ALTER TABLE dw.fact_orders
    ADD COLUMN IF NOT EXISTS customer_order_number     SMALLINT,
    ADD COLUMN IF NOT EXISTS customer_order_count      SMALLINT,
    ADD COLUMN IF NOT EXISTS days_since_prev_order     INTEGER,
    ADD COLUMN IF NOT EXISTS cohort_month              DATE,
    ADD COLUMN IF NOT EXISTS months_since_first_order  SMALLINT,
    ADD COLUMN IF NOT EXISTS in_cohort_window          BOOLEAN;

WITH ranked AS (
    SELECT
        order_id,
        order_purchase_timestamp,
        ROW_NUMBER() OVER w                                              AS order_number,
        COUNT(*) OVER (PARTITION BY customer_key)                        AS order_count,
        order_purchase_timestamp::date
            - LAG(order_purchase_timestamp::date) OVER w                 AS days_since_prev,
        DATE_TRUNC('month',
            MIN(order_purchase_timestamp) OVER (PARTITION BY customer_key))::date AS cohort_month
    FROM dw.fact_orders
    WHERE is_revenue_order
    WINDOW w AS (PARTITION BY customer_key ORDER BY order_purchase_timestamp, order_id)
)
UPDATE dw.fact_orders f
SET customer_order_number    = r.order_number,
    customer_order_count     = r.order_count,
    days_since_prev_order    = r.days_since_prev,
    cohort_month             = r.cohort_month,
    months_since_first_order = (
        (EXTRACT(YEAR FROM r.order_purchase_timestamp) - EXTRACT(YEAR FROM r.cohort_month)) * 12
        + EXTRACT(MONTH FROM r.order_purchase_timestamp) - EXTRACT(MONTH FROM r.cohort_month)
    )::SMALLINT,
    in_cohort_window         = r.cohort_month BETWEEN DATE '2017-01-01' AND DATE '2018-02-01'
FROM ranked r
WHERE f.order_id = r.order_id;

-- Expected: 94,983 first orders, 2,887 repeat customers, median 28 days to the second order
SELECT
    COUNT(*) FILTER (WHERE customer_order_number = 1)                    AS first_orders,
    COUNT(DISTINCT customer_key) FILTER (WHERE customer_order_count > 1) AS repeat_customers,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY days_since_prev_order)
        FILTER (WHERE customer_order_number = 2)                         AS median_days_to_second
FROM dw.fact_orders;
