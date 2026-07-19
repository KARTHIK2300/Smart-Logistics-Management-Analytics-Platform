CREATE DATABASE IF NOT EXISTS logistics_db; 
USE logistics_db;

-- 1. Table: courier_staff
CREATE TABLE IF NOT EXISTS courier_staff (
    courier_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    rating DECIMAL(3,1),
    vehicle_type VARCHAR(50)
);

-- 2. Table: warehouses
CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id VARCHAR(50) PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50),
    capacity INT
);

-- 3. Table: routes
CREATE TABLE IF NOT EXISTS routes (
    route_id VARCHAR(50) PRIMARY KEY,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    distance_km DECIMAL(10,2),
    avg_time_hours DECIMAL(5,2),
    -- Index to speed up geographic JOINs with the shipments table
    INDEX idx_route_locations (origin, destination) 
);

-- 4. Table: shipments
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id VARCHAR(50) PRIMARY KEY,
    order_date DATE NOT NULL,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    weight DECIMAL(10,2),
    courier_id VARCHAR(50),
    status VARCHAR(50) NOT NULL,
    delivery_date DATE NULL,
    FOREIGN KEY (courier_id) REFERENCES courier_staff(courier_id) ON DELETE SET NULL,
    -- Performance Indexes for 70k+ rows Streamlit filtering
    INDEX idx_shipment_status (status),
    INDEX idx_shipment_locations (origin, destination),
    INDEX idx_shipment_dates (order_date, delivery_date)
);

-- 5. Table: shipment_tracking
CREATE TABLE IF NOT EXISTS shipment_tracking (
    tracking_id INT AUTO_INCREMENT PRIMARY KEY,
    shipment_id VARCHAR(50),
    status VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id) ON DELETE CASCADE,
    INDEX idx_tracking_shipment (shipment_id)
);

-- 6. Table: costs
CREATE TABLE IF NOT EXISTS costs (
    shipment_id VARCHAR(50) PRIMARY KEY,
    fuel_cost DECIMAL(15,2) DEFAULT 0.00,
    labor_cost DECIMAL(15,2) DEFAULT 0.00,
    misc_cost DECIMAL(15,2) DEFAULT 0.00,
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id) ON DELETE CASCADE
);

-- Clear any existing records from child tables first to prevent constraint violations
SET FOREIGN_KEY_CHECKS = 0; 
TRUNCATE TABLE shipment_tracking; 
TRUNCATE TABLE costs; 
TRUNCATE TABLE shipments; 
TRUNCATE TABLE routes; 
TRUNCATE TABLE warehouses; 
TRUNCATE TABLE courier_staff; 
SET FOREIGN_KEY_CHECKS = 1;

-- (You can append your INSERT INTO statements here as needed)