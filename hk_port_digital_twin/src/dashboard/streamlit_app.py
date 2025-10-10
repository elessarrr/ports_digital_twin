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
from hk_port_digital_twin.src.dashboard.scenario_tab_consolidation import ConsolidatedScenariosTab
from hk_port_digital_twin.src.dashboard.vessel_charts import render_vessel_analytics_dashboard
from hk_port_digital_twin.src.dashboard.executive_dashboard import ExecutiveDashboard
from hk_port_digital_twin.src.utils.strategic_visualization import StrategicVisualization, render_strategic_controls
from hk_port_digital_twin.src.core.strategic_simulation_controller import StrategicSimulationController
from hk_port_digital_twin.src.utils.scenario_aware_calculator import ScenarioAwareCalculator, ValueType, ScenarioType
from hk_port_digital_twin.src.utils.scenario_helpers import get_wait_time_scenario_name

try:
    from hk_port_digital_twin.src.utils.wait_time_calculator import WaitTimeCalculator, calculate_wait_time
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
# from hk_port_digital_twin.src.dashboard.unified_simulations_tab import UnifiedSimulationsTab  # Commented out - tab hidden

try:
    from hk_port_digital_twin.src.dashboard.marine_traffic_integration import MarineTrafficIntegration
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
    
    # Create a list of statuses with exact length matching num_berths
    statuses = ['occupied'] * num_occupied + ['available'] * num_available + ['maintenance']
    np.random.shuffle(statuses)
    
    # Generate random utilization for occupied berths
    utilization_values = []
    for status in statuses:
        if status == 'occupied':
            utilization_values.append(np.random.randint(params['utilization_range'][0], params['utilization_range'][1] + 1))
        else:
            utilization_values.append(0)

    berth_data = {
        'berth_id': [f'Berth_{chr(65+i//4)}{i%4+1}' for i in range(num_berths)],
        'name': [f'Berth {chr(65+i//4)}{i%4+1}' for i in range(num_berths)],
        'x': [1, 2, 3, 4, 1, 2, 3, 4],
        'y': [1, 1, 1, 1, 2, 2, 3, 3],
        'status': statuses,
        'ship_id': [f'SHIP_{i:03d}' if statuses[i] == 'occupied' else None for i in range(num_berths)],
        'utilization': utilization_values,
        'berth_type': ['container', 'container', 'container', 'container', 'bulk', 'bulk', 'mixed', 'mixed'],
        'crane_count': [4, 3, 4, 2, 2, 2, 3, 3],
        'max_capacity_teu': [5000, 4000, 5000, 3000, 6000, 6000, 4500, 4500],
        'is_occupied': [status == 'occupied' for status in statuses]
    }

    # Load real container throughput data instead of simulated data
    if use_real_throughput_data:
        try:
            timeline_data = load_container_throughput()
            # The data already has a datetime index, so we use that as 'time'
            timeline_data = timeline_data.reset_index()
            timeline_data = timeline_data.rename(columns={'Date': 'time'})
            # Convert TEUs from thousands to actual numbers for better visualization
            timeline_data['seaborne_teus'] = timeline_data['seaborne_teus'] * 1000
            timeline_data['river_teus'] = timeline_data['river_teus'] * 1000
            timeline_data['total_teus'] = timeline_data['total_teus'] * 1000
        except Exception as e:
            # Enhanced fallback data using ScenarioAwareCalculator
            print(f"Warning: Could not load real throughput data: {e}")
            calculator = ScenarioAwareCalculator()
            
            # Determine scenario type based on scenario parameter
            if scenario == 'peak':
                scenario_type = ScenarioType.PEAK
            elif scenario == 'low':
                scenario_type = ScenarioType.LOW
            else:
                scenario_type = ScenarioType.NORMAL
            
            # Generate 25 hours of enhanced timeline data
            time_range = pd.date_range(start=datetime.now() - timedelta(hours=24), end=datetime.now(), freq='h')
            containers_processed = []
            ships_processed = []
            
            for hour in time_range:
                # Generate scenario-aware processing rates for each hour
                containers = calculator.generate_values(ValueType.CONTAINERS_PROCESSED, scenario_type, 1)[0]
                ships = calculator.generate_values(ValueType.SHIPS_PROCESSED, scenario_type, 1)[0]
                containers_processed.append(containers)
                ships_processed.append(ships)
            
            timeline_data = pd.DataFrame({
                'time': time_range,
                'containers_processed': containers_processed,
                'ships_processed': ships_processed
            })
    else:
        # Enhanced fallback data using ScenarioAwareCalculator
        calculator = ScenarioAwareCalculator()
        
        # Determine scenario type based on scenario parameter
        if scenario == 'peak':
            scenario_type = ScenarioType.PEAK
        elif scenario == 'low':
            scenario_type = ScenarioType.LOW
        else:
            scenario_type = ScenarioType.NORMAL
        
        # Generate 25 hours of enhanced timeline data
        time_range = pd.date_range(start=datetime.now() - timedelta(hours=24), end=datetime.now(), freq='h')
        containers_processed = []
        ships_processed = []
        
        for hour in time_range:
            # Generate scenario-aware processing rates for each hour
            containers = calculator.generate_values(ValueType.CONTAINERS_PROCESSED, scenario_type, 1)[0]
            ships = calculator.generate_values(ValueType.SHIPS_PROCESSED, scenario_type, 1)[0]
            containers_processed.append(containers)
            ships_processed.append(ships)
        
        timeline_data = pd.DataFrame({
            'time': time_range,
            'containers_processed': containers_processed,
            'ships_processed': ships_processed
        })

    # Enhanced ship queue data using ScenarioAwareCalculator
    num_ships_in_queue = int(3 * params['queue_multiplier'])
    
    # Initialize enhanced calculator for scenario-aware data generation
    calculator = ScenarioAwareCalculator()
    
    # Determine scenario type based on scenario parameter
    if scenario == 'peak':
        scenario_type = ScenarioType.PEAK
    elif scenario == 'low':
        scenario_type = ScenarioType.LOW
    else:
        scenario_type = ScenarioType.NORMAL
    
    ship_queue_data = {
        'ship_id': [f'SHIP_{i:03d}' for i in range(1, num_ships_in_queue + 1)],
        'name': [f'Ship {i}' for i in range(1, num_ships_in_queue + 1)],
        'ship_type': np.random.choice(['container', 'bulk'], num_ships_in_queue) if num_ships_in_queue > 0 else [],
        'arrival_time': [datetime.now() - timedelta(hours=i) for i in range(num_ships_in_queue, 0, -1)],
        'priority': np.random.choice(['high', 'medium', 'low'], num_ships_in_queue) if num_ships_in_queue > 0 else []
    }
    
    # Generate enhanced ship characteristics for all ships in queue
    if num_ships_in_queue > 0:
        # Generate ship profile with enhanced characteristics for all ships at once
        ship_profile = calculator.generate_ship_profile(scenario_type, num_ships_in_queue)
        
        # Extract enhanced characteristics from the profile structure
        characteristics = ship_profile.get('characteristics', {})
        ship_queue_data['containers'] = characteristics.get('containers', [0] * num_ships_in_queue)
        ship_queue_data['size_teu'] = characteristics.get('teu_capacity', [1000] * num_ships_in_queue)
        ship_queue_data['cargo_volume'] = characteristics.get('cargo_volume', [500] * num_ships_in_queue)
        ship_queue_data['processing_time'] = characteristics.get('processing_time', [4] * num_ships_in_queue)
        
        # Generate ship length and draft using individual value generation since they're not in ship_profile
        ship_queue_data['ship_length'] = calculator.generate_value(scenario_type, ValueType.SHIP_LENGTH, num_ships_in_queue)
        ship_queue_data['ship_draft'] = calculator.generate_value(scenario_type, ValueType.SHIP_DRAFT, num_ships_in_queue)
        
        # Generate enhanced waiting times using new calculator if available
        if calculate_wait_time:
            # Use new threshold-based calculator
            scenario_name = get_wait_time_scenario_name(scenario)
            waiting_times = [calculate_wait_time(scenario_name) for _ in range(num_ships_in_queue)]
        else:
            # Fallback to existing calculator
            waiting_times = []
            for i in range(num_ships_in_queue):
                wait_stats = calculator.get_wait_time_statistics(scenario_type, sample_size=1)
                # Use the mean waiting time as a representative value
                base_wait_time = wait_stats['statistics']['mean']
                waiting_times.append(base_wait_time)
        ship_queue_data['waiting_time'] = waiting_times
    else:
        # Empty lists for no ships
        ship_queue_data.update({
            'containers': [],
            'size_teu': [],
            'cargo_volume': [],
            'processing_time': [],
            'ship_length': [],
            'ship_draft': [],
            'waiting_time': []
        })
    
    # Sample waiting time data
    if calculate_wait_time:
        # Use new threshold-based calculator
        scenario_name = get_wait_time_scenario_name(scenario)
        waiting_times = [calculate_wait_time(scenario_name) for _ in range(20)]
    else:
        # Fallback to exponential distribution
        waiting_times = np.random.exponential(2, 20)
    
    waiting_data = {
        'ship_id': [f'SHIP_{i:03d}' for i in range(1, 21)],
        'waiting_time': waiting_times,
        'ship_type': np.random.choice(['container', 'bulk', 'mixed'], 20)
    }

    # Enhanced KPI data using processing rate statistics
    processing_stats = calculator.get_processing_rate_statistics(scenario_type, num_samples=50)
    
    # Calculate enhanced KPI values

    berth_utilization = np.mean(params['utilization_range'])
    throughput_rate = processing_stats['containers_processed']['mean']
    queue_length = 3 * params['queue_multiplier']
    processing_rate = processing_stats['processing_rate']['mean']
    ships_processed = processing_stats['ships_processed']['mean']
    
    kpi_data = {
        'metric': ['Berth Utilization', 'Throughput Rate', 'Queue Length', 'Processing Rate', 'Ships Processed/Day'],
        'value': [berth_utilization, throughput_rate, queue_length, processing_rate, ships_processed],
        'unit': ['%', 'containers/hour', 'ships', 'containers/hour', 'ships/day'],
        'target': [80, 90, 2, 75, 15],
        'status': [
            'good' if berth_utilization >= 70 else 'warning',
            'good' if throughput_rate >= 80 else 'warning',
            'warning' if queue_length > 2 else 'good',
            'good' if processing_rate >= 70 else 'warning',
            'good' if ships_processed >= 12 else 'warning'
        ]
    }

    return {
        'berths': pd.DataFrame(berth_data),
        'queue': pd.DataFrame(ship_queue_data),
        'timeline': timeline_data,
        'waiting': pd.DataFrame(waiting_data),
        'kpis': pd.DataFrame(kpi_data),
        'vessel_queue_analysis': {
            'total_vessels_waiting': len(ship_queue_data['ship_id']),
            'average_waiting_time': np.mean(ship_queue_data['waiting_time']) if num_ships_in_queue > 0 else 0,
            'queue_by_type': pd.DataFrame(ship_queue_data)['ship_type'].value_counts().to_dict() if num_ships_in_queue > 0 else {},
            'priority_distribution': pd.DataFrame(ship_queue_data)['priority'].value_counts().to_dict() if num_ships_in_queue > 0 else {}
        }
    }


def get_real_berth_data(berth_config):
    """Get real-time berth data from BerthManager"""
    if BerthManager and simpy:
        try:
            # Create a simulation environment and berth manager for real data
            env = simpy.Environment()
            berth_configs = load_berth_configurations()
            berth_manager = BerthManager(env, berth_configs)
            
            # Get berth statistics
            berth_stats = berth_manager.get_berth_statistics()
            
            # Convert berth data to DataFrame format
            berths_list = []
            for berth_id, berth in berth_manager.berths.items():
                berths_list.append({
                    'berth_id': berth_id,
                    'name': berth.name,  # Use actual berth name from CSV
                    'status': 'occupied' if berth.is_occupied else 'available',
                    'ship_id': berth.current_ship.ship_id if berth.current_ship else None,
                    'berth_type': berth.berth_type,
                    'crane_count': berth.crane_count,
                    'max_capacity_teu': berth.max_capacity_teu,
                    'is_occupied': berth.is_occupied,
                    'utilization': 100 if berth.is_occupied else 0,
                    'x': hash(berth_id) % 5 + 1,  # Simple positioning
                    'y': hash(berth_id) % 3 + 1
                })
            
            berths_df = pd.DataFrame(berths_list)
            
            # Add berth statistics
            berth_metrics = {
                'total_berths': berth_stats['total_berths'],
                'occupied_berths': berth_stats['occupied_berths'],
                'available_berths': berth_stats['available_berths'],
                'utilization_rate': berth_stats['overall_utilization_rate'],
                'berth_types': berth_stats['berth_types']
            }
            
            return berths_df, berth_metrics
            
        except Exception as e:
            print(f"Warning: Could not get real berth data: {e}")
    
    # Fallback to sample data
    data = load_sample_data()
    if 'berths' in data and data['berths'] is not None and not data['berths'].empty:
        berth_metrics = {
            'total_berths': len(data['berths']),
            'occupied_berths': len(data['berths'][data['berths']['status'] == 'occupied']),
            'available_berths': len(data['berths'][data['berths']['status'] == 'available']),
            'utilization_rate': len(data['berths'][data['berths']['status'] == 'occupied']) / len(data['berths']) * 100,
            'berth_types': data['berths']['berth_type'].value_counts().to_dict()
        }
        return data['berths'], berth_metrics
    else:
        # Return empty DataFrame and default metrics if berths data is not available
        empty_berths = pd.DataFrame(columns=['berth_id', 'name', 'status', 'ship_id', 'berth_type', 'crane_count', 'max_capacity_teu', 'is_occupied', 'utilization', 'x', 'y'])
        berth_metrics = {
            'total_berths': 0,
            'occupied_berths': 0,
            'available_berths': 0,
            'utilization_rate': 0,
            'berth_types': {}
        }
        return empty_berths, berth_metrics


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    logging.info("Initializing session state...")
    if 'scenario' not in st.session_state:
        st.session_state.scenario = 'normal'
    # Removed simulation_running and simulation_controller - no longer needed after removing simulation settings
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now()
    
    # Initialize real-time data manager
    if 'real_time_manager' not in st.session_state:
        if RealTimeDataConfig and get_real_time_manager:
            try:
                # Configure real-time data manager
                config = RealTimeDataConfig(
                    enable_weather_integration=True,
                    enable_file_monitoring=True,
                    vessel_update_interval=15,   # 15 seconds
                    weather_update_interval=300,  # 5 minutes
                    auto_reload_on_file_change=True,
                    cache_duration=60             # 1 minute
                )
                
                # Get and start the real-time manager
                manager = get_real_time_manager(config)
                manager.start_real_time_updates()
                st.session_state.real_time_manager = manager
                
                # Initialize vessel data pipeline
                try:
                    initialize_vessel_data_pipeline()
                    logging.info("Vessel data pipeline initialized successfully")
                except Exception as e:
                    logging.warning(f"Could not initialize vessel data pipeline: {e}")
                
            except Exception as e:
                print(f"Warning: Could not initialize real-time data manager: {e}")
                st.session_state.real_time_manager = None
        else:
            st.session_state.real_time_manager = None
    
    # Initialize dashboard preferences
    if 'use_consolidated_scenarios' not in st.session_state:
        st.session_state.use_consolidated_scenarios = True
    if 'show_section_navigation' not in st.session_state:
        st.session_state.show_section_navigation = False  # Disabled as per demo refinement plan
    # Removed expand_sections_by_default and remember_section_states - no longer needed after removing section navigation
    if 'scenarios_sections_expanded' not in st.session_state:
        st.session_state.scenarios_sections_expanded = False
    
    # Initialize scenario manager if not in session state
    if 'scenario_manager' not in st.session_state:
        st.session_state.scenario_manager = ScenarioManager()
    
    # Initialize debug mode
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = True  # Enable debug mode by default for troubleshooting
    
    # Vessel data scheduler disabled to prevent frequent XML downloads
    # The scheduler was causing downloads every minute due to Streamlit app restarts
    # Manual vessel data fetching is still available when needed
    # Daily downloads can be configured separately if needed via cron or external scheduler
    if 'vessel_data_scheduler' not in st.session_state:
        st.session_state.vessel_data_scheduler = None
        logging.info("Vessel data scheduler disabled - no automatic XML downloads")





def load_data(scenario: str):
    """Loads data for a given scenario with caching to prevent regeneration on UI interactions."""
    try:
        # Check if data is already cached for this scenario
        cache_key = f"data_{scenario}"
        if cache_key not in st.session_state:
            # Load data using the utility function and cache it
            st.session_state[cache_key] = load_sample_data(scenario)
        
        return st.session_state[cache_key]
    except Exception as e:
        st.error(f"Error loading data for scenario '{scenario}': {e}")
        return {}

def main():
    """Main dashboard application"""
    # Initialize session state
    initialize_session_state()


    
    # --- Main Content ---
    
    # Get current scenario from session state
    scenario = st.session_state.scenario_manager.get_current_scenario()
    
    # Check if scenario has changed and clear cache if needed
    if 'current_scenario' not in st.session_state or st.session_state.current_scenario != scenario:
        # Clear cached data when scenario changes
        keys_to_remove = [key for key in st.session_state.keys() if key.startswith('data_')]
        for key in keys_to_remove:
            del st.session_state[key]
        st.session_state.current_scenario = scenario

    # Load data based on the selected scenario (now cached)
    data = load_data(scenario)
    
    # Header
    st.title("🏗️ Hong Kong Port Digital Twin Dashboard")
    st.markdown("Real-time visualization and control of port operations")
    
    # Main dashboard layout - conditional based on user preference
    use_consolidated = st.session_state.get('use_consolidated_scenarios', True)
    
    if use_consolidated:
        # New consolidated structure with Strategic tab removed and components moved to other tabs
        # Strategic tab components moved to: Port Analytics (in Cargo Statistics) and Activity Trend (in Operational)
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview", "📦 Cargo Statistics", "🛳️ Vessel Insights (Operational)", 
            "🎯 Scenarios", "⚙️ Settings"
        ])
    else:
        # Original structure with Strategic tab removed and components moved to other tabs
        # Strategic tab components moved to: Port Analytics (in Cargo Statistics) and Activity Trend (in Operational)
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📊 Overview", "📦 Cargo Statistics", "🛳️ Vessel Insights (Operational)",
            "🎯 Scenarios", "⚙️ Settings",
            "📊 Performance Analytics", "📦 Cargo Analysis"
        ])
        # Note: Strategic tab removed - components consolidated into Cargo Statistics and Operational tabs
    
    with tab1:
        st.subheader("Port Overview")
        
        # KPI Summary
        # Center the forecast chart
        col1, col2, col3 = st.columns([0.5, 2, 0.5])
        
        with col2:
            # Load real forecast data if available
            try:
                if get_enhanced_cargo_analysis is not None:
                    cargo_analysis = get_enhanced_cargo_analysis()
                    forecasts = cargo_analysis.get('forecasts', {})
                else:
                    forecasts = {}
            except Exception:
                forecasts = {}
            if forecasts:
                # Convert forecast data to expected format for create_kpi_summary_chart
                kpi_dict = {}
                forecast_categories = ['direct_shipment', 'transhipment', 'seaborne', 'river']
                
                for category in forecast_categories:
                    if category in forecasts:
                        # Get the first forecast data (assuming it's the main metric)
                        category_data = forecasts[category]
                        if category_data:
                            first_metric = list(category_data.keys())[0]
                            forecast_info = category_data[first_metric]
                            
                            # Ensure years are integers
                            hist_years = [int(year) for year in forecast_info.get('historical_data', {}).keys()]
                            hist_values = list(forecast_info.get('historical_data', {}).values())
                            forecast_years = [int(year) for year in forecast_info.get('forecast_years', [])]
                            forecast_values = forecast_info.get('forecast_values', [])
                            
                            kpi_dict[category] = {
                                'historical_years': hist_years,
                                'historical_values': hist_values,
                                'forecast_years': forecast_years,
                                'forecast_values': forecast_values
                            }
                
                # Add model performance data
                model_performance = {}
                for category in forecast_categories:
                    if category in forecasts:
                        category_data = forecasts[category]
                        if category_data:
                            first_metric = list(category_data.keys())[0]
                            metrics = category_data[first_metric].get('model_metrics', {})
                            model_performance[category] = {
                                'r2_score': metrics.get('r2', 0),
                                'mae': metrics.get('mae', 0)
                            }
                
                kpi_dict['model_performance'] = model_performance
                create_kpi_summary_chart(kpi_dict)
            else:
                # Fallback to sample data if no forecasts available
                # Calculate dynamic wait time based on current scenario
                current_scenario = scenario if scenario else 'normal'
                wait_time_scenario = get_wait_time_scenario_name(current_scenario)
                
                if calculate_wait_time:
                    try:
                        # Calculate a representative average by sampling multiple times
                        num_samples = 100  # Number of samples for a stable average
                        wait_times = [calculate_wait_time(wait_time_scenario) for _ in range(num_samples)]
                        fallback_wait_time = np.mean(wait_times) if wait_times else 8.0
                    except Exception as e:
                        logging.warning(f"Error calculating wait time for KPI fallback: {e}")
                        fallback_wait_time = 8.0  # Default fallback
                else:
                    fallback_wait_time = 8.0  # Fallback when calculator not available
                
                kpi_dict = {
                    'average_waiting_time': fallback_wait_time,
                    'average_berth_utilization': 0.75,
                    'total_ships_processed': 85,
                    'total_containers_processed': 1200,
                    'average_queue_length': 3
                }
                create_kpi_summary_chart(kpi_dict)
        
        # Metrics section
        st.subheader("📊 Key Metrics")
        
        vessel_analysis = data.get('vessel_queue_analysis', {})
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # Get recent vessel counts for the most recent day with data
            vessel_counts = get_recent_vessel_counts()
            st.metric("🚢 Arriving", vessel_counts['arriving'])
            st.metric("⚓ In Port", vessel_counts['in_port'])
            st.metric("🛳️ Departing", vessel_counts['departing'])

        with col2:
            # Safe access to berths data with fallback
            berths_df = data.get('berths', pd.DataFrame())
            if not berths_df.empty and 'status' in berths_df.columns:
                available_berths = len(berths_df[berths_df['status'] == 'available'])
            else:
                available_berths = 0
            st.metric("Available Berths", available_berths)

        with col3:
            # Show recent arrivals if available
            if vessel_analysis and 'recent_activity' in vessel_analysis:
                arrivals_24h = vessel_analysis['recent_activity'].get('arrivals_last_24h', 0)
                st.metric("24h Arrivals", arrivals_24h)
            else:
                # Show port efficiency metric instead of wait time
                st.metric("Port Efficiency", "85%")

        with col4:
            st.metric("Utilization Rate", "75%")
        
 
    
    with tab2:
        st.subheader("📦 Port Cargo Statistics")
        st.markdown("Comprehensive analysis of Hong Kong port cargo throughput data with time series analysis and forecasting")
        
        # Load enhanced cargo analysis
        try:
            if load_focused_cargo_statistics is None or get_enhanced_cargo_analysis is None or get_time_series_data is None:
                st.warning("⚠️ Cargo statistics analysis not available")
                st.info("Please ensure the data loader module is properly installed and configured.")
                focused_data = {}
                cargo_analysis = {}
                time_series_data = {}
            else:
                with st.spinner("Loading enhanced cargo statistics..."):
                    # Load focused data (Tables 1 & 2)
                    focused_data = load_focused_cargo_statistics()
                    
                    # Get enhanced analysis with forecasting
                    cargo_analysis = get_enhanced_cargo_analysis()
                    
                    # Get time series data for visualization
                    time_series_data = get_time_series_data(focused_data)
        except Exception as e:
            st.error(f"Error loading cargo statistics: {str(e)}")
            st.info("Please ensure the Port Cargo Statistics CSV files are available in the raw_data directory.")
            focused_data = {}
            cargo_analysis = {}
            time_series_data = {}
        
        # Display data summary
        st.subheader("📊 Data Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            tables_processed = cargo_analysis.get('data_summary', {}).get('tables_processed', 0)
            st.markdown(f'''
            <div class="card">
                <div class="card-title">Tables Processed</div>
                <div class="card-text">{tables_processed}</div>
            </div>
            ''', unsafe_allow_html=True)
        with col2:
            status = "✅ Complete" if cargo_analysis else "❌ Failed"
            st.markdown(f'''
            <div class="card">
                <div class="card-title">Analysis Status</div>
                <div class="card-text">{status}</div>
            </div>
            ''', unsafe_allow_html=True)
        with col3:
            analysis_sections = len([k for k in cargo_analysis.keys() if k.endswith('_analysis')])
            st.markdown(f'''
            <div class="card">
                <div class="card-title">Analysis Sections</div>
                <div class="card-text">{analysis_sections}</div>
            </div>
            ''', unsafe_allow_html=True)
        with col4:
            timestamp = cargo_analysis.get('data_summary', {}).get('analysis_timestamp', datetime.now().isoformat())
            date = timestamp[:10] if timestamp else datetime.now().strftime("%Y-%m-%d")
            st.markdown(f'''
            <div class="card">
                <div class="card-title">Analysis Date</div>
                <div class="card-text">{date}</div>
            </div>
            ''', unsafe_allow_html=True)

        # Create tabs for different analysis sections
        cargo_tab1, cargo_tab2, cargo_tab3, cargo_tab4 = st.tabs([
            "📊 Shipment Types", "🚢 Transport Modes", "📈 Time Series", "🏗️ Port Analytics"
        ])

        with cargo_tab1:
            # Center the whole tab content
            main_col1, main_col2, main_col3 = st.columns([0.1, 0.8, 0.1])
            with main_col2:
                st.subheader("Shipment Type Analysis")
                
                # Get shipment type data from time series
                shipment_ts = time_series_data.get('shipment_types', pd.DataFrame())
                
                if not shipment_ts.empty:
                    # Get latest year data (2023)
                    latest_data = shipment_ts.loc[2023] if 2023 in shipment_ts.index else shipment_ts.iloc[-1]
                    total = latest_data['Overall']
                    direct_pct = (latest_data['Direct shipment cargo'] / total) * 100
                    tranship_pct = (latest_data['Transhipment cargo'] / total) * 100

                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**2023 Throughput Data**")
                        breakdown_data = {
                            'Direct Shipment': latest_data['Direct shipment cargo'],
                            'Transhipment': latest_data['Transhipment cargo']
                        }
                        breakdown_df = pd.DataFrame(list(breakdown_data.items()),
                                                    columns=['Shipment Type', 'Throughput (000 tonnes)'])
                        st.dataframe(breakdown_df, use_container_width=True)
                    
                    with col2:
                        st.write("**Percentage Distribution**")
                        st.metric("Direct Shipment", f"{direct_pct:.1f}%")
                        st.metric("Transhipment", f"{tranship_pct:.1f}%")
                        
                    # Show time series chart
                    st.write("**Historical Trends (2014-2023)**")
                    chart_data = shipment_ts[['Direct shipment cargo', 'Transhipment cargo']]
                    
                    # Create plotly chart for better control over formatting
                    import plotly.graph_objects as go
                    fig = go.Figure()
                    
                    # Ensure years are integers
                    years = [int(year) for year in chart_data.index]
                    
                    fig.add_trace(go.Scatter(
                        x=years,
                        y=chart_data['Direct shipment cargo'],
                        mode='lines+markers',
                        name='Direct Shipment Cargo',
                        line=dict(color='blue')
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=years,
                        y=chart_data['Transhipment cargo'],
                        mode='lines+markers',
                        name='Transhipment Cargo',
                        line=dict(color='red')
                    ))
                    
                    fig.update_layout(
                        xaxis_title="Year",
                        yaxis_title="Throughput (000 tonnes)",
                        height=400,
                        xaxis=dict(tickmode='linear', dtick=1),  # Force integer years
                        margin=dict(l=50, r=50, t=50, b=50)  # Center the chart
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, key="shipment_trends_chart")
                else:
                    st.info("No shipment type analysis data available.")
                    st.warning("Please ensure the Port Cargo Statistics CSV files are available in the raw_data directory.")

        with cargo_tab2:
            st.subheader("Transport Mode Analysis")
            
            # Get transport mode data from time series
            transport_ts = time_series_data.get('transport_modes', pd.DataFrame())
            
            if not transport_ts.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**2023 Transport Data**")
                    # Get latest year data (2023)
                    latest_data = transport_ts.loc[2023] if 2023 in transport_ts.index else transport_ts.iloc[-1]
                    
                    transport_breakdown = {
                        'Waterborne': latest_data['Waterborne'],
                        'Seaborne': latest_data['Seaborne'],
                        'River': latest_data['River']
                    }
                    transport_df = pd.DataFrame(list(transport_breakdown.items()), 
                                                columns=['Transport Mode', 'Throughput (000 tonnes)'])
                    st.dataframe(transport_df, use_container_width=True)
                    
                    # Calculate percentages
                    total = sum(transport_breakdown.values())
                    waterborne_pct = (latest_data['Waterborne'] / total) * 100
                    seaborne_pct = (latest_data['Seaborne'] / total) * 100
                    river_pct = (latest_data['River'] / total) * 100
                
                with col2:
                    st.write("**Modal Split Percentage**")
                    st.metric("Waterborne", f"{waterborne_pct:.1f}%")
                    st.metric("Seaborne", f"{seaborne_pct:.1f}%")
                    st.metric("River", f"{river_pct:.1f}%")
                    
                # Show time series chart
                st.write("**Historical Trends**")
                chart_data = transport_ts[['Waterborne', 'Seaborne', 'River']]
                
                # Create plotly chart for better control over formatting
                import plotly.graph_objects as go
                fig = go.Figure()
                
                # Ensure years are integers
                years = [int(year) for year in chart_data.index]
                
                fig.add_trace(go.Scatter(
                    x=years,
                    y=chart_data['Waterborne'],
                    mode='lines+markers',
                    name='Waterborne',
                    line=dict(color='purple')
                ))
                
                fig.add_trace(go.Scatter(
                    x=years,
                    y=chart_data['Seaborne'],
                    mode='lines+markers',
                    name='Seaborne',
                    line=dict(color='green')
                ))
                
                fig.add_trace(go.Scatter(
                    x=years,
                    y=chart_data['River'],
                    mode='lines+markers',
                    name='River',
                    line=dict(color='orange')
                ))
                
                fig.update_layout(
                    xaxis_title="Year",
                    yaxis_title="Throughput (000 tonnes)",
                    height=400,
                    xaxis=dict(tickmode='linear', dtick=1),  # Force integer years
                    margin=dict(l=50, r=50, t=50, b=50)  # Center the chart
                )
                
                # Center the chart
                chart_col1, chart_col2, chart_col3 = st.columns([0.1, 0.8, 0.1])
                with chart_col2:
                    st.plotly_chart(fig, use_container_width=True, key="transport_trends_chart")
                
            else:
                st.info("No transport mode analysis data available")
                st.warning("Please ensure the Port Cargo Statistics CSV files are available in the raw_data directory.")

        with cargo_tab3:
            st.subheader("Time Series Analysis")
            
            if time_series_data:
                # Display time series charts
                import plotly.graph_objects as go
                from plotly.subplots import make_subplots
                
                # Create subplots for different metrics
                fig = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=(
                        'Direct Shipment Trends', 'Transhipment Trends',
                        'Transport Mode Trends', 'River Transport Trends'
                    ),
                    specs=[[{"secondary_y": False}, {"secondary_y": False}],
                           [{"secondary_y": False}, {"secondary_y": False}]]
                )
                
                # Extract time series data
                shipment_ts = time_series_data.get('shipment_types', pd.DataFrame())
                transport_ts = time_series_data.get('transport_modes', pd.DataFrame())
                
                if not shipment_ts.empty:
                    # Ensure years are integers
                    years = [int(year) for year in shipment_ts.index.tolist()]
                    direct_values = shipment_ts['Direct shipment cargo'].tolist()
                    tranship_values = shipment_ts['Transhipment cargo'].tolist()
                    
                    # Direct shipment trend
                    fig.add_trace(
                        go.Scatter(x=years, y=direct_values, mode='lines+markers',
                                 name='Direct Shipment', line=dict(color='blue')),
                        row=1, col=1
                    )
                    
                    # Transhipment trend
                    fig.add_trace(
                        go.Scatter(x=years, y=tranship_values, mode='lines+markers',
                                 name='Transhipment', line=dict(color='red')),
                        row=1, col=2
                    )
                
                if not transport_ts.empty:
                    # Ensure years are integers
                    years = [int(year) for year in transport_ts.index.tolist()]
                    waterborne_values = transport_ts['Waterborne'].tolist()
                    seaborne_values = transport_ts['Seaborne'].tolist()
                    river_values = transport_ts['River'].tolist()
                    
                    # Waterborne transport trend
                    fig.add_trace(
                        go.Scatter(x=years, y=waterborne_values, mode='lines+markers',
                                 name='Waterborne', line=dict(color='purple')),
                        row=2, col=1
                    )
                    
                    # Seaborne transport trend
                    fig.add_trace(
                        go.Scatter(x=years, y=seaborne_values, mode='lines+markers',
                                 name='Seaborne', line=dict(color='green')),
                        row=2, col=1
                    )
                    
                    # River transport trend
                    fig.add_trace(
                        go.Scatter(x=years, y=river_values, mode='lines+markers',
                                 name='River', line=dict(color='orange')),
                        row=2, col=2
                    )
                
                fig.update_layout(
                    height=600,
                    title_text="Port Cargo Time Series Analysis (2014-2023)",
                    showlegend=False,
                    margin=dict(l=50, r=50, t=50, b=50)  # Center the chart
                )
                
                fig.update_xaxes(title_text="Year", tickmode='linear', dtick=1)  # Force integer years
                fig.update_yaxes(title_text="Throughput (000 tonnes)")
                
                # Center the chart
                chart_col1, chart_col2, chart_col3 = st.columns([0.1, 0.8, 0.1])
                with chart_col2:
                    st.plotly_chart(fig, use_container_width=True, key="time_series_chart")

        with cargo_tab4:
            st.subheader("🏗️ Port Analytics")
            st.markdown("Throughput and waiting time analysis for port operations")
            
            # Check if data is properly loaded for analytics
            if data and 'berths' in data:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Throughput Timeline")
                    if create_throughput_timeline is not None:
                        fig_timeline = create_throughput_timeline(data['timeline'])
                        st.plotly_chart(fig_timeline, use_container_width=True, key="cargo_analytics_throughput_timeline_chart")
                    else:
                        st.warning("Throughput timeline visualization not available. Please check visualization module import.")
                        st.dataframe(data['timeline'], use_container_width=True)
                
                with col2:
                    st.subheader("Waiting Time Distribution")
                    # Convert DataFrame to list for visualization
                    waiting_times_list = data['waiting']['waiting_time'].tolist()
                    if create_waiting_time_distribution is not None:
                        fig_waiting = create_waiting_time_distribution(waiting_times_list)
                        st.plotly_chart(fig_waiting, use_container_width=True, key="cargo_analytics_waiting_time_chart")
                    else:
                        st.warning("Waiting time distribution visualization not available. Please check visualization module import.")
                        st.dataframe(data['waiting'], use_container_width=True)
            else:
                st.info("Analytics data not available. Please ensure scenario data is properly loaded.")

    
    with tab3:
        # COMMENTED OUT: Live Vessel Arrivals heading and Refresh Data button - user requested to hide these for now
        # st.subheader("🚢 Live Vessel Arrivals")
        # st.markdown("Real-time vessel arrival data and analytics for Hong Kong port")
        
        # # Add refresh data button and status (moved from Strategic tab)
        # col1, col2, col3, col4 = st.columns([0.3, 0.5, 1, 1])
        # with col1:
        #     if st.button("🔄 Refresh Data", help="Download latest vessel data from Hong Kong Marine Department", key="refresh_live_arrivals"):
        #         with st.spinner("Refreshing vessel data..."):
        #             try:
        #                 # Import and use the vessel data fetcher
        #                 from hk_port_digital_twin.src.utils.vessel_data_fetcher import VesselDataFetcher
        #                 
        #                 fetcher = VesselDataFetcher()
        #                 results = fetcher.fetch_xml_files()
        #                 
        #                 if results:
        #                     success_count = sum(1 for success in results.values() if success)
        #                     total_count = len(results)
        #                     
        #                     if success_count == total_count:
        #                         st.success(f"✅ Successfully refreshed all {total_count} vessel data files!")
        #                     elif success_count > 0:
        #                         st.warning(f"⚠️ Refreshed {success_count} of {total_count} files. Some files may have failed.")
        #                     else:
        #                         st.error("❌ Failed to refresh vessel data. Please check the logs.")
        #                 else:
        #                     st.error("❌ No data files were processed. Please check the configuration.")
        #                     
        #                 # Force a rerun to reload the data
        #                 st.rerun()
        #                 
        #             except Exception as e:
        #                 st.error(f"❌ Error refreshing data: {str(e)}")
        
        # # with col2:
        #     # Show scheduler status side by side with the refresh button
        #     # Use a compact container to limit the width of the auto-refresh info
        #     # COMMENTED OUT: Auto-refresh display section - user requested to hide this for now
        #     # try:
        #     #     scheduler = st.session_state.get('vessel_data_scheduler')
        #     #     if scheduler:
        #     #         status = scheduler.get_scheduler_status()
        #     #         if status['running']:
        #     #             next_run = status.get('next_execution_time')
        #     #             if next_run:
        #     #                 next_run_dt = datetime.fromisoformat(next_run.replace('Z', '+00:00'))
        #     #                 time_until = next_run_dt - datetime.now()
        #     #                 minutes_until = int(time_until.total_seconds() / 60)
        #     #                 
        #     #                 if minutes_until > 0:
        #     #                     # Create a compact container for the auto-refresh info
        #     #                     with st.container():
        #     #                         st.markdown(
        #     #                             f'<div style="background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 0.25rem; padding: 0.5rem; margin: 0.25rem 0; display: inline-block; color: #0c5460; font-size: 0.875rem;">🤖 Auto-refresh in {minutes_until} min</div>',
        #     #                             unsafe_allow_html=True
        #     #                         )
        #     #                 else:
        #     #                     with st.container():
        #     #                         st.markdown(
        #     #                             f'<div style="background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 0.25rem; padding: 0.5rem; margin: 0.25rem 0; display: inline-block; color: #0c5460; font-size: 0.875rem;">🤖 Auto-refresh running...</div>',
        #     #                             unsafe_allow_html=True
        #     #                         )
        #     #             else:
        #     #                 with st.container():
        #     #                     st.markdown(
        #     #                         f'<div style="background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 0.25rem; padding: 0.5rem; margin: 0.25rem 0; display: inline-block; color: #0c5460; font-size: 0.875rem;">🤖 Auto-refresh active</div>',
        #     #                         unsafe_allow_html=True
        #     #                     )
        #     #         else:
        #     #             with st.container():
        #     #                 st.markdown(
        #     #                     f'<div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 0.25rem; padding: 0.5rem; margin: 0.25rem 0; display: inline-block; color: #0c5460; font-size: 0.875rem;">🤖 Auto-refresh disabled</div>',
        #     #                     unsafe_allow_html=True
        #     #                 )
        #     #     else:
        #     #         with st.container():
        #     #             st.markdown(
        #     #                 f'<div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 0.25rem; padding: 0.5rem; margin: 0.25rem 0; display: inline-block; color: #856404; font-size: 0.875rem;">🤖 Scheduler unavailable</div>',
        #     #                 unsafe_allow_html=True
        #     #             )
        #     # except Exception as e:
        #     #     st.caption(f"Scheduler status unavailable: {str(e)}")
        #     pass  # Placeholder to maintain code structure
        
        # with col3:
        #     # Column intentionally left empty
        #     pass
        
        # with col4:
        #     # Column intentionally left empty
        #     pass
        
        # Time range selection (moved to top to determine data loading strategy)
        st.subheader("📊 Data Selection")
        
        # Add info about historical data availability
        #st.info("💡 **Historical Data Available**: 466 backup files ready to load. Select 'All historical data' to access comprehensive vessel history!")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Time range filter with enhanced options
            time_range_options = [
                'Last 7 days ', 
                'Last 30 days', 
                'Last 90 days',
                'Last 180 days',
                'Last 1 year',
                'Last 2 years',
                'Last 3 years',
                '🗂️ All historical data'
            ]
            selected_time_range = st.selectbox("Time Range", time_range_options, index=0)
            
            # Convert back to original format for processing
            if selected_time_range.startswith('Last 7 days'):
                selected_time_range = 'Last 7 days'
            elif selected_time_range.startswith('Last 30 days'):
                selected_time_range = 'Last 30 days'
            elif selected_time_range.startswith('Last 90 days'):
                selected_time_range = 'Last 90 days'
            elif selected_time_range.startswith('Last 180 days'):
                selected_time_range = 'Last 180 days'
            elif selected_time_range.startswith('Last 1 year'):
                selected_time_range = 'Last 1 year'
            elif selected_time_range.startswith('Last 2 years'):
                selected_time_range = 'Last 2 years'
            elif selected_time_range.startswith('Last 3 years'):
                selected_time_range = 'Last 3 years'
            elif selected_time_range.startswith('🗂️ All historical data'):
                selected_time_range = 'All historical data'
        
        with col2:
            st.write("")  # Placeholder for future controls
        
        with col3:
            st.write("")  # Placeholder for future controls
        
        # Load vessel data based on time range selection
        try:
            if selected_time_range == 'All historical data':
                # Enhanced loading feedback
                with st.spinner("🔄 Loading comprehensive historical data..."):
                    backup_file_count = count_backup_files()
                    st.warning(f"⏳ **Loading {backup_file_count} backup files** - This may take 30-60 seconds. Please wait...")
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("📂 Initializing backup file loading...")
                    progress_bar.progress(10)
                    
                    # Load all historical data including backups (no file limit for comprehensive data)
                    all_vessel_data = load_all_vessel_data_with_backups(include_backups=True, max_backup_files=None)
                    
                    progress_bar.progress(90)
                    status_text.text("🔄 Processing and deduplicating vessel records...")
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Historical data loading complete!")
                
                # Combine all data sources into a single DataFrame
                vessel_dataframes = []
                for source_name, df in all_vessel_data.items():
                    if not df.empty:
                        df['data_source'] = source_name
                        vessel_dataframes.append(df)
                
                if vessel_dataframes:
                    vessel_data = pd.concat(vessel_dataframes, ignore_index=True)
                    # Remove duplicates based on call_sign and arrival_time if available
                    duplicate_columns = ['call_sign']
                    if 'arrival_time' in vessel_data.columns:
                        duplicate_columns.append('arrival_time')
                    elif 'timestamp' in vessel_data.columns:
                        duplicate_columns.append('timestamp')
                    vessel_data = vessel_data.drop_duplicates(subset=duplicate_columns, keep='first')
                else:
                    vessel_data = pd.DataFrame()
            else:
                # Load current vessel data and apply time filtering
                if selected_time_range in ['Last 7 days', 'Last 30 days', 'Last 90 days', 'Last 180 days', 'Last 1 year', 'Last 2 years', 'Last 3 years']:
                    # Load all historical data first, then filter by time range
                    all_vessel_data = load_all_vessel_data_with_backups(include_backups=True, max_backup_files=None)
                    
                    # Combine all data sources into a single DataFrame
                    vessel_dataframes = []
                    for source_name, df in all_vessel_data.items():
                        if not df.empty:
                            df['data_source'] = source_name
                            vessel_dataframes.append(df)
                    
                    if vessel_dataframes:
                        vessel_data = pd.concat(vessel_dataframes, ignore_index=True)
                        # Remove duplicates based on call_sign and arrival_time if available
                        duplicate_columns = ['call_sign']
                        if 'arrival_time' in vessel_data.columns:
                            duplicate_columns.append('arrival_time')
                        elif 'timestamp' in vessel_data.columns:
                            duplicate_columns.append('timestamp')
                        vessel_data = vessel_data.drop_duplicates(subset=duplicate_columns, keep='first')
                        
                        # Apply time filtering
                        vessel_data = filter_vessel_data_by_time_range(vessel_data, selected_time_range)
                    else:
                        vessel_data = pd.DataFrame()
                else:
                    # Load current vessel data only (for backward compatibility)
                    vessel_data = load_combined_vessel_data()
            
            if vessel_data is None or vessel_data.empty:
                st.warning("⚠️ No vessel data available")
                st.info("Please ensure vessel data files are available in the data directory.")
                vessel_data = pd.DataFrame()
        except Exception as e:
            st.error(f"Error loading vessel data: {str(e)}")
            vessel_data = pd.DataFrame()
        
        if not vessel_data.empty:
            # Current vessel status
            st.subheader("📊 Current Vessel Status")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_vessels = len(vessel_data)
                st.metric("Total Vessels", total_vessels)
            
            with col2:
                arriving_vessels = len(vessel_data[vessel_data.get('status', '') == 'arriving']) if 'status' in vessel_data.columns else 0
                st.metric("Arriving", arriving_vessels)
            
            with col3:
                in_port_vessels = len(vessel_data[vessel_data.get('status', '') == 'in_port']) if 'status' in vessel_data.columns else 0
                st.metric("In Port", in_port_vessels)
            
            with col4:
                departed_vessels = len(vessel_data[vessel_data.get('status', '') == 'departed']) if 'status' in vessel_data.columns else 0
                st.metric("Departed", departed_vessels)
            
            # Data Source Summary
            st.subheader("📋 Data Source Summary")
            if selected_time_range == 'All historical data':
                st.success(f"✅ **Historical Data Loaded**: Displaying {total_vessels:,} vessels from {backup_file_count} backup files + current data")
                st.info("🗂️ **Data Coverage**: Complete historical records with enhanced vessel tracking")
            elif selected_time_range in ['Last 180 days', 'Last 1 year', 'Last 2 years', 'Last 3 years']:
                st.success(f"✅ **Filtered Historical Data**: Displaying {total_vessels:,} vessels from {selected_time_range.lower()}")
                st.info("🗂️ **Data Source**: Filtered from complete historical database (backup files + current data)")
            else:
                st.info(f"📅 **Current Data**: Displaying {total_vessels:,} vessels from {selected_time_range.lower()}")
                st.warning("💡 **Tip**: Select 'All historical data' above to see the complete vessel database ")
            
            # Vessel locations
            st.subheader("📍 Vessel Locations")
            location_column = 'current_location' if 'current_location' in vessel_data.columns else 'location'
            if location_column in vessel_data.columns:
                location_counts = vessel_data[location_column].value_counts().head(10)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Location Distribution**")
                    location_df = pd.DataFrame({
                        'Location': location_counts.index,
                        'Vessel Count': location_counts.values
                    })
                    st.dataframe(location_df, use_container_width=True)
                
                with col2:
                    st.write("**Location Distribution Chart**")
                    import plotly.express as px
                    fig = px.pie(values=location_counts.values, names=location_counts.index, 
                                title="Vessels by Location")
                    st.plotly_chart(fig, use_container_width=True, key="location_pie_chart")
            
            # Ship categories
            st.subheader("🚢 Ship Categories")
            ship_type_column = 'ship_category' if 'ship_category' in vessel_data.columns else 'ship_type'
            if ship_type_column in vessel_data.columns:
                category_counts = vessel_data[ship_type_column].value_counts().head(10)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Category Distribution**")
                    category_df = pd.DataFrame({
                        'Ship Type': category_counts.index,
                        'Count': category_counts.values
                    })
                    st.dataframe(category_df, use_container_width=True)
                
                with col2:
                    st.write("**Category Distribution Chart**")
                    import plotly.express as px
                    fig = px.bar(x=category_counts.index, y=category_counts.values,
                                title="Vessels by Ship Type",
                                labels={'x': 'Ship Type', 'y': 'Count'})
                    st.plotly_chart(fig, use_container_width=True, key="category_bar_chart")
            

            
            # 7-Day Vessel Activity Trend Graph
            st.subheader("📈 7-Day Vessel Activity Trend")
            
            def create_7day_vessel_activity_chart(vessel_data):
                """
                Create a 7-day vessel activity trend chart showing daily counts of arriving, departed, and in_port vessels.
                
                Args:
                    vessel_data (pd.DataFrame): Vessel data with status and timestamp columns
                    
                Returns:
                    plotly.graph_objects.Figure: Interactive line chart
                """
                try:
                    import plotly.graph_objects as go
                    from datetime import datetime, timedelta
                    
                    # Get the last 7 days
                    end_date = datetime.now().date()
                    start_date = end_date - timedelta(days=6)  # 7 days total including today
                    
                    # Create date range for the last 7 days
                    date_range = [start_date + timedelta(days=i) for i in range(7)]
                    
                    # Initialize daily counts
                    daily_counts = {
                        'dates': date_range,
                        'arriving': [0] * 7,
                        'departed': [0] * 7,
                        'in_port': [0] * 7
                    }
                    
                    if not vessel_data.empty and 'status' in vessel_data.columns:
                        # Find the best timestamp column to use
                        timestamp_col = None
                        for col in ['arrival_time', 'departure_time', 'timestamp']:
                            if col in vessel_data.columns:
                                timestamp_col = col
                                break
                        
                        if timestamp_col:
                            # Convert timestamp column to datetime if not already
                            vessel_data_copy = vessel_data.copy()
                            try:
                                vessel_data_copy[timestamp_col] = pd.to_datetime(vessel_data_copy[timestamp_col])
                                vessel_data_copy['date'] = vessel_data_copy[timestamp_col].dt.date
                                
                                # Count vessels by status for each day
                                for i, date in enumerate(date_range):
                                    day_data = vessel_data_copy[vessel_data_copy['date'] == date]
                                    
                                    daily_counts['arriving'][i] = len(day_data[day_data['status'] == 'arriving'])
                                    daily_counts['departed'][i] = len(day_data[day_data['status'] == 'departed'])
                                    daily_counts['in_port'][i] = len(day_data[day_data['status'] == 'in_port'])
                                    
                            except Exception as e:
                                st.warning(f"Could not process timestamp data: {str(e)}")
                    
                    # Create the plotly figure
                    fig = go.Figure()
                    
                    # Add lines for each vessel status
                    fig.add_trace(go.Scatter(
                        x=daily_counts['dates'],
                        y=daily_counts['arriving'],
                        mode='lines+markers',
                        name='Arriving',
                        line=dict(color='#1f77b4', width=3),
                        marker=dict(size=8)
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=daily_counts['dates'],
                        y=daily_counts['departed'],
                        mode='lines+markers',
                        name='Departed',
                        line=dict(color='#ff7f0e', width=3),
                        marker=dict(size=8)
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=daily_counts['dates'],
                        y=daily_counts['in_port'],
                        mode='lines+markers',
                        name='In Port',
                        line=dict(color='#2ca02c', width=3),
                        marker=dict(size=8)
                    ))
                    
                    # Update layout
                    fig.update_layout(
                        title="Daily Vessel Activity - Last 7 Days",
                        xaxis_title="Date",
                        yaxis_title="Number of Vessels",
                        height=400,
                        hovermode='x unified',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        ),
                        margin=dict(l=50, r=50, t=80, b=50)
                    )
                    
                    # Format x-axis to show dates nicely
                    fig.update_xaxes(
                        tickformat='%m/%d',
                        tickmode='array',
                        tickvals=daily_counts['dates']
                    )
                    
                    return fig
                    
                except Exception as e:
                    st.error(f"Error creating 7-day activity chart: {str(e)}")
                    return None
            
            # Display the 7-day activity chart
            try:
                activity_chart = create_7day_vessel_activity_chart(vessel_data)
                if activity_chart:
                    st.plotly_chart(activity_chart, use_container_width=True, key="7day_vessel_activity")
                else:
                    st.info("7-day vessel activity chart is temporarily unavailable.")
            except Exception as e:
                st.error(f"Error displaying 7-day activity chart: {str(e)}")
            
            # Detailed vessel table
            st.subheader("📋 Vessels activity - detailed look")
            
            # Add filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if ship_type_column in vessel_data.columns:
                    ship_types = ['All'] + list(vessel_data[ship_type_column].unique())
                    selected_type = st.selectbox("Filter by Ship Type", ship_types)
                else:
                    selected_type = 'All'
            
            with col2:
                if location_column in vessel_data.columns:
                    locations = ['All'] + list(vessel_data[location_column].unique())
                    selected_location = st.selectbox("Filter by Location", locations)
                else:
                    selected_location = 'All'
            
            with col3:
                if 'status' in vessel_data.columns:
                    statuses = ['All'] + sorted(list(vessel_data['status'].unique()))
                    selected_status = st.selectbox("Filter by Status", statuses)
                else:
                    selected_status = 'All'
            
            # Add Show All Columns checkbox
            show_all = st.checkbox("Show All Columns", value=False)
            
            
            # Apply filters
            filtered_data = vessel_data.copy()
            
            # Apply filters
            if selected_type != 'All' and ship_type_column in vessel_data.columns:
                filtered_data = filtered_data[filtered_data[ship_type_column] == selected_type]
            
            if selected_location != 'All' and location_column in vessel_data.columns:
                filtered_data = filtered_data[filtered_data[location_column] == selected_location]
            
            if selected_status != 'All' and 'status' in vessel_data.columns:
                filtered_data = filtered_data[filtered_data['status'] == selected_status]
            
            # Display table
            if not show_all:
                # Show only key columns including date/time information
                display_columns = []
                for col in ['vessel_name', 'ship_type', 'location', 'arrival_time', 'departure_time', 'timestamp', 'status']:
                    if col in filtered_data.columns:
                        display_columns.append(col)
                
                if display_columns:
                    # Create a copy for display
                    display_data = filtered_data[display_columns].copy()
                    
                    # Ensure datetime columns are properly formatted for sorting
                    datetime_columns = ['arrival_time', 'departure_time', 'timestamp']
                    column_config = {}
                    
                    for col in datetime_columns:
                        if col in display_data.columns:
                            # Convert to datetime if not already (preserve datetime objects for sorting)
                            try:
                                display_data[col] = pd.to_datetime(display_data[col])
                                # Configure column to display formatted datetime
                                column_config[col] = st.column_config.DatetimeColumn(
                                    col.replace('_', ' ').title(),
                                    format="YYYY-MM-DD HH:mm",
                                    help=f"Click column header to sort by {col.replace('_', ' ')}"
                                )
                            except:
                                # If conversion fails, keep original values
                                pass
                    
                    # Display dataframe with proper datetime sorting and formatting
                    st.dataframe(
                        display_data, 
                        use_container_width=True,
                        column_config=column_config
                    )
                else:
                    st.dataframe(filtered_data, use_container_width=True)
            else:
                st.dataframe(filtered_data, use_container_width=True)
            
            # Export functionality
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📥 Export to CSV"):
                    csv = filtered_data.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"vessel_arrivals_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                st.metric("Total Records", len(filtered_data))
        
        else:
            st.info("No vessel arrivals data available. Please check data sources.")
            
            # Show sample data structure
            st.subheader("📋 Expected Data Structure")
            sample_data = pd.DataFrame({
                'vessel_name': ['Sample Vessel 1', 'Sample Vessel 2'],
                'ship_type': ['Container Ship', 'Bulk Carrier'],
                'location': ['Kwai Tsing', 'Western Anchorage'],
                'arrival_time': [datetime.now(), datetime.now() - timedelta(hours=2)],
                'status': ['arrived', 'anchored']
            })
            st.dataframe(sample_data, use_container_width=True)

    # Analytics tab removed - content moved to bottom of Vessel Analytics tab (tab2)
    
    # COMMENTED OUT: Ships & Berths tab - functionality moved to Scenarios tab
    # with tab6:
    #     # Ships & Berths - Operational Impact Analysis
    #     st.subheader("🚢 Ships & Berths")
    #     st.markdown("Real-time analysis of ships and berths including queue management, berth utilization, and vessel tracking.")
    #     
    #     # Create tabs for different operational views
    #     ops_tab1, ops_tab2, ops_tab3 = st.tabs(["🚢 Ship Queue", "🏗️ Berth Utilization", "📊 Live Operations"])
    #     
    #     with ops_tab1:
    #         st.subheader("🚢 Ship Queue Analysis")
    #         
    #         # Get simulation data if available
    #         simulation_data = getattr(st.session_state, 'simulation_data', None)
    #         
    #         if simulation_data and hasattr(simulation_data, 'ship_queue'):
    #             # Real simulation data
    #             queue_data = simulation_data.ship_queue
    #             
    #             # Queue metrics
    #             queue_col1, queue_col2, queue_col3, queue_col4 = st.columns(4)
    #             with queue_col1:
    #                 st.metric("Ships in Queue", len(queue_data))
    #             with queue_col2:
    #                 avg_wait = sum(ship.get('waiting_time', 0) for ship in queue_data) / max(len(queue_data), 1)
    #                 st.metric("Avg Wait Time", f"{avg_wait:.1f} hrs")
    #             with queue_col3:
    #                 priority_ships = sum(1 for ship in queue_data if ship.get('priority', 'normal') == 'high')
    #                 st.metric("Priority Ships", priority_ships)
    #             with queue_col4:
    #                 total_cargo = sum(ship.get('cargo_volume', 0) for ship in queue_data)
    #                 st.metric("Total Cargo", f"{total_cargo:,.0f} TEU")
    #             
    #             # Queue visualization
    #             if queue_data:
    #                 queue_df = pd.DataFrame(queue_data)
    #                 
    #                 # Queue timeline chart
    #                 import plotly.express as px
    #                 fig_queue = px.bar(
    #                     queue_df,
    #                     x='ship_id',
    #                     y='waiting_time',
    #                     color='ship_type',
    #                     title='Ship Queue - Waiting Times',
    #                     labels={'waiting_time': 'Waiting Time (hours)', 'ship_id': 'Ship ID'}
    #                 )
    #                 st.plotly_chart(fig_queue, use_container_width=True)
    #                 
    #                 # Detailed queue table
    #                 st.subheader("📋 Queue Details")
    #                 display_columns = ['ship_id', 'ship_type', 'arrival_time', 'waiting_time', 'cargo_volume', 'priority']
    #                 available_columns = [col for col in display_columns if col in queue_df.columns]
    #                 st.dataframe(queue_df[available_columns], use_container_width=True)
    #             else:
    #                 st.info("No ships currently in queue")
    #         else:
    #             # Sample data for demonstration
    #             st.info("📊 Using sample data - Start simulation for real-time queue data")
    #             
    #             # Generate sample queue data
    #             import numpy as np
    #             sample_queue = [
    #                 {'ship_id': f'SHIP-{i:03d}', 'ship_type': np.random.choice(['Container', 'Bulk', 'Tanker']),
    #                  'arrival_time': f'{np.random.randint(0, 24):02d}:00', 'waiting_time': np.random.exponential(2),
    #                  'cargo_volume': np.random.randint(500, 3000), 'priority': np.random.choice(['normal', 'high'], p=[0.8, 0.2])}
    #                 for i in range(np.random.randint(5, 15))
    #             ]
    #             
    #             # Sample metrics
    #             queue_col1, queue_col2, queue_col3, queue_col4 = st.columns(4)
    #             with queue_col1:
    #                 st.metric("Ships in Queue", len(sample_queue))
    #             with queue_col2:
    #                 avg_wait = sum(ship['waiting_time'] for ship in sample_queue) / len(sample_queue)
    #                 st.metric("Avg Wait Time", f"{avg_wait:.1f} hrs")
    #             with queue_col3:
    #                 priority_ships = sum(1 for ship in sample_queue if ship['priority'] == 'high')
    #                 st.metric("Priority Ships", priority_ships)
    #             with queue_col4:
    #                 total_cargo = sum(ship['cargo_volume'] for ship in sample_queue)
    #                 st.metric("Total Cargo", f"{total_cargo:,.0f} TEU")
    #             
    #             # Sample queue visualization
    #             queue_df = pd.DataFrame(sample_queue)
    #             import plotly.express as px
    #             fig_queue = px.bar(
    #                 queue_df,
    #                 x='ship_id',
    #                 y='waiting_time',
    #                 color='ship_type',
    #                 title='Ship Queue - Waiting Times (Sample Data)',
    #                 labels={'waiting_time': 'Waiting Time (hours)', 'ship_id': 'Ship ID'}
    #             )
    #             st.plotly_chart(fig_queue, use_container_width=True)
    #             
    #             # Sample queue table
    #             st.subheader("📋 Queue Details")
    #             st.dataframe(queue_df, use_container_width=True)
    #     
    #     with ops_tab2:
    #         st.subheader("🏗️ Berth Utilization Analysis")
    #         st.info("Berth utilization analysis will be displayed here when simulation is running.")
    #         
    #         # Sample berth data
    #         berth_data = {
    #             'Berth ID': ['B001', 'B002', 'B003', 'B004', 'B005'],
    #             'Status': ['Occupied', 'Available', 'Occupied', 'Maintenance', 'Occupied'],
    #             'Current Ship': ['SHIP-001', '-', 'SHIP-003', '-', 'SHIP-005'],
    #             'Utilization %': [85, 0, 92, 0, 78]
    #         }
    #         berth_df = pd.DataFrame(berth_data)
    #         st.dataframe(berth_df, use_container_width=True)
    #     
    #     with ops_tab3:
    #         st.subheader("📊 Live Operations")
    #         st.info("Live operations dashboard will be displayed here when simulation is running.")
    #         
    #         # Sample operations metrics
    #         ops_col1, ops_col2, ops_col3 = st.columns(3)
    #         with ops_col1:
    #             st.metric("Active Operations", "12")
    #         with ops_col2:
    #             st.metric("Throughput Today", "2,450 TEU")
    #         with ops_col3:
    #             st.metric("Efficiency Rate", "87.5%")
    
    with tab4:
        if use_consolidated:
            # Initialize and render the consolidated scenarios tab
            consolidated_tab = ConsolidatedScenariosTab()
            # Get current scenario from session state
            current_scenario = st.session_state.get('scenario', 'normal')
            scenario_data = {'name': current_scenario}
            consolidated_tab.render_consolidated_tab(scenario_data)
        else:
            # Original Scenario Analysis tab content
            st.subheader("🎯 Scenario Analysis & Comparison")
            st.markdown("Compare different operational scenarios and their impact on port performance")
            
            # Scenario selection for comparison
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Select Scenarios to Compare**")
                available_scenarios = list_available_scenarios()
                # Create display names with emojis
                scenario_display_options = [get_scenario_display_name(scenario) for scenario in available_scenarios]
                
                scenario1_display = st.selectbox("Scenario 1", scenario_display_options, key="scenario1_select")
                scenario2_display = st.selectbox("Scenario 2", scenario_display_options, key="scenario2_select", index=1 if len(scenario_display_options) > 1 else 0)
                
                # Extract actual scenario keys for processing
                scenario1 = get_scenario_key_from_display(scenario1_display)
                scenario2 = get_scenario_key_from_display(scenario2_display)
            
            with col2:
                st.write("**Comparison Parameters**")
                compare_metrics = st.multiselect(
                    "Metrics to Compare",
                    ["Ship Arrival Rate", "Processing Efficiency", "Berth Utilization", "Waiting Times"],
                    default=["Ship Arrival Rate", "Processing Efficiency"]
                )
            
            if st.button("🔄 Run Scenario Comparison", type="primary"):
                with st.spinner("Running scenario comparison..."):
                    # Simulate comparison logic
                    comparison_data = {
                        'Scenario': [scenario1, scenario2],
                        'Ship Arrival Rate': [85.2, 92.1],
                        'Processing Efficiency': [78.5, 82.3],
                        'Berth Utilization': [72.1, 76.8],
                        'Waiting Times': [2.3, 1.9]
                    }
                    
                    st.session_state.scenario_comparison_data = comparison_data
                    st.success("Scenario comparison completed!")
            
            # Display comparison results if available
            if hasattr(st.session_state, 'scenario_comparison_data'):
                st.subheader("📊 Comparison Results")
                
                comparison_df = pd.DataFrame(st.session_state.scenario_comparison_data)
                st.dataframe(comparison_df, use_container_width=True)
                
                # Visualization
                if "Ship Arrival Rate" in compare_metrics:
                    import plotly.express as px
                    fig = px.bar(comparison_df, x='Scenario', y='Ship Arrival Rate', 
                               title="Ship Arrival Rate by Scenario")
                    st.plotly_chart(fig, use_container_width=True)
                
                if "Processing Efficiency" in compare_metrics:
                    fig = px.bar(comparison_df, x='Scenario', y='Processing Efficiency', 
                               title="Processing Efficiency by Scenario")
                    st.plotly_chart(fig, use_container_width=True)
    
    # Unified Simulations tab - always tab8 regardless of mode
    # Unified Simulations tab - COMMENTED OUT
    # with tab8:
    #     # Initialize unified simulations tab
    #     if 'unified_simulations_tab' not in st.session_state:
    #         st.session_state.unified_simulations_tab = UnifiedSimulationsTab()
    #     
    #     # Render the unified simulations interface
    #     st.session_state.unified_simulations_tab.render()
    
    # Settings tab - now tab5 (was tab6, originally tab9)
    with tab5:
        st.subheader("⚙️ Settings")
        st.markdown("Configure simulation parameters and system settings")
        
        # Dashboard Preferences
        st.subheader("🎛️ Dashboard Preferences")
        
        pref_col1, pref_col2 = st.columns(2)
        
        with pref_col1:
            st.write("**Tab Structure**")
            use_consolidated_checkbox = st.checkbox(
                "Use consolidated scenarios tab", 
                value=st.session_state.get('use_consolidated_scenarios', True),
                help="Switch between original tab structure and new consolidated scenarios tab"
            )
            
            if use_consolidated_checkbox != st.session_state.get('use_consolidated_scenarios', True):
                st.session_state.use_consolidated_scenarios = use_consolidated_checkbox
                st.rerun()
            
            # Section navigation checkbox removed as per demo refinement plan
        
        with pref_col2:
            st.write("**Section Behavior**")
            sections_expanded = st.checkbox(
                "Expand sections by default", 
                value=st.session_state.get('scenarios_sections_expanded', False),
                help="Default expanded state for scenario sections"
            )
            st.session_state.scenarios_sections_expanded = sections_expanded
            
            # Removed 'Remember section states' checkbox - no longer needed after removing section navigation
        
        # Simulation settings
        st.subheader("🔧 Simulation Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Performance Settings**")
            auto_refresh = st.checkbox("Auto-refresh dashboard", value=True)
            refresh_interval = st.slider("Refresh interval (seconds)", 1, 30, 5)
            
            st.write("**Data Settings**")
            use_real_data = st.checkbox("Use real-time data", value=True)
            cache_duration = st.slider("Cache duration (minutes)", 1, 60, 10)
        
        with col2:
            st.write("**Display Settings**")
            show_debug_info = st.checkbox("Show debug information", value=False)
            chart_theme = st.selectbox("Chart theme", ["plotly", "plotly_white", "plotly_dark"], index=0)
            
            st.write("**Export Settings**")
            default_export_format = st.selectbox("Default export format", ["CSV", "Excel", "JSON"], index=0)
        
        # System information
        st.subheader("📊 System Information")
        
        info_col1, info_col2, info_col3 = st.columns(3)
        
        with info_col1:
            st.metric("Dashboard Version", "1.0.0")
            st.metric("Streamlit Version", st.__version__)
        
        with info_col2:
            st.metric("Active Sessions", "1")
            st.metric("Uptime", "Running")
        
        with info_col3:
            st.metric("Data Sources", "3")
            st.metric("Last Update", datetime.now().strftime("%H:%M:%S"))
        
        # Reset options
        st.subheader("🔄 Reset Options")
        
        reset_col1, reset_col2, reset_col3, reset_col4 = st.columns(4)
        
        with reset_col1:
            if st.button("🗑️ Clear Cache"):
                st.cache_data.clear()
                st.success("Cache cleared successfully!")
        
        with reset_col2:
            if st.button("🔄 Reset Session"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.success("Session reset successfully!")
                st.rerun()
        
        with reset_col3:
            # Reset Simulation button removed - no longer needed after removing simulation settings
            st.empty()
        
        with reset_col4:
            if st.button("📋 Reset Sections"):
                if 'consolidated_sections_state' in st.session_state:
                    del st.session_state['consolidated_sections_state']
                st.success("Section states reset successfully!")
                st.rerun()
    
    # Additional tabs for original structure
    if not use_consolidated:
        with tab5:
            st.subheader("📊 Performance Analytics")
            st.markdown("Detailed performance metrics and analytics")
            st.info("Performance analytics content would be displayed here.")
        
        with tab6:
            st.subheader("📦 Cargo Analysis")
            st.markdown("Advanced cargo flow and logistics analysis")
            st.info("Cargo analysis content would be displayed here.")



if __name__ == "__main__":
    main()