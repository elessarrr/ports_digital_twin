import streamlit as st
import plotly.express as px
from typing import Dict, Any
from ..styles.theme_manager import ThemeManager

def render_interactive_charts(data: Dict[str, Any], theme_manager: ThemeManager):
    """
    Renders interactive charts for container throughput and shipment analysis.
    
    Args:
        data (Dict[str, Any]): A dictionary containing data for the charts.
        theme_manager (ThemeManager): An instance of the ThemeManager to handle chart styling.
    """
    
    st.header("Container Throughput and Shipment Analysis")
    
    chart_colors = theme_manager.get_chart_colors()
    
    # Monthly Container Throughput (TEUs)
    if "container_throughput" in data and not data["container_throughput"].empty:
        fig_line = px.line(
            data["container_throughput"],
            x="month",
            y="total_teus",
            title="Monthly Container Throughput (TEUs)",
            labels={"month": "Month", "total_teus": "Total TEUs"},
            color_discrete_sequence=[chart_colors[0]]
        )
        fig_line.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme_manager.get_theme_colors()['text_primary']
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.warning("Container throughput data is not available.")

    # Shipment Type Trend
    if "enhanced_analysis" in data and not data["enhanced_analysis"].empty:
        fig_bar = px.bar(
            data["enhanced_analysis"],
            x="month",
            y="shipment_count",
            color="shipment_type",
            title="Shipment Type Trend",
            labels={"month": "Month", "shipment_count": "Number of Shipments"},
            color_discrete_sequence=chart_colors[1:]
        )
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color=theme_manager.get_theme_colors()['text_primary'],
            legend_title_text='Shipment Type'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("Shipment analysis data is not available.")