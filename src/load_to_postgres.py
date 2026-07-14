"""
load_to_postgres.py
Loads processed CSV files into PostgreSQL using SQLAlchemy + psycopg2.
Run AFTER etl_pipeline.py.
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'ecommerce_dw')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASSWORD', 'yourpassword')

PROC_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
DDL_FILE = os.path.join(os.path.dirname(__file__), '..', 'sql', 'ddl', 'create_tables.sql')

CONNECTION_STRING = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


def get_engine():
    engine = create_engine(CONNECTION_STRING, echo=False)
    print(f"Connected to: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    return engine


def run_ddl(engine):
    with open(DDL_FILE, 'r') as f:
        ddl = f.read()
    with engine.connect() as conn:
        conn.execute(text(ddl))
        conn.commit()
    print("Schema created successfully.")


def load_table(engine, csv_name, table_name, if_exists='append'):
    path = os.path.join(PROC_DIR, csv_name)
    df = pd.read_csv(path)
    
    # Fix for dim_date
    if table_name == 'dim_date':
        df['is_weekend'] = df['is_weekend'].astype(bool)

    # Fix for fact_orders (Add these two lines)
    if table_name == 'fact_orders':
        df['is_late'] = df['is_late'].astype(bool)

    df.to_sql(table_name, engine, if_exists=if_exists, index=False, method='multi', chunksize=500)
    print(f"  Loaded {len(df):,} rows → {table_name}")

def main():
    engine = get_engine()

    print("\nCreating schema...")
    run_ddl(engine)

    print("\nLoading dimension tables (order matters — FK deps)...")
    load_table(engine, 'dim_date.csv',      'dim_date')
    load_table(engine, 'dim_customers.csv', 'dim_customers')
    load_table(engine, 'dim_products.csv',  'dim_products')
    load_table(engine, 'dim_sellers.csv',   'dim_sellers')

    print("\nLoading fact table...")
    load_table(engine, 'fact_orders.csv',   'fact_orders')

    print("\nRow counts:")
    with engine.connect() as conn:
        for tbl in ['dim_date','dim_customers','dim_products','dim_sellers','fact_orders']:
            result = conn.execute(text(f'SELECT COUNT(*) FROM {tbl}')).scalar()
            print(f"  {tbl:20s}  {result:,}")

    print("\nDatabase load complete!")


if __name__ == '__main__':
    main()
