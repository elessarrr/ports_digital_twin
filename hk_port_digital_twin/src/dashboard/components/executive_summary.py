import streamlit as st
import pandas as pd

def render_executive_summary(data):
    """
    Renders the executive summary view with key performance indicators.
    """
    st.header("Executive Summary")
    st.markdown("High-level overview of port performance and key metrics.")

    container_throughput = data.get('container_throughput')
    enhanced_analysis = data.get('enhanced_analysis')

    if container_throughput is not None and not container_throughput.empty:
        latest_data = container_throughput.iloc[-1]
        
        col1, col2, col3 = st.columns(3)

        # KPI: Total Container Throughput
        total_teus = latest_data.get('total_teus', 0)
        yoy_change = latest_data.get('total_yoy_change', 0)
        col1.metric(
            label="Total Container Throughput (x1000 TEUs)",
            value=f"{total_teus:,.0f}",
            delta=f"{yoy_change:.2f}% vs Previous Year"
        )

        # KPI: Seaborne vs. River
        seaborne_teus = latest_data.get('seaborne_teus', 0)
        river_teus = latest_data.get('river_teus', 0)
        col2.metric(
            label="Seaborne Throughput (x1000 TEUs)",
            value=f"{seaborne_teus:,.0f}",
            delta=f"{latest_data.get('seaborne_yoy_change', 0):.2f}%"
        )
        col3.metric(
            label="River Throughput (x1000 TEUs)",
            value=f"{river_teus:,.0f}",
            delta=f"{latest_data.get('river_yoy_change', 0):.2f}%"
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

    st.markdown("---")