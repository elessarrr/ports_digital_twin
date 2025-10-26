import sys
import os
import time
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logging
import numpy as np
import simpy

# Add the project root to the Python path to allow absolute imports
# Use Path for more robust path handling in cloud environments
from pathlib import Path

def find_project_root(marker_file='streamlit_app.py'):
    """Find the project root by searching for a marker file."""
    current_path = Path(__file__).resolve()
    # We are looking for the directory that contains both the marker_file and the 'hk_port_digital_twin' directory
    for parent in current_path.parents:
        if (parent / marker_file).exists() and (parent / 'hk_port_digital_twin').exists():
            return str(parent)
    # Fallback for environments where the structure might be different
    # This is a bit of a guess, but it's better than a hardcoded index.
    for parent in current_path.parents:
        if (parent / 'hk_port_digital_twin').exists():
            return str(parent)
    raise FileNotFoundError(f"Project root not found. Could not find a directory containing '{marker_file}' or 'hk_port_digital_twin'.")


project_root = find_project_root()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from hk_port_digital_twin.src.utils.data_loader import RealTimeDataConfig, get_real_time_manager, load_container_throughput, load_vessel_arrivals, load_berth_configurations, initialize_vessel_data_pipeline, load_all_vessel_data, get_comprehensive_vessel_analysis, load_combined_vessel_data, load_all_vessel_data_with_backups
from hk_port_digital_twin.config.settings import SIMULATION_CONFIG, get_enhanced_simulation_config
from hk_port_digital_twin.src.core.port_simulation import PortSimulation
from hk_port_digital_twin.src.core.simulation_controller import SimulationController
from hk_port_digital_twin.src.core.berth_manager import BerthManager
from hk_port_digital_twin.src.scenarios import ScenarioManager, list_available_scenarios
from hk_port_digital_twin.src.utils.visualization import create_kpi_summary_chart, create_port_layout_chart, create_ship_queue_chart, create_berth_utilization_chart, create_throughput_timeline, create_waiting_time_distribution
# Weather integration disabled for feature removal
# from hk_port_digital_twin.src.utils.weather_integration import HKObservatoryIntegration
HKObservatoryIntegration = None  # Disabled
from hk_port_digital_twin.src.utils.data_loader import load_focused_cargo_statistics, get_enhanced_cargo_analysis, get_time_series_data
from hk_port_digital_twin.src.dashboard.scenario_tab_consolidation_refactored import render_consolidated_scenarios_tab
from hk_port_digital_twin.src.dashboard.vessel_charts import render_vessel_analytics_dashboard
from hk_port_digital_twin.src.dashboard.executive_dashboard import ExecutiveDashboard
from hk_port_digital_twin.src.analysis.roi_calculator import render_roi_calculator
from hk_port_digital_twin.src.dashboard import guided_tour
from hk_port_digital_twin.src.utils.strategic_visualization import StrategicVisualization, render_strategic_controls

# Tab configuration
from .tabs.berth_tab import render as render_berth_tab
from .tabs.cargo_tab import render as render_cargo_tab
from .tabs.vessel_tab import render as render_vessel_tab

def render_overview_tab():
    st.subheader("🚢 Port Overview")
    
    with st.expander("KPI Summary", expanded=True):
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        with kpi_col1:
            st.metric("Vessels in Port", "85", delta="-5%", help="Total vessels currently at berth or anchorage")
        with kpi_col2:
            st.metric("Berth Utilization", "92%", delta="3%", help="Percentage of berths currently occupied")
        with kpi_col3:
            st.metric("Avg. Turnaround Time", "18h", delta="-1h", help="Average time from arrival to departure")
        with kpi_col4:
            st.metric("Cargo Throughput (TEUs)", "1.2M", delta="8%", help="Total Twenty-foot Equivalent Units processed this month")

    # ROI Calculator
    render_roi_calculator()


def render_cargo_statistics_tab():
    st.subheader("📊 Cargo Statistics")
    st.write("Cargo statistics content will be added here.")


def render_vessel_insights_tab():
    st.subheader("⚓ Vessel Insights")
    st.write("Vessel insights content will be added here.")


def render_scenarios_tab():
    """Renders the scenarios tab."""
    st.subheader("⚙️ Scenarios")
    st.write("Content for scenarios will be added here.")

def render_settings_tab():
    """Renders the settings tab."""
    st.subheader("🔧 Settings")
    st.write("Content for settings will be added here.")

TABS = {
    "Overview": render_overview_tab,
    "Berth Planning": render_berth_tab,
    "Cargo Statistics": render_cargo_tab,
    "Vessel Analytics": render_vessel_tab,
    "Scenarios": render_consolidated_scenarios_tab,
}

def main():
    """Main function to run the Streamlit application."""
    st.title("🚢 Hong Kong Port Digital Twin")

    with st.sidebar:
        st.title("Navigation")
        selected_tab = st.radio("Go to", list(TABS.keys()))

    # Render the selected tab
    if selected_tab in TABS:
        TABS[selected_tab]()

if __name__ == "__main__":
    main()