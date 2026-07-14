# Power BI Dashboard Setup Guide

## Prerequisites
- Power BI Desktop (free download from Microsoft)
- PostgreSQL running with the ecommerce_dw database loaded

---

## Step 1: Connect Power BI to PostgreSQL

1. Open Power BI Desktop
2. Click **Home → Get Data → Database → PostgreSQL database**
3. Enter:
   - Server: `localhost` (or your DB host)
   - Database: `ecommerce_dw`
4. Click **OK → DirectQuery** (recommended for large data) or **Import**
5. Select all 5 tables: `fact_orders`, `dim_date`, `dim_customers`, `dim_products`, `dim_sellers`

---

## Step 2: Define Relationships

Go to **Model view** and verify/create these relationships:

| From Table | Column | To Table | Column | Cardinality |
|---|---|---|---|---|
| fact_orders | customer_key | dim_customers | customer_key | Many → One |
| fact_orders | product_key | dim_products | product_key | Many → One |
| fact_orders | seller_key | dim_sellers | seller_key | Many → One |
| fact_orders | date_key | dim_date | date_key | Many → One |

---

## Step 3: Create DAX Measures

In the **fact_orders** table, add these measures:

```dax
Total Revenue =
    SUM(fact_orders[revenue])

Total Orders =
    DISTINCTCOUNT(fact_orders[order_id])

Avg Order Value =
    DIVIDE([Total Revenue], [Total Orders])

Total Profit =
    SUM(fact_orders[profit])

Profit Margin % =
    DIVIDE([Total Profit], [Total Revenue]) * 100

Late Delivery Rate % =
    DIVIDE(
        COUNTROWS(FILTER(fact_orders, fact_orders[is_late] = TRUE())),
        COUNTROWS(fact_orders)
    ) * 100

Avg Review Score =
    AVERAGE(fact_orders[avg_review_score])

MoM Revenue Growth % =
    VAR CurrentMonth = [Total Revenue]
    VAR PrevMonth =
        CALCULATE(
            [Total Revenue],
            DATEADD(dim_date[full_date], -1, MONTH)
        )
    RETURN
        DIVIDE(CurrentMonth - PrevMonth, PrevMonth) * 100
```

---

## Step 4: Dashboard Layout

### Page 1 — Executive Overview
- **KPI Cards** (top row): Total Revenue · Total Orders · Avg Order Value · Avg Review Score
- **Line Chart**: Monthly Revenue Trend (X: month, Y: Total Revenue, Line: Rolling Avg)
- **Bar Chart**: Revenue by Product Category (top 10, horizontal)
- **Map Visual**: Orders by Customer State (bubble map of Brazil)
- **Slicer Panel**: Date Range · Order Status · Product Category

### Page 2 — Customer & Product Analysis
- **Scatter Chart**: Customer RFM (X: Frequency, Y: Revenue, Size: Recency)
- **Matrix Heatmap**: Cohort Retention (rows: cohort month, cols: months since first order)
- **Bar Chart**: Avg Review Score by Category (reference line at 4.0)
- **Donut Chart**: Payment Type GMV Share

### Page 3 — Logistics & Sellers
- **Table**: Late Delivery Rate by State (conditional formatting: red = high late %)
- **Bar Chart**: Delivery Tier vs Avg Review Score
- **Table**: Top Sellers (GMV, orders, avg delivery days, avg review)
- **Card**: Overall Late Delivery Rate %

---

## Step 5: Apply Filters / Slicers

Add to each page:
- Date slicer (between) on `dim_date[full_date]`
- Dropdown slicer on `dim_customers[customer_state]`
- Dropdown slicer on `dim_products[product_category_name]`
- Toggle slicer on `fact_orders[order_status]`

Enable **Sync slicers** across all pages via View → Sync slicers.

---

## Recommended Colour Theme

| Metric | Colour |
|---|---|
| Revenue / Positive | #534AB7 (purple) |
| Profit | #1D9E75 (teal) |
| Late / Negative | #E24B4A (red) |
| Neutral | #888780 (gray) |
| Accent | #EF9F27 (amber) |
