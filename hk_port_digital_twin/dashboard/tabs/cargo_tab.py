import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def _get_past_date(days_ago):
    return datetime.now() - timedelta(days=days_ago)

def _generate_time_series_data(days=365):
    dates = [_get_past_date(i) for i in range(days)][::-1]
    shipments = np.random.randint(50, 200, size=days) + np.sin(np.arange(days) / 50) * 20
    return pd.DataFrame({"Date": dates, "Number of Shipments": shipments})

def _render_forecasting_analysis():
    st.subheader("🔮 Forecasting Analysis")
    st.write("Predictive analytics for future cargo trends.")
    
    # Placeholder for forecasting model
    forecast_days = st.slider("Select number of days to forecast", 30, 365, 90)
    
    # Generate dummy forecast data
    last_date = datetime.now()
    future_dates = [last_date + timedelta(days=i) for i in range(forecast_days)]
    
    # Simple forecasting model (e.g., moving average + noise)
    base_shipments = np.random.randint(100, 150, size=forecast_days)
    seasonality = np.sin(np.arange(forecast_days) / 30) * 30
    forecasted_shipments = base_shipments + seasonality
    
    forecast_df = pd.DataFrame({
        "Date": future_dates,
        "Forecasted Shipments": forecasted_shipments
    })
    
    fig = px.line(forecast_df, x='Date', y='Forecasted Shipments', title="Shipment Forecast")
    st.plotly_chart(fig, use_container_width=True)

def _render_cargo_types_analysis():
    st.subheader("📦 Cargo Types Analysis")
    st.write("Breakdown of different cargo types.")
    
    # Dummy data for cargo types
    cargo_types = ['Electronics', 'Apparel', 'Machinery', 'Chemicals', 'Food Products', 'Other']
    volumes = np.random.randint(10000, 50000, size=len(cargo_types))
    
    df = pd.DataFrame({'Cargo Type': cargo_types, 'Volume (TEUs)': volumes})
    
    fig = px.pie(df, names='Cargo Type', values='Volume (TEUs)', title="Cargo Volume by Type")
    st.plotly_chart(fig, use_container_width=True)

def render():
    st.markdown("### 📦 Cargo Analysis")
    st.markdown("Comprehensive analysis of cargo throughput data, including shipment types, transport modes, time series analysis, and forecasting.")
    
    _render_cargo_data_summary()
    
    cargo_tab1, cargo_tab2, cargo_tab3, cargo_tab4, cargo_tab5, cargo_tab6 = st.tabs([
        "📊 Shipment Types", "🚛 Transport Modes", "📈 Time Series", 
        "🔮 Forecasting", "📦 Cargo Types", "🌍 Locations"
    ])
    
    with cargo_tab1:
        _render_shipment_types_analysis()
        
    with cargo_tab2:
        _render_transport_modes_analysis()
        
    with cargo_tab3:
        _render_time_series_analysis()
        
    with cargo_tab4:
        _render_forecasting_analysis()
        
    with cargo_tab5:
        _render_cargo_types_analysis()
        
    with cargo_tab6:
        _render_locations_analysis()

def _render_cargo_data_summary():
    st.subheader("📊 Data Summary")
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        total_shipments = np.random.randint(15000, 25000)
        st.metric("Total Shipments", f"{total_shipments:,}")
        
    with summary_col2:
        total_teu = np.random.randint(800000, 1200000)
        st.metric("Total TEUs", f"{total_teu:,}")
        
    with summary_col3:
        avg_shipment_size = total_teu / total_shipments
        st.metric("Avg. Shipment Size (TEUs)", f"{avg_shipment_size:.2f}")
        
    with summary_col4:
        unique_destinations = np.random.randint(50, 150)
        st.metric("Unique Destinations", unique_destinations)

def _render_shipment_types_analysis():
    st.subheader("📊 Shipment Types Analysis")
    st.write("Analysis of Full Container Load (FCL) vs. Less than Container Load (LCL) shipments.")
    
    # Dummy data for FCL/LCL
    shipment_types = ['FCL', 'LCL']
    counts = [np.random.randint(10000, 20000), np.random.randint(3000, 8000)]
    
    df = pd.DataFrame({'Shipment Type': shipment_types, 'Count': counts})
    
    fig = px.bar(df, x='Shipment Type', y='Count', title="FCL vs. LCL Shipments")
    st.plotly_chart(fig, use_container_width=True)

def _render_transport_modes_analysis():
    st.subheader("🚛 Transport Modes Analysis")
    st.write("Distribution of cargo by transport mode (e.g., sea, air, land).")
    
    # Dummy data for transport modes
    modes = ['Sea', 'Air', 'Land']
    percentages = [75, 15, 10]
    
    df = pd.DataFrame({'Transport Mode': modes, 'Percentage': percentages})
    
    fig = px.pie(df, names='Transport Mode', values='Percentage', title="Cargo Distribution by Transport Mode")
    st.plotly_chart(fig, use_container_width=True)

def _render_time_series_analysis():
    st.subheader("📈 Time Series Analysis")
    st.write("Historical cargo shipment trends over time.")
    
    # Generate time series data
    df = _generate_time_series_data()
    
    fig = px.line(df, x='Date', y='Number of Shipments', title="Daily Shipments Over the Last Year")
    st.plotly_chart(fig, use_container_width=True)

def _render_locations_analysis():
    st.subheader("🌍 Locations Analysis")
    st.write("Analysis of cargo origins and destinations.")
    
    # Dummy data for locations
    locations = ['Shanghai', 'Singapore', 'Rotterdam', 'Los Angeles', 'Dubai', 'Other']
    imports = np.random.randint(5000, 20000, size=len(locations))
    exports = np.random.randint(5000, 20000, size=len(locations))
    
    df = pd.DataFrame({
        'Location': locations,
        'Imports (TEUs)': imports,
        'Exports (TEUs)': exports
    })
    
    st.dataframe(df.set_index('Location'))
    
    fig = px.bar(df, x='Location', y=['Imports (TEUs)', 'Exports (TEUs)'], title="Top Import/Export Locations", barmode='group')
    st.plotly_chart(fig, use_container_width=True)