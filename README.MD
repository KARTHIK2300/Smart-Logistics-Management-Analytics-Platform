# 🚚 Smart Logistics Management & Analytics Platform

## 📌 Project Overview
The Smart Logistics Management & Analytics Platform is an end-to-end data pipeline and dashboard solution designed to simulate enterprise-grade logistics operations. It consolidates scattered operational data (shipments, tracking, costs, routes, couriers, and warehouses) into a centralized MySQL database and surfaces real-time insights through an interactive Streamlit application.

## 🎯 Objectives
* **Data Ingestion**: Clean and ingest 70,000+ logistics records from CSV and JSON formats using automated Python scripts.
* **Database Management**: Store data in a fully normalized MySQL relational database maintaining referential integrity.
* **Dashboarding**: Provide an interactive Streamlit interface for shipment tracking, KPI monitoring, and operational deep-dives utilizing Plotly visualizations.
* **Business Intelligence**: Answer critical business questions regarding bottleneck routes, courier efficiency, cost analytics, and cancellation patterns.

## 🛠️ Technology Stack
* **Language**: Python 3.8+ (pandas, numpy)
* **Database**: MySQL (SQLAlchemy, pymysql)
* **Frontend**: Streamlit, Plotly Express
* **Data Formats**: CSV, JSON, Excel

## 🗄️ Database Schema
The MySQL database (`logistics_db`) consists of 6 normalized tables:
1. **`courier_staff`**: Employee metrics, ratings, and vehicle assignments.
2. **`warehouses`**: Regional storage capacities and locations.
3. **`routes`**: Origin-destination pairs, distances in km, and expected transit times.
4. **`shipments`**: Core order data linking origins, destinations, and assigned couriers.
5. **`shipment_tracking`**: Timestamped status logs for active tracking events.
6. **`costs`**: Breakdown of fuel, labor, and miscellaneous costs per shipment.

## 🚀 Setup & Installation Instructions

### 1. Prerequisites
Ensure you have **Python 3.8+** and **MySQL Server** installed and running on your local machine.

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/smart-logistics-platform.git
cd smart-logistics-platform
