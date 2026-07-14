-- =============================================================================
-- advanced_queries.sql
-- 10 advanced analytical SQL queries for the e-commerce data warehouse
-- Target: PostgreSQL 14+
-- =============================================================================


-- ── Q1: Monthly Revenue Trend with Month-over-Month Growth ───────────────────
-- Business insight: Identify seasonal peaks, revenue momentum, and growth dips.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    d.year,
    d.month,
    d.month_name,
    ROUND(SUM(f.revenue), 2)                                                      AS total_revenue,
    COUNT(DISTINCT f.order_id)                                                    AS total_orders,
    ROUND(AVG(f.revenue), 2)                                                      AS avg_order_value,
    LAG(SUM(f.revenue)) OVER (ORDER BY d.year, d.month)                           AS prev_month_revenue,
    ROUND((SUM(f.revenue) - LAG(SUM(f.revenue)) OVER (ORDER BY d.year, d.month))
          / NULLIF(LAG(SUM(f.revenue)) OVER (ORDER BY d.year, d.month), 0) * 100, 2) AS mom_growth_pct
FROM fact_orders f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;


-- ── Q2: Top 10 Revenue-Generating Product Categories ────────────────────────
-- Business insight: Invest in high-revenue, high-review categories. Investigate
-- high-revenue but low-review categories for quality issues.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    p.product_category_name,
    COUNT(DISTINCT f.order_id)              AS total_orders,
    ROUND(SUM(f.revenue), 2)                AS total_revenue,
    ROUND(SUM(f.profit), 2)                 AS total_profit,
    ROUND(AVG(f.avg_review_score), 2)       AS avg_review,
    RANK() OVER (ORDER BY SUM(f.revenue) DESC) AS revenue_rank
FROM fact_orders f
JOIN dim_products p ON f.product_key = p.product_key
GROUP BY p.product_category_name
ORDER BY revenue_rank
LIMIT 10;


-- ── Q3: RFM Customer Segmentation ────────────────────────────────────────────
-- Business insight: Identify Champions, Loyal, At-Risk, and Churned customers
-- for targeted CRM and retention campaigns.
-- ─────────────────────────────────────────────────────────────────────────────
WITH rfm_base AS (
    SELECT
        c.customer_id,
        c.customer_state,
        MAX(d.full_date)                            AS last_order_date,
        COUNT(DISTINCT f.order_id)                  AS frequency,
        ROUND(SUM(f.revenue), 2)                    AS monetary,
        CURRENT_DATE - MAX(d.full_date)             AS recency_days
    FROM fact_orders f
    JOIN dim_customers c ON f.customer_key = c.customer_key
    JOIN dim_date d      ON f.date_key      = d.date_key
    GROUP BY c.customer_id, c.customer_state
),
rfm_scored AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY recency_days   ASC)  AS r_score,
        NTILE(5) OVER (ORDER BY frequency      DESC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary       DESC) AS m_score
    FROM rfm_base
)
SELECT *,
    (r_score + f_score + m_score)                    AS rfm_total,
    CASE
        WHEN r_score >= 4 AND f_score >= 4           THEN 'Champion'
        WHEN r_score >= 3 AND f_score >= 3           THEN 'Loyal'
        WHEN r_score >= 3 AND f_score < 3            THEN 'Potential Loyalist'
        WHEN r_score < 3  AND f_score >= 3           THEN 'At Risk'
        ELSE                                              'Churned'
    END AS segment
FROM rfm_scored
ORDER BY rfm_total DESC;


-- ── Q4: Late Delivery Rate by State ──────────────────────────────────────────
-- Business insight: Identify states with logistics problems and correlate
-- late delivery with lower customer satisfaction scores.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    c.customer_state,
    COUNT(*)                                                                      AS total_orders,
    SUM(CASE WHEN f.is_late THEN 1 ELSE 0 END)                                   AS late_orders,
    ROUND(100.0 * SUM(CASE WHEN f.is_late THEN 1 ELSE 0 END) / COUNT(*), 2)      AS late_pct,
    ROUND(AVG(f.delivery_days), 1)                                                AS avg_delivery_days,
    ROUND(AVG(f.avg_review_score), 2)                                             AS avg_review_score
FROM fact_orders f
JOIN dim_customers c ON f.customer_key = c.customer_key
GROUP BY c.customer_state
ORDER BY late_pct DESC;


-- ── Q5: Rolling 3-Month Revenue Average ──────────────────────────────────────
-- Business insight: Smooth noise to expose true revenue direction for exec
-- reporting and near-term forecasting.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    d.year,
    d.month,
    ROUND(SUM(f.revenue), 2)                                                      AS monthly_revenue,
    ROUND(AVG(SUM(f.revenue)) OVER (
        ORDER BY d.year, d.month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2)                                                                         AS rolling_3m_avg,
    ROUND(SUM(SUM(f.revenue)) OVER (
        ORDER BY d.year, d.month
    ), 2)                                                                         AS cumulative_revenue
FROM fact_orders f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month;


-- ── Q6: Top 5 Sellers per State (ROW_NUMBER) ─────────────────────────────────
-- Business insight: Benchmark local market leaders in each state. Operations
-- can study their practices for regional replication.
-- ─────────────────────────────────────────────────────────────────────────────
WITH seller_state_revenue AS (
    SELECT
        s.seller_id,
        s.seller_state,
        COUNT(DISTINCT f.order_id)          AS total_orders,
        ROUND(SUM(f.revenue), 2)            AS total_revenue,
        ROUND(AVG(f.avg_review_score), 2)   AS avg_review,
        ROUND(AVG(f.delivery_days), 1)      AS avg_delivery_days,
        ROW_NUMBER() OVER (
            PARTITION BY s.seller_state
            ORDER BY SUM(f.revenue) DESC
        )                                   AS state_rank
    FROM fact_orders f
    JOIN dim_sellers s ON f.seller_key = s.seller_key
    GROUP BY s.seller_id, s.seller_state
)
SELECT * FROM seller_state_revenue
WHERE state_rank <= 5
ORDER BY seller_state, state_rank;


-- ── Q7: Revenue Contribution % by Category ───────────────────────────────────
-- Business insight: Quantify business concentration risk. If 2-3 categories
-- drive >60% revenue, that is a strategic vulnerability.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    p.product_category_name,
    ROUND(SUM(f.revenue), 2)                                                      AS category_revenue,
    ROUND(SUM(f.profit),  2)                                                      AS category_profit,
    COUNT(DISTINCT f.order_id)                                                    AS orders,
    ROUND(100.0 * SUM(f.revenue) / SUM(SUM(f.revenue)) OVER (), 2)               AS pct_of_total_revenue,
    ROUND(SUM(100.0 * SUM(f.revenue) / SUM(SUM(f.revenue)) OVER ()) OVER (
        ORDER BY SUM(f.revenue) DESC
        ROWS UNBOUNDED PRECEDING
    ), 2)                                                                         AS cumulative_pct
FROM fact_orders f
JOIN dim_products p ON f.product_key = p.product_key
GROUP BY p.product_category_name
ORDER BY pct_of_total_revenue DESC;


-- ── Q8: Monthly Customer Cohort Retention ────────────────────────────────────
-- Business insight: Measure true customer loyalty. Falling retention in months
-- 2+ indicates a post-purchase experience or product quality problem.
-- ─────────────────────────────────────────────────────────────────────────────
WITH first_purchase AS (
    SELECT
        f.customer_key,
        MIN(d.date_key)                 AS first_date_key,
        MIN(d.year * 100 + d.month)     AS cohort_ym
    FROM fact_orders f
    JOIN dim_date d ON f.date_key = d.date_key
    GROUP BY f.customer_key
),
activity AS (
    SELECT
        fp.cohort_ym,
        fp.customer_key,
        (d.year * 12 + d.month) - ((fp.cohort_ym / 100) * 12 + MOD(fp.cohort_ym, 100)) AS month_number
    FROM fact_orders f
    JOIN dim_date d       ON f.date_key       = d.date_key
    JOIN first_purchase fp ON f.customer_key  = fp.customer_key
)
SELECT
    cohort_ym,
    month_number,
    COUNT(DISTINCT customer_key)    AS customers,
    ROUND(100.0 * COUNT(DISTINCT customer_key)
          / FIRST_VALUE(COUNT(DISTINCT customer_key)) OVER (
                PARTITION BY cohort_ym ORDER BY month_number
            ), 1)                   AS retention_pct
FROM activity
GROUP BY cohort_ym, month_number
ORDER BY cohort_ym, month_number;


-- ── Q9: Average Order Value & GMV by Payment Type ────────────────────────────
-- Business insight: Credit card installments correlate with higher AOV.
-- Informs checkout UX and financing promotion strategy.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    payment_type,
    COUNT(DISTINCT order_id)            AS total_orders,
    ROUND(AVG(payment_value),  2)       AS avg_order_value,
    ROUND(SUM(payment_value),  2)       AS total_gmv,
    ROUND(AVG(payment_installments), 1) AS avg_installments,
    ROUND(100.0 * SUM(payment_value) /
          SUM(SUM(payment_value)) OVER (), 2) AS pct_of_gmv
FROM fact_orders
WHERE payment_type IS NOT NULL
GROUP BY payment_type
ORDER BY total_gmv DESC;


-- ── Q10: Delivery Speed Tiers vs Review Score & Late Rate ────────────────────
-- Business insight: Quantifies how delivery speed directly drives customer
-- satisfaction — a clear business case for logistics investment.
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    CASE
        WHEN delivery_days <= 3  THEN '1 - Express (≤3 days)'
        WHEN delivery_days <= 7  THEN '2 - Fast (4–7 days)'
        WHEN delivery_days <= 14 THEN '3 - Standard (8–14 days)'
        ELSE                          '4 - Slow (15+ days)'
    END                                     AS delivery_tier,
    COUNT(*)                                AS total_orders,
    ROUND(AVG(avg_review_score), 2)         AS avg_review_score,
    ROUND(AVG(delivery_days::NUMERIC), 1)   AS avg_delivery_days,
    ROUND(100.0 * SUM(CASE WHEN is_late THEN 1 ELSE 0 END) / COUNT(*), 1) AS late_pct,
    ROUND(SUM(revenue), 2)                  AS total_revenue
FROM fact_orders
WHERE delivery_days IS NOT NULL
GROUP BY delivery_tier
ORDER BY delivery_tier;
