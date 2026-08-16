import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import urllib.parse

# App Configuration
st.set_page_config(page_title="Smart Logistics Analytics Platform", layout="wide")

# Database connection using SQLAlchemy
# (Make sure to install pymysql if you haven't: pip install pymysql)
@st.cache_resource
def get_engine():
    # Safely parse password if it contains special characters
    password = urllib.parse.quote_plus("12345")
    engine = create_engine(f"mysql+pymysql://root:{password}@localhost/logistics_db")
    return engine

# Load data helper using SQLAlchemy engine
def run_query(query, params=None):
    engine = get_engine()
    try:
        # Use pandas with the SQLAlchemy engine directly
        df = pd.read_sql(query, engine, params=params)
        return df
    except Exception as e:
        st.error(f"Database Query Error: {e}")
        return pd.DataFrame()

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
        # Updated to width='stretch' to clear deprecation warning
        st.plotly_chart(fig, width='stretch')

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
            WHERE shipment_id = %(search_id)s ORDER BY timestamp DESC
        """
        # SQLAlchemy requires dicts for parameters
        track_df = run_query(track_query, params={"search_id": search_id})
        if not track_df.empty:
            st.success(f"Tracking Details Found for {search_id}")
            # Updated to width='stretch'
            st.dataframe(track_df, width='stretch')
        else:
            st.warning("No shipment/logs found with that tracking ID.")
            
    st.markdown("---")
    st.markdown("#### Filter Shipments Dataset")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    status_options = ["All"] + run_query("SELECT DISTINCT status FROM shipments")['status'].tolist()
    status_filter = col1.selectbox("Status", status_options)
    
    origin_filter = col2.text_input("Origin City:")
    dest_filter = col3.text_input("Destination City:")
    
    couriers = run_query("SELECT courier_id, name FROM courier_staff")
    courier_dict = dict(zip(couriers['name'], couriers['courier_id'])) if not couriers.empty else {}
    courier_options = ["All"] + list(couriers['name']) if not couriers.empty else ["All"]
    courier_filter = col4.selectbox("Courier", courier_options)
    
    dates = col5.date_input("Order Date Range", value=None)
    
    filter_query = "SELECT * FROM shipments WHERE 1=1"
    params = {}
    
    if status_filter != "All":
        filter_query += " AND status = %(status)s"
        params["status"] = status_filter
    if origin_filter:
        filter_query += " AND origin LIKE %(orig)s"
        params["orig"] = f"%{origin_filter}%"
    if dest_filter:
        filter_query += " AND destination LIKE %(dest)s"
        params["dest"] = f"%{dest_filter}%"
    if courier_filter != "All":
        filter_query += " AND courier_id = %(courier)s"
        params["courier"] = courier_dict[courier_filter]
    if dates and len(dates) == 2:
        filter_query += " AND order_date >= %(start)s AND order_date <= %(end)s"
        params["start"] = dates[0]
        params["end"] = dates[1]
        
    filter_query += " LIMIT 100"
    
    results_df = run_query(filter_query, params)
    # Updated to width='stretch'
    st.dataframe(results_df, width='stretch')

# -------------------------------------------------------------
# VIEW 3: ANALYTICAL DEEP DIVES
# -------------------------------------------------------------
elif choice == "Analytical Deep Dives":
    st.subheader("📈 Operational Analytics & Business Intelligence")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "1️⃣ Delivery Routes", 
        "2️⃣ Courier Strategy", 
        "3️⃣ Cost Analytics",
        "4️⃣ Cancellation Analysis",
        "5️⃣ Warehouse Insights"
    ])
    
    # ----------------- TAB 1: DELIVERY PERFORMANCE -----------------
    with tab1:
        st.markdown("### Route Bottlenecks vs Delays")
        route_query = """
            SELECT 
                r.route_id, 
                CONCAT(r.origin, ' -> ', r.destination) as route_name,
                r.distance_km,
                r.avg_time_hours as expected_hours,
                AVG(DATEDIFF(s.delivery_date, s.order_date) * 24) as actual_avg_hours
            FROM routes r
            JOIN shipments s ON r.origin = s.origin AND r.destination = s.destination
            WHERE s.status = 'Delivered'
            GROUP BY r.route_id, r.origin, r.destination, r.distance_km, r.avg_time_hours
            HAVING COUNT(s.shipment_id) > 5
            ORDER BY actual_avg_hours DESC
            LIMIT 30
        """
        route_df = run_query(route_query)
        if not route_df.empty:
            fig = px.scatter(
                route_df, x="distance_km", y="actual_avg_hours", 
                color="actual_avg_hours", color_continuous_scale="Reds", size="expected_hours",
                hover_name="route_name",
                labels={"distance_km": "Distance (Kilometers)", "actual_avg_hours": "Actual Travel Time (Hours)"},
                title="Actual Route Hours vs Net Distance (Highlighting Bottlenecks)"
            )
            fig.update_layout(hoverlabel=dict(bgcolor="white", font_color="black"))
            st.plotly_chart(fig, width='stretch')

    # ----------------- TAB 2: COURIER STRATEGY -----------------
    with tab2:
        st.markdown("### Courier Performance & Impact")
        courier_query = """
            SELECT 
                c.name,
                c.rating,
                c.vehicle_type,
                COUNT(s.shipment_id) as total_shipments,
                AVG(DATEDIFF(s.delivery_date, s.order_date)) as avg_delivery_time_days
            FROM courier_staff c
            JOIN shipments s ON c.courier_id = s.courier_id
            WHERE s.status = 'Delivered'
            GROUP BY c.courier_id, c.name, c.rating, c.vehicle_type
            ORDER BY total_shipments DESC
            LIMIT 50
        """
        courier_df = run_query(courier_query)
        if not courier_df.empty:
            colA, colB = st.columns(2)
            fig1 = px.bar(
                courier_df.head(15), x="name", y="total_shipments", color="vehicle_type", 
                title="Top 15 Couriers by Volume Handled"
            )
            colA.plotly_chart(fig1, width='stretch')
            
            fig2 = px.scatter(
                courier_df, x="rating", y="avg_delivery_time_days", color="vehicle_type",
                title="Courier Rating vs. Avg Delivery Time"
            )
            colB.plotly_chart(fig2, width='stretch')

    # ----------------- TAB 3: COST ANALYTICS -----------------
    with tab3:
        st.markdown("### Cost Diagnostics & Drivers")
        colA, colB = st.columns(2)
        
        cost_query = """
            SELECT 
                SUM(fuel_cost) as Total_Fuel, 
                SUM(labor_cost) as Total_Labor, 
                SUM(misc_cost) as Total_Misc 
            FROM costs
        """
        cost_df = run_query(cost_query)
        if not cost_df.empty:
            melted_df = pd.DataFrame({
                'Cost Component': ['Fuel', 'Labor', 'Misc'],
                'Expenses ($)': [cost_df.iloc[0]['Total_Fuel'], cost_df.iloc[0]['Total_Labor'], cost_df.iloc[0]['Total_Misc']]
            })
            fig1 = px.pie(melted_df, values='Expenses ($)', names='Cost Component', title='Expense Weight Contribution Percentage')
            colA.plotly_chart(fig1, width='stretch')
            
        weight_query = """
            SELECT 
                s.weight, 
                (c.fuel_cost + c.labor_cost + c.misc_cost) as total_cost,
                s.status
            FROM shipments s
            JOIN costs c ON s.shipment_id = c.shipment_id
            LIMIT 2000
        """
        weight_df = run_query(weight_query)
        if not weight_df.empty:
            fig2 = px.scatter(
                weight_df, x="weight", y="total_cost", color="status", opacity=0.6,
                title="Shipment Weight vs. Total Operational Cost"
            )
            colB.plotly_chart(fig2, width='stretch')
            
        st.markdown("#### Top 10 Most Expensive Shipments")
        expensive_query = """
            SELECT 
                s.shipment_id, s.origin, s.destination, s.weight, 
                (c.fuel_cost + c.labor_cost + c.misc_cost) as total_cost
            FROM shipments s
            JOIN costs c ON s.shipment_id = c.shipment_id
            ORDER BY total_cost DESC
            LIMIT 10
        """
        st.dataframe(run_query(expensive_query), width='stretch')

    # ----------------- TAB 4: CANCELLATION ANALYSIS -----------------
    with tab4:
        st.markdown("### Cancellation Patterns")
        
        colA, colB = st.columns(2)
        
        cancel_origin_query = """
            SELECT 
                origin, 
                COUNT(shipment_id) as total_shipments,
                SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(shipment_id) * 100 as cancellation_rate
            FROM shipments
            GROUP BY origin
            HAVING total_shipments > 50
            ORDER BY cancellation_rate DESC
            LIMIT 10
        """
        cancel_df = run_query(cancel_origin_query)
        if not cancel_df.empty:
            fig1 = px.bar(
                cancel_df, x="origin", y="cancellation_rate", text_auto='.1f',
                title="Top 10 Origin Cities by Cancellation Rate %", color="cancellation_rate", color_continuous_scale="Reds"
            )
            colA.plotly_chart(fig1, width='stretch')
            
        # Time-to-cancellation analysis
        time_query = """
            SELECT 
                DATEDIFF(t.timestamp, s.order_date) as days_to_cancel
            FROM shipments s
            JOIN shipment_tracking t ON s.shipment_id = t.shipment_id
            WHERE s.status = 'Cancelled' AND t.status = 'Cancelled'
        """
        time_df = run_query(time_query)
        if not time_df.empty:
            fig2 = px.histogram(
                time_df, x="days_to_cancel", nbins=20, 
                title="Time-to-Cancellation Analysis (Days)", color_discrete_sequence=['indianred']
            )
            colB.plotly_chart(fig2, width='stretch')

    # ----------------- TAB 5: WAREHOUSE INSIGHTS -----------------
    with tab5:
        st.markdown("### Warehouse Infrastructure")
        wh_query = "SELECT warehouse_id, city, state, capacity FROM warehouses ORDER BY capacity DESC"
        full_wh_df = run_query(wh_query)
        
        if not full_wh_df.empty:
            colA, colB = st.columns([1, 2])
            colA.dataframe(full_wh_df, width='stretch')
            
            fig = px.treemap(
                full_wh_df, path=[px.Constant("All States"), 'state', 'city'], values='capacity',
                title="Warehouse Capacity Distribution by State & City"
            )
            colB.plotly_chart(fig, width='stretch')
