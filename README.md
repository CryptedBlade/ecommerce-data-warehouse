# E-Commerce Data Warehouse + BI Dashboard

End-to-end data warehouse project modeling e-commerce order data into a star
schema, with Python ETL, advanced SQL analytics, and a Power BI dashboard.

---

## Skills Demonstrated

| Skill | Where |
|---|---|
| Star Schema Design | `sql/ddl/create_tables.sql` — 1 fact + 4 dimension tables |
| Window Functions | `sql/queries/advanced_queries.sql` — RANK, LAG, NTILE, ROW_NUMBER, FIRST_VALUE, SUM/AVG OVER |
| Dynamic SQL | `src/load_to_postgres.py` — row-count validation across variable table names |
| Pivoting / Unpivoting | `sql/queries/advanced_queries.sql` — Queries 11–12, monthly category revenue |
| ETL Pipeline | `src/etl_pipeline.py` — Pandas-based cleaning, dedup, transformation |
| BI Dashboarding | `dashboard/ecommerce_dashboard.pbix` — Power BI connected to PostgreSQL |

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
│       └── advanced_queries.sql  # 12 analytical queries (window fns, dynamic SQL, pivot/unpivot)
├── dashboard/
│   ├── ecommerce_dashboard.pbix  # Power BI file
│   └── screenshots/              # Chart PNGs
├── docs/
│   └── data_dictionary.md        # Column-level documentation
├── run_all.py                    # One-click full pipeline runner
├── requirements.txt
├── .env.example
└── README.md

---

## Quick Start

### 1. Clone & install dependencies

```bash
git clone https://github.com/CryptedBlade/ecommerce-data-warehouse.git
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
python src/generate_sample_data.py    # Generate sample data (or use real Kaggle CSVs in data/raw/)
python src/etl_pipeline.py            # Clean, transform, build star schema CSVs
python src/eda_and_visualizations.py  # Generate EDA charts
python src/load_to_postgres.py        # Load into PostgreSQL
```

### 5. Connect Power BI

1. Open `dashboard/ecommerce_dashboard.pbix` in Power BI Desktop
2. Go to **Home → Transform data → Data source settings**
3. Update the PostgreSQL server/database to match your `.env`
4. Click **Refresh**

---

## Star Schema
