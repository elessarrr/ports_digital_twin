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

from hk_port_digital_twin.utils.data_loader import RealTimeDataConfig, get_real_time_manager, load_container_throughput, load_vessel_arrivals, load_berth_configurations, initialize_vessel_data_pipeline, load_all_vessel_data, get_comprehensive_vessel_analysis, load_combined_vessel_data, load_all_vessel_data_with_backups
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
from hk_port_digital_twin.core.strategic_simulation_controller import StrategicSimulationController
from hk_port_digital_twin.utils.scenario_aware_calculator import ScenarioAwareCalculator, ValueType, ScenarioType
from hk_port_digital_twin.analysis.roi_calculator import render_roi_calculator
from hk_port_digital_twin.utils.scenario_helpers import get_wait_time_scenario_name
from hk_port_digital_twin.dashboard.utils.debouncing import DebounceManager
from hk_port_digital_twin.dashboard.utils.session_state_manager import SessionStateManager
from hk_port_digital_twin.dashboard.utils.rendering_optimization import optimized_computation

try:
    from hk_port_digital_twin.utils.wait_time_calculator import WaitTimeCalculator, calculate_wait_time
except (ImportError, NameError, AttributeError) as e:
    # This allows the app to run even if the wait time calculator is not available
    # The dashboard will gracefully degrade by hiding wait time-related features
    # This is a robust way to handle optional dependencies
    WaitTimeCalculator = None
    calculate_wait_time = None
    st.sidebar.warning(f"Wait time calculator not available. Features disabled. Error: {e}")

# Function to load and apply custom CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title="Hong Kong Port Digital Twin",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
css_path = os.path.join(os.path.dirname(__file__), "style.css")
load_css(css_path)
# from hk_port_digital_twin.dashboard.unified_simulations_tab import UnifiedSimulationsTab  # Commented out - tab hidden

try:
    from hk_port_digital_twin.dashboard.marine_traffic_integration import MarineTrafficIntegration
except ImportError:
    MarineTrafficIntegration = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(threadName)s - %(message)s')


def get_scenario_display_name(scenario_key: str) -> str:
    """
    Get display name with emoji for a scenario.
    
    Args:
        scenario_key: The scenario key ('peak', 'normal', 'low')
        
    Returns:
        Display name with emoji (e.g., 'peak 🔥')
    """
    emoji_map = {
        'peak': '🔥',
        'normal': '✅', 
        'low': '📉'
    }
    emoji = emoji_map.get(scenario_key, '')
    return f"{scenario_key} {emoji}" if emoji else scenario_key

def get_scenario_key_from_display(display_name: str) -> str:
    """
    Extract scenario key from display name with emoji.
    
    Args:
        display_name: Display name with emoji (e.g., 'peak 🔥')
        
    Returns:
        Scenario key (e.g., 'peak')
    """
    # Remove emojis and extra spaces to get the key
    return display_name.split()[0].strip()



def filter_vessel_data_by_time_range(vessel_data: pd.DataFrame, time_range: str) -> pd.DataFrame:
    """Filter vessel data based on the selected time range.
    
    Args:
        vessel_data: DataFrame containing vessel data
        time_range: Time range string (e.g., 'Last 7 days', 'Last 1 year')
        
    Returns:
        Filtered DataFrame containing only vessels within the specified time range
    """
    if vessel_data.empty:
        return vessel_data
    
    # Determine the time column to use for filtering
    time_column = None
    if 'arrival_time' in vessel_data.columns:
        time_column = 'arrival_time'
    elif 'timestamp' in vessel_data.columns:
        time_column = 'timestamp'
    elif 'departure_time' in vessel_data.columns:
        time_column = 'departure_time'
    
    if time_column is None:
        # No time column found, return original data
        return vessel_data
    
    # Ensure the time column is in datetime format
    vessel_data[time_column] = pd.to_datetime(vessel_data[time_column], errors='coerce')
    
    # Calculate the cutoff date based on the time range
    now = datetime.now()
    
    if time_range == 'Last 7 days':
        cutoff_date = now - timedelta(days=7)
    elif time_range == 'Last 30 days':
        cutoff_date = now - timedelta(days=30)
    elif time_range == 'Last 90 days':
        cutoff_date = now - timedelta(days=90)
    elif time_range == 'Last 180 days':
        cutoff_date = now - timedelta(days=180)
    elif time_range == 'Last 1 year':
        cutoff_date = now - timedelta(days=365)
    elif time_range == 'Last 2 years':
        cutoff_date = now - timedelta(days=365*2)
    elif time_range == 'Last 3 years':
        cutoff_date = now - timedelta(days=365*3)
    else:
        # Unknown time range, return original data
        return vessel_data
    
    # Filter the data
    filtered_data = vessel_data[
        (vessel_data[time_column].notna()) & 
        (vessel_data[time_column] >= cutoff_date)
    ].copy()
    
    logging.info(f"Filtered vessel data: {len(vessel_data)} -> {len(filtered_data)} vessels for {time_range}")
    
    return filtered_data


def count_backup_files():
    """Count the number of XML backup files in the vessel data backup directory.
    
    Returns:
        int: Number of XML files in the backup directory, or 0 if directory doesn't exist
    """
    try:
        # Get the project root and construct the backup directory path
        backup_dir = os.path.join(find_project_root(), 'raw_data', 'vessel_data', 'backups')
        backup_dir = os.path.abspath(backup_dir)
        
        if not os.path.exists(backup_dir):
            logging.warning(f"Backup directory not found: {backup_dir}")
            return 0
        
        # Count XML files in the backup directory
        xml_files = [f for f in os.listdir(backup_dir) if f.endswith('.xml')]
        file_count = len(xml_files)
        
        logging.info(f"Found {file_count} XML backup files in {backup_dir}")
        return file_count
        
    except Exception as e:
        logging.error(f"Error counting backup files: {e}")
        return 0


def get_recent_vessel_counts():
    """
    Get vessel status counts for the most recent day with data.
    Returns counts for arriving, departing, and in_port vessels.
    """
    try:
        # Load the combined vessel data (same as used in Vessel Insights tab)
        vessel_data = load_combined_vessel_data()
        
        if vessel_data is None or vessel_data.empty:
            logging.warning("No vessel data available for recent counts")
            return {'arriving': 0, 'departing': 0, 'in_port': 0}
        
        # Get the most recent date in the data
        if 'timestamp' in vessel_data.columns:
            vessel_data['timestamp'] = pd.to_datetime(vessel_data['timestamp'])
            most_recent_date = vessel_data['timestamp'].max()
            # Filter to last 24 hours from the most recent date
            cutoff_time = most_recent_date - timedelta(hours=24)
            recent_data = vessel_data[vessel_data['timestamp'] >= cutoff_time]
        else:
            # If no timestamp column, use all data
            recent_data = vessel_data
        
        # Count vessels by status
        if 'status' in recent_data.columns:
            status_counts = recent_data['status'].value_counts()
            
            # Map status values to our categories
            arriving_count = status_counts.get('arriving', 0)
            departing_count = status_counts.get('departing', 0) + status_counts.get('departed', 0)
            in_port_count = status_counts.get('in_port', 0)
            
            logging.info(f"Recent vessel counts - Arriving: {arriving_count}, Departing: {departing_count}, In Port: {in_port_count}")
            
            return {
                'arriving': int(arriving_count),
                'departing': int(departing_count), 
                'in_port': int(in_port_count)
            }
        else:
            logging.warning("No 'status' column found in vessel data")
            return {'arriving': 0, 'departing': 0, 'in_port': 0}
            
    except Exception as e:
        logging.error(f"Error getting recent vessel counts: {e}")
        return {'arriving': 0, 'departing': 0, 'in_port': 0}


@optimized_computation(key="load_sample_data", ttl=600)
def load_sample_data(scenario='normal', use_real_throughput_data=True):
    """Load sample data based on scenario"""
    # Define scenario-based parameters with distinct, non-overlapping ranges
    scenario_params = {
        'peak': {
            'queue_multiplier': 2,
            'utilization_range': (85, 100),  # High utilization range
            'occupied_berths_range': (6, 8),  # High occupancy
            'waiting_time_multiplier': 1.5
        },
        'low': {
            'queue_multiplier': 0.5,
            'utilization_range': (25, 45),  # Low utilization range
            'occupied_berths_range': (1, 3),  # Low occupancy
            'waiting_time_multiplier': 0.7
        },
        'normal': {
            'queue_multiplier': 1,
            'utilization_range': (60, 80),  # Medium utilization range
            'occupied_berths_range': (4, 5),  # Medium occupancy
            'waiting_time_multiplier': 1
        }
    }
    
    params = scenario_params.get(scenario, scenario_params['normal'])
    
    # Randomly determine the number of occupied berths within the defined range
    num_berths = 8
    num_occupied = np.random.randint(params['occupied_berths_range'][0], params['occupied_berths_range'][1] + 1)
    
    # Ensure we don't exceed total berths and always have at least one maintenance berth
    num_occupied = min(num_occupied, num_berths - 1)  # Reserve at least 1 berth for maintenance
    num_available = num_berths - num_occupied - 1  # 1 berth for maintenance
    with tab1:
        st.subheader("🚢 Port Overview")
        
        with lazy_expander("KPI Summary"):
            kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
            with kpi_col1:
                st.metric("Vessels in Port", "85", delta="-5%", help="Total vessels currently at berth or anchorage")