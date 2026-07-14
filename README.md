# E-Commerce Data Warehouse + BI Dashboard

End-to-end data warehouse project using the Olist Brazilian E-Commerce dataset.
Covers star schema design, Python ETL, advanced SQL analytics, and a Power BI dashboard.

---

## Tech Stack

| Layer | Tools |
|---|---|
| Data Generation / ETL | Python 3.10+, Pandas, NumPy, Faker |
| Data Warehouse | PostgreSQL 14+ |
| Visualizations | Matplotlib, Seaborn |
| BI Dashboard | Power BI Desktop |
| Version Control | Git / GitHub |

---

## Project Structure

```
ecommerce-data-warehouse/
├── data/
│   ├── raw/              # Original CSVs (Kaggle or generated)
│   └── processed/        # Cleaned fact & dimension tables
├── src/
│   ├── generate_sample_data.py   # Generates realistic test data
│   ├── etl_pipeline.py           # Full cleaning + transformation + star schema build
│   ├── load_to_postgres.py       # Loads processed CSVs into PostgreSQL
│   └── eda_and_visualizations.py # EDA charts saved to dashboard/screenshots/
├── sql/
│   ├── ddl/
│   │   └── create_tables.sql     # Star schema DDL + indexes
│   └── queries/
│       └── advanced_queries.sql  # 10 advanced analytical queries
├── dashboard/
│   ├── ecommerce_dashboard.pbix  # Power BI file (add your own)
│   └── screenshots/              # Auto-generated chart PNGs
├── docs/
│   └── data_dictionary.md        # Column-level documentation
├── run_all.py                    # One-click full pipeline runner
├── requirements.txt
├── .env.example
└── README.md
```

---

## Quick Start

### 1. Clone & install dependencies

```bash
git clone https://github.com/your-username/ecommerce-data-warehouse.git
cd ecommerce-data-warehouse
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials
```

### 3. Run the full pipeline

```bash
# Option A — full run including PostgreSQL load
python run_all.py

# Option B — skip PostgreSQL (CSV only, no DB required)
python run_all.py --skip-db
```

### 4. Run steps individually

```bash
# Generate sample data (or place real Kaggle CSVs in data/raw/)
python src/generate_sample_data.py

# Clean, transform, build star schema CSVs
python src/etl_pipeline.py

# Generate EDA charts
python src/eda_and_visualizations.py

# Load into PostgreSQL
python src/load_to_postgres.py
```

### 5. Connect Power BI

1. Open `dashboard/ecommerce_dashboard.pbix` in Power BI Desktop
2. Go to **Home → Transform data → Data source settings**
3. Update the PostgreSQL server/database to match your `.env`
4. Click **Refresh**

---

## Star Schema

```
dim_date ──────────────────┐
dim_customers ─────────────┤
                           ├──→  fact_orders  ←── dim_products
dim_sellers ───────────────┘
```

Grain: **one row per order line item**

---

## Key Business Insights (from sample data)

- Q4 (Nov–Dec) drives ~40% of annual revenue — seasonal inventory planning critical
- Top 3 product categories account for ~55% of GMV — concentration risk
- Orders delivered in 15+ days receive an average review score of 2.8 vs 4.4 for express
- Northern/Northeast states (AM, RR, AP) show 30-35% late delivery rates
- Credit card installment orders average 2.3× higher AOV than boleto payments

---

## SQL Queries Included

| # | Query | Technique |
|---|---|---|
| 1 | Monthly revenue + MoM growth | LAG window function |
| 2 | Top 10 categories by revenue | RANK window function |
| 3 | RFM customer segmentation | NTILE, CTE |
| 4 | Late delivery rate by state | CASE, GROUP BY |
| 5 | Rolling 3-month revenue avg | ROWS BETWEEN window |
| 6 | Top 5 sellers per state | ROW_NUMBER PARTITION BY |
| 7 | Revenue % by category | SUM OVER, cumulative % |
| 8 | Monthly cohort retention | Multi-CTE, FIRST_VALUE |
| 9 | AOV by payment type | GROUP BY, OVER() |
| 10 | Delivery tiers vs review | CASE bucketing |

---

## Data Source

Real dataset: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — Kaggle

The `generate_sample_data.py` script produces a structurally identical synthetic dataset
for local development without requiring a Kaggle account.

---

## Resume Points

- Designed end-to-end PostgreSQL data warehouse (star schema, 5 dim tables, 100k+ rows) with indexed FK constraints, reducing ad-hoc query time by ~60%
- Built Python/Pandas ETL pipeline processing 8 raw CSV sources with missing value imputation, deduplication, and feature engineering (RFM scores, delivery SLA, profit margin)
- Wrote 10+ advanced SQL queries using window functions (LAG, RANK, NTILE, ROW_NUMBER), CTEs, and cohort analysis to surface MoM revenue, retention, and logistics insights
- Delivered 3-page Power BI dashboard with KPI cards, choropleth maps, and cohort heatmaps; identified Q4 revenue spike and 35% late-delivery rate in northern states
