import streamlit as st
import plotly.express as px
from ...utils.data_loader import load_container_throughput, get_enhanced_cargo_analysis

def render_interactive_charts():
    """
    Renders interactive charts for container throughput and cargo analysis.

    This function loads relevant data and uses Plotly to generate and display:
    - A line chart for monthly container throughput (Total, Seaborne, River).
    - A bar chart comparing different shipment and transport types based on trend analysis.
    """
    st.subheader("Interactive Data Charts")

    # Load data
    container_throughput = load_container_throughput()
    enhanced_analysis = get_enhanced_cargo_analysis()

    if not container_throughput.empty:
        st.write("#### Monthly Container Throughput")
        fig = px.line(
            container_throughput.reset_index(), 
            x='Date', 
            y=['total_teus', 'seaborne_teus', 'river_teus'],
            title="Container Throughput Over Time",
            labels={'value': 'Throughput (x1000 TEUs)', 'variable': 'Transport Mode'}
        )
        st.plotly_chart(fig, use_container_width=True)

    if enhanced_analysis and 'time_series_data' in enhanced_analysis:
        st.write("#### Cargo Analysis")
        
        shipment_types = enhanced_analysis['time_series_data'].get('shipment_types')
        
        if shipment_types is not None:
            st.write("##### Shipment Type Trends")
            fig2 = px.bar(
                shipment_types.reset_index(),
                x='Year',
                y=shipment_types.columns,
                title="Shipment Types Over Time",
                labels={'value': 'Tonnes', 'variable': 'Shipment Type'}
            )
            st.plotly_chart(fig2, use_container_width=True)