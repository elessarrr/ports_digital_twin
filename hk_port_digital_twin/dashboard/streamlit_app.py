import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

def find_project_root(marker_name='hk_port_digital_twin'):
    """Find the project root by searching for a marker directory."""
    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if (parent / marker_name).is_dir():
            # Check if we are inside the marker directory, if so, go one level up
            if parent.name == marker_name:
                return str(parent.parent)
            return str(parent)
    raise FileNotFoundError(f"Project root not found. Could not find a directory containing '{marker_name}'.")


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
from dotenv import load_dotenv

# from hk_port_digital_twin.utils.file_watcher import start_file_watcher
# from hk_port_digital_twin.utils.redis_utils import get_redis_connection

from hk_port_digital_twin.utils.data_pipeline import DataPipeline
from hk_port_digital_twin.config.settings import SIMULATION_CONFIG, get_enhanced_simulation_config
from hk_port_digital_twin.core.port_simulation import PortSimulation
from hk_port_digital_twin.core.simulation_controller import SimulationController
from hk_port_digital_twin.core.berth_manager import BerthManager
from hk_port_digital_twin.scenarios import ScenarioManager, list_available_scenarios
from hk_port_digital_twin.utils.visualization import create_kpi_summary_chart, create_port_layout_chart, create_ship_queue_chart, create_berth_utilization_chart, create_throughput_timeline, create_waiting_time_distribution
# Weather integration disabled for feature removal
# from hk_port_digital_twin.utils.weather_integration import HKObservatoryIntegration
HKObservatoryIntegration = None  # Disabled
from hk_port_digital_twin.utils.data_loader import load_focused_cargo_statistics, get_enhanced_cargo_analysis, get_time_series_data
from hk_port_digital_twin.dashboard.scenario_tab_consolidation_refactored import ConsolidatedScenariosTab
from hk_port_digital_twin.dashboard.vessel_charts import render_vessel_analytics_dashboard
from hk_port_digital_twin.dashboard.executive_dashboard import ExecutiveDashboard
from hk_port_digital_twin.analysis.roi_calculator import render_roi_calculator
from hk_port_digital_twin.dashboard import guided_tour
from hk_port_digital_twin.utils.strategic_visualization import StrategicVisualization, render_strategic_controls
from hk_port_digital_twin.dashboard.performance_dashboard import render_performance_dashboard
from hk_port_digital_twin.dashboard.utils.performance_monitor import PerformanceMonitor
from hk_port_digital_twin.dashboard.quick_demo import run_quick_demo

from hk_port_digital_twin.utils.vessel_data_fetcher import VesselDataFetcher
from hk_port_digital_twin.utils.vessel_data_scheduler import VesselDataScheduler
from hk_port_digital_twin.utils.marine_traffic_fetcher import MarineTrafficFetcher
from hk_port_digital_twin.dashboard.utils.background_processor import BackgroundProcessor
from hk_port_digital_twin.dashboard.utils.real_time_updater import RealTimeUpdater

# Tab configuration
from hk_port_digital_twin.dashboard.tabs.berth_tab import render as render_berth_tab
from hk_port_digital_twin.dashboard.tabs.cargo_tab import render as render_cargo_tab
from hk_port_digital_twin.dashboard.tabs.vessel_tab import render as render_vessel_tab

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

from hk_port_digital_twin.dashboard.documentation_tab import render_documentation_tab

TABS = {
    "Overview": render_overview_tab,
    "Berth Planning": render_berth_tab,
    "Cargo Statistics": render_cargo_tab,
    "Vessel Analytics": render_vessel_tab,
    "Scenarios": ConsolidatedScenariosTab().render,
    "Performance Dashboard": render_performance_dashboard,
    "Documentation": render_documentation_tab,
}

@st.cache_data
def load_data():
    """Loads all the data needed for the app."""
    data_path = os.path.join(project_root, "data", "vessel_arrivals")
    pipeline = DataPipeline(data_path)
    return pipeline.run()

def on_message(message):
    """Callback function to handle received messages."""
    logging.info(f"Received message: {message}")
    try:
        # Attempt to rerun the app
        st.rerun()
        logging.info("Successfully triggered st.rerun()")
    except Exception as e:
        logging.error(f"Failed to trigger st.rerun(): {e}", exc_info=True)

def main():
    """Main function to run the Streamlit application."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Executing main function...")

    # Use session state to ensure threads are started only once
    if 'threads_started' not in st.session_state:
        logging.info("Initializing background threads...")
        st.session_state.bg_processor = BackgroundProcessor()
        st.session_state.data_load_task_id = st.session_state.bg_processor.add_task(load_data)
        # start_redis_subscription_thread("vessel_updates", on_message)
        # start_background_watcher()
        st.session_state.threads_started = True
        logging.info("Background threads initialized.")
    else:
        logging.info("Background threads already running.")


    st.set_page_config(page_title="Hong Kong Port Digital Twin", layout="wide")

    st.title("Hong Kong Port Digital Twin")
    st.subheader("A Real-Time Simulation and Analytics Platform")

    # Load data
    data_load_result = st.session_state.bg_processor.get_result(st.session_state.data_load_task_id)

    if not data_load_result or data_load_result['status'] == 'pending':
        with st.spinner('Loading data...'):
            while not data_load_result or data_load_result['status'] == 'pending':
                time.sleep(1)
                data_load_result = st.session_state.bg_processor.get_result(st.session_state.data_load_task_id)

    if data_load_result['status'] == 'failed':
        st.error(f"Failed to load data: {data_load_result['error']}")
        return

    data = data_load_result['result']


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
            help="Select a tab to view different aspects of the port digital twin.",
            key="main_menu"
        )

        if st.button("🚀 Quick Demo"):
            run_quick_demo()

        st.title("Settings")
        debug_mode = st.checkbox("Enable Debug Mode", help="Enable this to see performance metrics and other debugging information.")

    # Get tab from query params
    query_params = st.query_params
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
    updater = RealTimeUpdater(update_interval=10)
    updater.run()

def _subscribe_to_channel(channel_name: str, callback):
    """Generic function to subscribe to a Redis channel and trigger a callback."""
    logging.info(f"Attempting to subscribe to Redis channel: {channel_name}")
    try:
        redis_host = os.environ.get("REDIS_HOST", "localhost")
        redis_port = int(os.environ.get("REDIS_PORT", 6379))
        redis_conn = get_redis_connection(host=redis_host, port=redis_port)
        pubsub = redis_conn.pubsub()
        pubsub.subscribe(channel_name)
        logging.info(f"Subscribed to {channel_name} channel.")
        while True:
            message = pubsub.get_message()
            if message and message["type"] == "message":
                logging.info(f"Received message on {channel_name}: {message['data']}")
                callback(message['data'])
            time.sleep(0.1)  # Prevent busy-waiting
    except Exception as e:
        logging.error(f"Failed to subscribe or listen to Redis channel {channel_name}: {e}", exc_info=True)

def start_redis_subscription_thread(channel_name: str, callback):
    """Starts a background thread to listen to a Redis channel."""
    logging.info(f"Starting Redis subscription thread for channel: {channel_name}")
    thread = threading.Thread(target=_subscribe_to_channel, args=(channel_name, callback), daemon=True)
    thread.start()
    logging.info(f"Redis subscription thread started for channel: {channel_name}")
    return thread

def start_background_watcher():
    # data_directory = Path(project_root) / "data" / "vessel_arrivals"
    # thread = threading.Thread(target=start_file_watcher, args=(data_directory,), daemon=True)
    # thread.start()
    # return thread
    pass

def initialize_data_pipeline():
    """Initializes and starts the data pipeline scheduler."""
    vessel_data_fetcher = VesselDataFetcher()
    marine_traffic_fetcher = MarineTrafficFetcher()
    
    scheduler = VesselDataScheduler(
        fetcher_callback=vessel_data_fetcher.fetch_xml_files,
        marine_traffic_fetcher_callback=marine_traffic_fetcher.fetch_data
    )
    
    scheduler.start()
    return scheduler

if __name__ == "__main__":
    main()