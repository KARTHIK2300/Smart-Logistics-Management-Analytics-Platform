from sqlalchemy import create_engine, text
import pandas as pd

DB_USER = 'root'
DB_PASSWORD = '12345' 
DB_HOST = 'localhost'
DB_NAME = 'logistics_db'

def get_engine():
    return create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

def clear_database(engine):
    print("Clearing existing database tables to prevent duplicates...")
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        for table in ['shipment_tracking', 'costs', 'shipments', 'routes', 'warehouses', 'courier_staff']:
            conn.execute(text(f"TRUNCATE TABLE {table};"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        conn.commit()

def load_data_to_sql(df, table_name, engine, chunk_size=5000):
    if df is None or df.empty:
        print(f"Skipping {table_name}: No data to load.")
        return

    print(f"Loading {len(df)} records into the '{table_name}' table...")
    try:
        df.to_sql(name=table_name, con=engine, if_exists='append', index=False, chunksize=chunk_size)
        print(f"Successfully loaded data into '{table_name}'.")
    except Exception as e:
        print(f"Failed to load data into '{table_name}'. Error: {e}")