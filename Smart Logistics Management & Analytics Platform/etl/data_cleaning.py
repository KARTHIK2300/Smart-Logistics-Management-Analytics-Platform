import pandas as pd
import json
import os

def get_path(filename):
    for root, dirs, files in os.walk(os.getcwd()):
        if filename in files:
            return os.path.join(root, filename)
    raise FileNotFoundError(f"Could not find '{filename}' anywhere in your project folders.")

def clean_couriers():
    print("Cleaning Courier Staff data...")
    df = pd.read_csv(get_path('courier_staff.csv'))
    df = df.drop_duplicates(subset=['courier_id'])
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    return df

def clean_routes():
    print("Cleaning Routes data...")
    df = pd.read_csv(get_path('routes.csv'))
    df = df.drop_duplicates(subset=['route_id'])
    df['distance_km'] = pd.to_numeric(df['distance_km'], errors='coerce')
    df['avg_time_hours'] = pd.to_numeric(df['avg_time_hours'], errors='coerce')
    return df

def clean_warehouses():
    print("Cleaning Warehouses data...")
    try:
        with open(get_path('warehouses.json'), 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        
        df = df.drop_duplicates(subset=['warehouse_id'])
        return df
    except FileNotFoundError:
        print("Warning: warehouses.json not found. Skipping.")
        return None

def clean_shipments():
    print("Cleaning Shipments data...")
    with open(get_path('shipments.json'), 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    
    df = df.drop_duplicates(subset=['shipment_id'])
    
    df['order_date'] = pd.to_datetime(df['order_date']).dt.date
    df['delivery_date'] = pd.to_datetime(df['delivery_date'], errors='coerce').dt.date
    df['delivery_date'] = df['delivery_date'].replace({pd.NaT: None})
    df['weight'] = pd.to_numeric(df['weight'], errors='coerce')
    return df

def clean_tracking():
    print("Cleaning Shipment Tracking data...")
    try:
        df = pd.read_csv(get_path('shipment_tracking.csv'))
    except FileNotFoundError:
        try:
            df = pd.read_excel(get_path('shipment_tracking.xlsx'))
        except FileNotFoundError:
            print("Warning: Tracking file not found. Skipping.")
            return None
            
    df = df.drop_duplicates(subset=['tracking_id'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def clean_costs():
    print("Cleaning Costs data...")
    try:
        df = pd.read_csv(get_path('costs.csv'))
    except FileNotFoundError:
        with open(get_path('costs.json'), 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        
    df = df.drop_duplicates(subset=['shipment_id'])
    for col in ['fuel_cost', 'labor_cost', 'misc_cost']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    return df