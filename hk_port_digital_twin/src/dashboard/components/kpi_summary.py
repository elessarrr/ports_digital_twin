import streamlit as st
import pandas as pd
from ...utils.data_loader import load_container_throughput, get_enhanced_cargo_analysis

def render_kpi_summary():
    """
    Renders a summary of Key Performance Indicators (KPIs).

    This function loads container throughput data and enhanced cargo analysis 
    to display critical metrics such as total container throughput, year-over-year 
    growth, and trend analysis for different cargo types. It is designed to 
    provide a high-level overview of the port's performance on the main dashboard.
    """
    st.subheader("Key Performance Indicators")

    # Load data
    container_throughput = load_container_throughput()
    enhanced_analysis = get_enhanced_cargo_analysis()

    if not container_throughput.empty:
        latest_data = container_throughput.iloc[-1]
        previous_data = container_throughput.iloc[-2]

        col1, col2, col3 = st.columns(3)

        # KPI: Total Container Throughput
        total_teus = latest_data['total_teus']
        yoy_change = latest_data['total_yoy_change']
        col1.metric(
            label="Total Container Throughput (x1000 TEUs)",
            value=f"{total_teus:,.0f}",
            delta=f"{yoy_change:.2f}% vs Previous Year"
        )

        # KPI: Seaborne vs. River
        seaborne_teus = latest_data['seaborne_teus']
        river_teus = latest_data['river_teus']
        col2.metric(
            label="Seaborne Throughput (x1000 TEUs)",
            value=f"{seaborne_teus:,.0f}",
            delta=f"{latest_data['seaborne_yoy_change']:.2f}%"
        )
        col3.metric(
            label="River Throughput (x1000 TEUs)",
            value=f"{river_teus:,.0f}",
            delta=f"{latest_data['river_yoy_change']:.2f}%"
        )

    if enhanced_analysis and 'trend_analysis' in enhanced_analysis:
        st.markdown("---")
        st.write("#### Cargo Trend Analysis")
        
        trends = enhanced_analysis['trend_analysis']
        
        if 'shipment_types' in trends:
            shipment_trends = trends['shipment_types']
            
            # Display trends for key shipment types
            direct_shipment_trend = shipment_trends.get('Direct shipment', {})
            transhipment_trend = shipment_trends.get('Transhipment', {})

            col1, col2 = st.columns(2)

            if direct_shipment_trend:
                col1.info(f"""
                **Direct Shipments:**
                - Trend: {direct_shipment_trend.get('trend_direction', 'N/A')}
                - CAGR: {direct_shipment_trend.get('cagr', 0):.2f}%
                """)

            if transhipment_trend:
                col2.success(f"""
                **Transhipments:**
                - Trend: {transhipment_trend.get('trend_direction', 'N/A')}
                - CAGR: {transhipment_trend.get('cagr', 0):.2f}%
                """)