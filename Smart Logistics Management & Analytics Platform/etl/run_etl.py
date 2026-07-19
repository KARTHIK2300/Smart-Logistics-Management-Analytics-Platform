import data_cleaning as clean
import sql_ingestion as db

def run_pipeline():
    print("=== Starting ETL Pipeline ===")
    engine = db.get_engine()
    
    try:
        # Clear existing data so we don't get duplicate errors from previous runs
        db.clear_database(engine)

        # Extract & Clean Data
        df_couriers = clean.clean_couriers()
        df_routes = clean.clean_routes()
        df_warehouses = clean.clean_warehouses()
        
        df_shipments = clean.clean_shipments()
        df_tracking = clean.clean_tracking()
        df_costs = clean.clean_costs()
        
        # Load Data into SQL
        print("\n=== Loading Data to Database ===")
        db.load_data_to_sql(df_couriers, 'courier_staff', engine)
        db.load_data_to_sql(df_routes, 'routes', engine)
        db.load_data_to_sql(df_warehouses, 'warehouses', engine)
        
        db.load_data_to_sql(df_shipments, 'shipments', engine)
        db.load_data_to_sql(df_tracking, 'shipment_tracking', engine)
        db.load_data_to_sql(df_costs, 'costs', engine)
        
        print("\n=== ETL Pipeline Completed Successfully ===")
        
    except Exception as e:
        print(f"\nPipeline failed due to an error: {e}")

if __name__ == "__main__":
    run_pipeline()