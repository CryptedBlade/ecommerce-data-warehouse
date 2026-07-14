-- q01_monthly_revenue.sql
-- Monthly revenue trend with month-over-month growth %
-- Business value: identifies seasonal peaks and revenue momentum

SELECT
    d.year,
    d.month,
    d.month_name,
    ROUND(SUM(f.revenue), 2)                                                        AS total_revenue,
    COUNT(DISTINCT f.order_id)                                                      AS total_orders,
    ROUND(AVG(f.revenue), 2)                                                        AS avg_order_value,
    LAG(SUM(f.revenue)) OVER (ORDER BY d.year, d.month)                             AS prev_month_revenue,
    ROUND(
        (SUM(f.revenue) - LAG(SUM(f.revenue)) OVER (ORDER BY d.year, d.month))
        / NULLIF(LAG(SUM(f.revenue)) OVER (ORDER BY d.year, d.month), 0) * 100
    , 2)                                                                            AS mom_growth_pct
FROM fact_orders f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;
