import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
from sqlalchemy import create_engine

# App Configuration
st.set_page_config(page_title="Smart Logistics Analytics Platform", layout="wide")

# Database connection helper
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="logistics_db"
    )

# Load data helper safely
def run_query(query, params=None):
    conn = get_connection()
    try:
        df = pd.read_sql(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"Database Query Error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

st.title("📦 Smart Logistics Management & Analytics Platform")
st.markdown("---")

# Navigation Sidebar
menu = ["Dashboard Overview", "Shipment Search & Filter", "Analytical Deep Dives"]
choice = st.sidebar.selectbox("Navigate Menu", menu)

# -------------------------------------------------------------
# VIEW 1: DASHBOARD OVERVIEW & KPIs
# -------------------------------------------------------------
if choice == "Dashboard Overview":
    st.subheader("📊 Operational KPIs")
    
    # Query for calculating standard project KPIs
    kpi_query = """
        SELECT 
            COUNT(s.shipment_id) as total_shipments,
            SUM(CASE WHEN s.status = 'Delivered' THEN 1 ELSE 0 END) / COUNT(s.shipment_id) * 100 as delivery_rate,
            SUM(CASE WHEN s.status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(s.shipment_id) * 100 as cancellation_rate,
            AVG(DATEDIFF(s.delivery_date, s.order_date)) as avg_delivery_time,
            SUM(c.fuel_cost + c.labor_cost + c.misc_cost) as total_cost
        FROM shipments s
        LEFT JOIN costs c ON s.shipment_id = c.shipment_id
    """
    kpi_df = run_query(kpi_query)
    
    if not kpi_df.empty:
        # Safely extract values or default to 0 if they are None
        total_shipments = kpi_df['total_shipments'].iloc[0] or 0
        delivery_rate = kpi_df['delivery_rate'].iloc[0] or 0.0
        cancellation_rate = kpi_df['cancellation_rate'].iloc[0] or 0.0
        avg_delivery_time = kpi_df['avg_delivery_time'].iloc[0] or 0.0
        total_cost = kpi_df['total_cost'].iloc[0] or 0.0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Shipments", f"{total_shipments:,}")
    col2.metric("Delivered %", f"{delivery_rate:.1f}%")
    col3.metric("Cancelled %", f"{cancellation_rate:.1f}%")
    col4.metric("Avg TransTime", f"{avg_delivery_time:.1f} Days")
    col5.metric("Total Op Cost", f"${total_cost:,.2f}")
    
    st.markdown("---")
    st.subheader("📍 High-Traffic Warehouse Cities")
    warehouse_query = """
        SELECT city, capacity, COUNT(*) as active_hubs 
        FROM warehouses GROUP BY city, capacity ORDER BY capacity DESC LIMIT 5
    """
    wh_df = run_query(warehouse_query)
    if not wh_df.empty:
        fig = px.bar(wh_df, x='city', y='capacity', color='city', title="Top Warehouses by Volume Capacity")
        st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------
# VIEW 2: SHIPMENT SEARCH & FILTERS
# -------------------------------------------------------------
elif choice == "Shipment Search & Filter":
    st.subheader("🔎 Shipment Search & Global Filtering")
    
    # Single Item Lookup Feature
    search_id = st.text_input("Enter exact Shipment ID to search:")
    if search_id:
        track_query = """
            SELECT status, timestamp FROM shipment_tracking 
            WHERE shipment_id = %s ORDER BY timestamp DESC
        """
        track_df = run_query(track_query, (search_id,))
        if not track_df.empty:
            st.success(f"Tracking Details Found for {search_id}")
            st.dataframe(track_df)
        else:
            st.warning("No shipment/logs found with that tracking ID.")
            
    st.markdown("---")
    st.markdown("#### Filter Shipments Dataset")
    
    # Dynamic setup filters
    col1, col2, col3 = st.columns(3)
    # Automatically fetch all unique statuses directly from the database
    status_options = ["All"] + run_query("SELECT DISTINCT status FROM shipments")['status'].tolist()
    status_filter = col1.selectbox("Status", status_options)
    origin_filter = col2.text_input("Origin City Name (or leave blank):")
    dest_filter = col3.text_input("Destination City Name (or leave blank):")
    
    filter_query = "SELECT * FROM shipments WHERE 1=1"
    params = []
    
    if status_filter != "All":
        filter_query += " AND status = %s"
        params.append(status_filter)
    if origin_filter:
        filter_query += " AND origin LIKE %s"
        params.append(f"%{origin_filter}%")
    if dest_filter:
        filter_query += " AND destination LIKE %s"
        params.append(f"%{dest_filter}%")
        
    filter_query += " LIMIT 100" # Batch layout optimization for responsive performance
    results_df = run_query(filter_query, tuple(params))
    st.dataframe(results_df)

# -------------------------------------------------------------
# VIEW 3: ANALYTICAL DEEP DIVES
# -------------------------------------------------------------
elif choice == "Analytical Deep Dives":
    st.subheader("📈 Operational Analytics & Business Intelligence")
    
    tab1, tab2, tab3 = st.tabs(["Delivery Performance & Routes", "Courier Strategy", "Cost Diagnostics"])
    
    with tab1:
        st.markdown("### Route Bottlenecks vs Delays")
        
        # Optimized query to fetch route data [cite: 40]
        route_query = """
            SELECT 
                route_id,
                origin, 
                destination, 
                CONCAT(origin, ' → ', destination) AS route_name,
                distance_km, 
                avg_time_hours 
            FROM routes 
            ORDER BY avg_time_hours DESC 
            LIMIT 20
        """
        route_df = run_query(route_query)
        
        if not route_df.empty:
            # Re-engineered Plotly Scatter plot
            fig = px.scatter(
                route_df, 
                x="distance_km", 
                y="avg_time_hours", 
                color="avg_time_hours",       
                color_continuous_scale="Reds", 
                size="avg_time_hours",         
                hover_name="route_name",       
                hover_data={
                    "route_id": True,
                    "distance_km": ":.2f km",  
                    "avg_time_hours": ":.1f hrs"
                },
                labels={
                    "distance_km": "Distance (Kilometers)",
                    "avg_time_hours": "Average Travel Time (Hours)"
                },
                title="Expected Route Hours vs Net Distance"
            )
            
            # Enforce clean formatting and black text styling for all chart text elements
            fig.update_layout(
                margin=dict(l=40, r=40, t=50, b=40),
                
                # Fix 1: Enforces solid black text inside the hover cards / pop-up dot points
                hoverlabel=dict(
                    bgcolor="white",       
                    font_size=14,          
                    font_family="Arial",   
                    font_color="black"     # Forces hover text to black
                )
            )
            
            # Fix 2: If text labels are drawn on the graph, force their font colors to black
            fig.update_traces(
                textposition='top center',
                textfont=dict(
                    family="Arial",
                    size=12,
                    color="black"          # Forces on-graph text labels to black
                )
            )
            
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No route operational metrics found to display.")
            
    with tab2:
        st.markdown("### Courier Assessment Matrix")
        courier_query = """
            SELECT name, vehicle_type, rating FROM courier_staff 
            WHERE rating IS NOT NULL ORDER BY rating DESC LIMIT 15
        """
        courier_df = run_query(courier_query)
        if not courier_df.empty:
            fig = px.bar(courier_df, x="name", y="rating", color="vehicle_type", 
                         title="Courier Employee Ratings Matrix")
            st.plotly_chart(fig, use_container_width=True)
            
    with tab3:
        st.markdown("### Financial Cost Components")
        cost_query = """
            SELECT 
                SUM(fuel_cost) as Total_Fuel, 
                SUM(labor_cost) as Total_Labor, 
                SUM(misc_cost) as Total_Misc 
            FROM costs
        """
        cost_df = run_query(cost_query)
        if not cost_df.empty and cost_df.iloc[0]['Total_Fuel'] is not None:
            melted_df = pd.DataFrame({
                'Cost Component': ['Fuel', 'Labor', 'Misc'],
                'Expenses ($)': [cost_df.iloc[0]['Total_Fuel'], cost_df.iloc[0]['Total_Labor'], cost_df.iloc[0]['Total_Misc']]
            })
            fig = px.pie(melted_df, values='Expenses ($)', names='Cost Component', title='Expense Weight Contribution Percentage')
            st.plotly_chart(fig, use_container_width=True)