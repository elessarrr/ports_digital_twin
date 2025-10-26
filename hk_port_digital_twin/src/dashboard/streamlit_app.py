import sys
import os
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

import time
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logging
import numpy as np
import simpy
import threading

from hk_port_digital_twin.src.utils.file_watcher import start_file_watcher
from hk_port_digital_twin.src.utils.redis_utils import get_redis_connection

from hk_port_digital_twin.src.utils.data_pipeline import DataPipeline
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
from hk_port_digital_twin.src.dashboard.performance_dashboard import render_performance_dashboard
from hk_port_digital_twin.src.dashboard.utils.performance_monitor import PerformanceMonitor
from hk_port_digital_twin.src.dashboard.quick_demo import run_quick_demo

# Tab configuration
from hk_port_digital_twin.src.dashboard.tabs.berth_tab import render as render_berth_tab
from hk_port_digital_twin.src.dashboard.tabs.cargo_tab import render as render_cargo_tab
from hk_port_digital_twin.src.dashboard.tabs.vessel_tab import render as render_vessel_tab

def render_overview_tab():
    st.subheader("🚢 Port Overview")
    
    col1, col2 = st.columns(2)

    with col1:
        with st.expander("KPI Summary", expanded=True):
            kpi_col1, kpi_col2 = st.columns(2)
            with kpi_col1:
                st.metric("Vessels in Port", "85", delta="-5%", help="Total number of vessels currently within the port area, including those at berth and at anchorage.")
                st.metric("Avg. Turnaround Time", "18h", delta="-1h", help="The average time it takes for a vessel to arrive, unload/load, and depart from the port.")
            with kpi_col2:
                st.metric("Berth Utilization", "92%", delta="3%", help="The percentage of berths that are currently occupied by vessels.")
                st.metric("Cargo Throughput (TEUs)", "1.2M", delta="8%", help="The total volume of cargo, measured in Twenty-foot Equivalent Units (TEUs), that has been processed this month.")

    with col2:
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

from hk_port_digital_twin.src.dashboard.documentation_tab import render_documentation_tab

TABS = {
    "Overview": render_overview_tab,
    "Berth Planning": render_berth_tab,
    "Cargo Statistics": render_cargo_tab,
    "Vessel Analytics": render_vessel_tab,
    "Scenarios": render_consolidated_scenarios_tab,
    "Performance Dashboard": render_performance_dashboard,
    "Documentation": render_documentation_tab,
}

@st.cache_data
def load_data():
    """Loads all the data needed for the app."""
    data_pipeline = DataPipeline(data_path="./data")
    return data_pipeline.run()

def main():
    """Main function to run the Streamlit application."""
    st.set_page_config(layout="wide")

    # --- HEADER ---
    # st.image(os.path.join(os.path.dirname(__file__), "logo.png"), width=100)
    st.title("Hong Kong Port Digital Twin")
    st.subheader("A Real-Time Simulation and Analytics Platform")

    # Load data
    data = load_data()

    with st.sidebar:
        st.title("MENU")
        selected_tab = st.radio(
            " ",
            [
                "Overview",
                "Berth Planning",
                "Vessel Analytics",
                "Cargo Statistics",
                "Scenarios",
                "Performance Dashboard",
                "Documentation",
            ],
            help="Select a tab to view different aspects of the port digital twin."
        )

        if st.button("🚀 Quick Demo"):
            run_quick_demo()

        st.title("Settings")
        debug_mode = st.checkbox("Enable Debug Mode", help="Enable this to see performance metrics and other debugging information.")

    # Get tab from query params
    query_params = st.experimental_get_query_params()
    if "tab" in query_params:
        selected_tab = query_params["tab"][0]

    # Render the selected tab
    if selected_tab in TABS:
        if debug_mode:
            monitor = PerformanceMonitor()
            monitor.track_memory_usage(selected_tab)
            TABS[selected_tab]()
            monitor.generate_report()
        else:
            TABS[selected_tab]()

    # Add a placeholder for real-time updates
    # st.toast("New vessel data arrived!", icon="🚢")


def subscribe_to_vessel_updates():
    redis_conn = get_redis_connection()
    pubsub = redis_conn.pubsub()
    pubsub.subscribe("vessel_updates")
    logging.info("Subscribed to vessel_updates channel.")
    for message in pubsub.listen():
        if message['type'] == 'message':
            logging.info(f"Received message: {message['data']}")
            st.toast("New vessel data arrived!", icon="🚢")
            st.experimental_rerun()

@st.cache_resource
def start_background_watcher():
    data_directory = Path(project_root) / "data" / "vessel_arrivals"
    thread = threading.Thread(target=start_file_watcher, args=(data_directory,), daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    start_background_watcher()
    main()
    subscribe_to_vessel_updates() # This will block and listen for messages