import streamlit as st
from ..components.executive_summary import render_executive_summary
from ..components.interactive_charts import render_interactive_charts
from ..components.data_table_view import render_data_table
from ..components.layout import LayoutManager


class MonitoringPage:
    """Renders the main monitoring page of the dashboard."""

    def render(self, data, theme_manager):
        """Render the monitoring page layout and components."""
        # Section: Executive Summary
        with LayoutManager.create_card("Executive Summary"):
            render_executive_summary(data)

        LayoutManager.add_spacing("lg")

        # Section: Throughput Analysis
        with LayoutManager.create_card("Throughput Analysis"):
            render_interactive_charts(data, theme_manager)

        LayoutManager.add_spacing("lg")

        # Section: Detailed Analysis
        with LayoutManager.create_card("Detailed Analysis"):
            render_data_table(data.get('enhanced_analysis'))