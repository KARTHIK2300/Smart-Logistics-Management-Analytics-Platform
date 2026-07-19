# 📂 Project Structure: Smart Logistics Management & Analytics Platform

```text
smart-logistics-platform/
│
├── 📂 data/                         # Contains all raw datasets
│   ├── shipments.json               # Shipment order data
│   ├── shipment_tracking.csv        # Tracking logs (or .xlsx)
│   ├── courier_staff.csv            # Courier details
│   ├── routes.csv                   # Route distances and time
│   ├── warehouses.csv               # Warehouse capacities
│   └── costs.csv                    # Operational costs
│
├── 📂 database/                     # SQL Scripts
│   └── schema.sql                   # Table creation script (e.g., MYSQL80.sql)
│
├── 📂 etl/                          # Extract, Transform, Load logic
│   ├── data_cleaning.py             # Data extraction and pandas transformation logic
│   ├── sql_ingestion.py             # SQLAlchemy bulk insertion logic (chunking)
│   └── run_etl.py                   # Main execution script to trigger the pipeline
│
├── 📂 app/                          # Streamlit application files
│   └── app.py                       # Main frontend dashboard code
│
├── requirements.txt                 # Python dependencies
├── README.md                        # Project documentation
└── Project_Structure.md             # Project folder layout