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

from hk_port_digital_twin.src.utils.data_loader import RealTimeDataConfig, get_real_time_manager, load_container_throughput, load_vessel_arrivals, load_berth_configurations, initialize_vessel_data_pipeline, load_all_vessel_data, get_comprehensive_vessel_analysis, load_combined_vessel_data
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
# from hk_port_digital_twin.src.dashboard.unified_simulations_tab import UnifiedSimulationsTab  # Commented out - tab hidden

try:
    from hk_port_digital_twin.src.dashboard.marine_traffic_integration import MarineTrafficIntegration
except ImportError:
    MarineTrafficIntegration = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(threadName)s - %(message)s')


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
            # Fallback to sample data if real data loading fails
            print(f"Warning: Could not load real throughput data: {e}")
            timeline_data = {
                'time': pd.date_range(start=datetime.now() - timedelta(hours=24),
                                     end=datetime.now(), freq='h'),
                'containers_processed': np.random.randint(10, 100, 25),
                'ships_processed': np.random.randint(1, 8, 25)
            }
            timeline_data = pd.DataFrame(timeline_data)
    else:
        # Fallback to sample data if function not available
        timeline_data = {
            'time': pd.date_range(start=datetime.now() - timedelta(hours=24),
                                 end=datetime.now(), freq='h'),
            'containers_processed': np.random.randint(10, 100, 25),
            'ships_processed': np.random.randint(1, 8, 25)
        }
        timeline_data = pd.DataFrame(timeline_data)

    # Sample ship queue data (ships waiting for berths)
    num_ships_in_queue = int(3 * params['queue_multiplier'])
    ship_queue_data = {
        'ship_id': [f'SHIP_{i:03d}' for i in range(1, num_ships_in_queue + 1)],
        'name': [f'Ship {i}' for i in range(1, num_ships_in_queue + 1)],
        'ship_type': np.random.choice(['container', 'bulk'], num_ships_in_queue) if num_ships_in_queue > 0 else [],
        'arrival_time': [datetime.now() - timedelta(hours=i) for i in range(num_ships_in_queue, 0, -1)],
        'containers': np.random.randint(100, 300, num_ships_in_queue) if num_ships_in_queue > 0 else [],
        'size_teu': np.random.randint(5000, 15000, num_ships_in_queue) if num_ships_in_queue > 0 else [],
        'waiting_time': np.random.uniform(1.0, 5.0, num_ships_in_queue) * params['waiting_time_multiplier'] if num_ships_in_queue > 0 else [],
        'priority': np.random.choice(['high', 'medium', 'low'], num_ships_in_queue) if num_ships_in_queue > 0 else []
    }
    
    # Sample waiting time data
    waiting_data = {
        'ship_id': [f'SHIP_{i:03d}' for i in range(1, 21)],
        'waiting_time': np.random.exponential(2, 20) * params['waiting_time_multiplier'],
        'ship_type': np.random.choice(['container', 'bulk', 'mixed'], 20)
    }

    # Sample KPI data
    kpi_data = {
        'metric': ['Average Waiting Time', 'Berth Utilization', 'Throughput Rate', 'Queue Length'],
        'value': [2.5 * params['waiting_time_multiplier'], np.mean(params['utilization_range']), 85, 3 * params['queue_multiplier']],
        'unit': ['hours', '%', 'containers/hour', 'ships'],
        'target': [2.0, 80, 90, 2],
        'status': ['warning', 'good', 'good', 'warning']
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


def create_sidebar():
    """Create sidebar with simulation controls"""
    st.sidebar.title("🚢 Port Control Panel")
    
    # Scenario Management
    st.sidebar.subheader("📋 Scenario Management")
    
    # Initialize scenario manager if not in session state
    if 'scenario_manager' not in st.session_state:
        st.session_state.scenario_manager = ScenarioManager()
    
    scenario_manager = st.session_state.scenario_manager
    
    # Scenario selection
    available_scenarios = list_available_scenarios()
    current_scenario = scenario_manager.get_current_scenario()
    
    selected_scenario = st.sidebar.selectbox(
        "Select Scenario",
        available_scenarios,
        index=available_scenarios.index(current_scenario) if current_scenario in available_scenarios else 0,
        help="Choose operational scenario based on expected conditions"
    )
    
    # Update scenario if changed
    if selected_scenario != current_scenario:
        scenario_manager.set_scenario(selected_scenario)
        st.session_state.scenario = selected_scenario  # Update session state
        st.sidebar.success(f"Scenario changed to: {selected_scenario}")
        st.rerun()
    
    # Auto-detection toggle
    auto_detect = st.sidebar.checkbox(
        "Auto-detect scenario",
        value=scenario_manager.auto_detection_enabled,
        help="Automatically select scenario based on current date and historical patterns"
    )
    
    if auto_detect != scenario_manager.auto_detection_enabled:
        if auto_detect:
            scenario_manager.enable_auto_detection()
        else:
            scenario_manager.disable_auto_detection()
    
    # Display scenario info
    scenario_info = scenario_manager.get_scenario_info()
    if scenario_info:
        with st.sidebar.expander("📊 Scenario Details", expanded=False):
            st.write(f"**Description:** {scenario_info.get('description', 'N/A')}")
            st.write(f"**Ship Arrival Rate:** {scenario_info.get('ship_arrival_multiplier', 1.0):.1f}x")
            st.write(f"**Container Volume:** {scenario_info.get('container_volume_multiplier', 1.0):.1f}x")
            st.write(f"**Processing Efficiency:** {scenario_info.get('processing_efficiency_factor', 1.0):.1f}x")
    
    # Historical Data Integration section removed as per demo refinement plan
    
    # Simulation Settings section removed as per demo refinement plan
    # This includes duration slider, arrival rate controls, start/stop buttons, and status display


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
    # Page configuration
    st.set_page_config(
        page_title="Hong Kong Port Digital Twin",
        page_icon="🚢",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state
    initialize_session_state()

    # --- Sidebar ---
    create_sidebar()
    
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
        # New consolidated structure with Settings as tab8 (Unified Simulations hidden)
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
            "📊 Overview", "🚢 Vessel Analytics", "📦 Cargo Statistics", "🛳️ Live Vessels", 
            "📈 Analytics", "🚢 Ships & Berths", "🎯 Scenarios", "⚙️ Settings"
        ])
    else:
        # Original structure with Settings as tab8 (Unified Simulations hidden)
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
            "📊 Overview", "🚢 Vessel Analytics", "📦 Cargo Statistics", "🛳️ Live Vessels",
            "📈 Analytics", "🚢 Ships & Berths", "🎯 Scenarios", "⚙️ Settings",
            "📊 Performance Analytics", "📦 Cargo Analysis"
        ])
    
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
                kpi_dict = {
                    'average_waiting_time': 2.5,
                    'average_berth_utilization': 0.75,
                    'total_ships_processed': 85,
                    'total_containers_processed': 1200,
                    'average_queue_length': 3
                }
                create_kpi_summary_chart(kpi_dict)
        
        # Metrics section
        st.subheader("📊 Key Metrics")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Enhanced metrics with real vessel data
                vessel_analysis = data.get('vessel_queue_analysis', {})
                
                if vessel_analysis:
                    active_vessels = vessel_analysis.get('current_status', {}).get('active_vessels', 0)
                    st.metric("Live Vessels", active_vessels)
                else:
                    # Safe access to queue data with fallback
                    queue_length = len(data.get('queue', [])) if 'queue' in data and data['queue'] is not None else 0
                    st.metric("Active Ships", queue_length)
                
                # Safe access to berths data with fallback
                berths_df = data.get('berths', pd.DataFrame())
                if not berths_df.empty and 'status' in berths_df.columns:
                    available_berths = len(berths_df[berths_df['status'] == 'available'])
                else:
                    available_berths = 0
                st.metric("Available Berths", available_berths)
                
                # Show recent arrivals if available
                if vessel_analysis and 'recent_activity' in vessel_analysis:
                    arrivals_24h = vessel_analysis['recent_activity'].get('arrivals_last_24h', 0)
                    st.metric("24h Arrivals", arrivals_24h)
                else:
                    st.metric("Avg Waiting Time", "2.5 hrs")
                
                st.metric("Utilization Rate", "75%")
        
        # Port Layout
        st.subheader("Port Layout")
        if create_port_layout_chart is not None and 'berths' in data and data['berths'] is not None:
            fig_layout = create_port_layout_chart(data['berths'])
            st.plotly_chart(fig_layout, use_container_width=True, key="port_layout_chart")
        else:
            if 'berths' not in data or data['berths'] is None:
                st.warning("Berth data not available. Please check data loading.")
            else:
                st.info("Port layout visualization not available. Please ensure visualization module is properly installed.")
    
    with tab2:
        # Vessel Analytics tab (same for both consolidated and original modes)
        st.subheader("🚢 Vessel Analytics Dashboard")
        st.markdown("Real-time analysis of vessel distribution and activity patterns")
        
        try:
            # Load comprehensive vessel analysis data (includes timestamps from all XML files)
            vessel_analysis = get_comprehensive_vessel_analysis()
            
            if vessel_analysis and vessel_analysis.get('data_summary', {}).get('total_vessels', 0) > 0:
                # Display data summary
                data_summary = vessel_analysis.get('data_summary', {})
                st.write(f"**Data Summary:** {data_summary.get('total_vessels', 0)} vessels loaded from {data_summary.get('files_processed', 0)} files")
                
                # Show data sources
                data_sources = data_summary.get('data_sources', [])
                if data_sources:
                    st.write(f"**Data Sources:** {', '.join([src.replace('.xml', '') for src in data_sources])}")
                
                # Location breakdown
                location_breakdown = vessel_analysis.get('location_type_breakdown', {})
                if location_breakdown:
                    st.write(f"**Locations:** {len(location_breakdown)} unique location types")
                
                # Ship category breakdown
                category_breakdown = vessel_analysis.get('ship_category_breakdown', {})
                if category_breakdown:
                    st.write(f"**Ship Categories:** {len(category_breakdown)} different types")
                
                # Recent activity
                recent_activity = vessel_analysis.get('recent_activity', {})
                if recent_activity:
                    st.write(f"**Recent Activity:** {recent_activity.get('vessels_last_24h', 0)} vessels in last 24 hours")
                
                # Display timestamp if available
                from hk_port_digital_twin.src.dashboard.vessel_charts import _extract_latest_timestamp
                latest_timestamp = _extract_latest_timestamp(vessel_analysis)
                if latest_timestamp:
                    st.caption(f"📅 Last updated at: {latest_timestamp}")
                else:
                    st.caption("📅 Last updated at: Not available")
                
                # Render the vessel analytics dashboard with comprehensive analysis data
                render_vessel_analytics_dashboard(vessel_analysis)
                
            else:
                st.warning("No vessel data available for analytics.")
                st.info("Please ensure vessel data files are properly loaded from the raw_data directory.")
                
        except Exception as e:
            st.error(f"Error loading vessel analytics: {str(e)}")
            st.info("Using sample data for demonstration purposes.")
            
            # Fallback to sample data with proper structure
            sample_vessel_analysis = {
                'data_summary': {
                    'total_vessels': 3,
                    'files_processed': 1,
                    'data_sources': ['sample_data']
                },
                'location_type_breakdown': {'berth': 2, 'anchorage': 1},
                'ship_category_breakdown': {'container': 2, 'bulk_carrier': 1},
                'file_breakdown': {
                    'sample_data': {
                        'earliest_timestamp': (datetime.now() - timedelta(hours=8)).isoformat(),
                        'latest_timestamp': (datetime.now() - timedelta(hours=2)).isoformat()
                    }
                },
                'analysis_timestamp': datetime.now().isoformat()
            }
            render_vessel_analytics_dashboard(sample_vessel_analysis)

    
    with tab3:
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
            st.metric("Tables Processed", tables_processed)
        with col2:
            st.metric("Analysis Status", "✅ Complete" if cargo_analysis else "❌ Failed")
        with col3:
            analysis_sections = len([k for k in cargo_analysis.keys() if k.endswith('_analysis')])
            st.metric("Analysis Sections", analysis_sections)
        with col4:
            timestamp = cargo_analysis.get('data_summary', {}).get('analysis_timestamp', datetime.now().isoformat())
            st.metric("Analysis Date", timestamp[:10] if timestamp else datetime.now().strftime("%Y-%m-%d"))

        # Create tabs for different analysis sections
        cargo_tab1, cargo_tab2, cargo_tab3, cargo_tab4, cargo_tab5, cargo_tab6 = st.tabs([
            "📊 Shipment Types", "🚢 Transport Modes", "📈 Time Series", "🔮 Forecasting", "📦 Cargo Types", "📍 Locations"
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
            else:
                st.info("No time series data available")
                st.warning("Please ensure the Port Cargo Statistics CSV files are available in the raw_data directory.")

        with cargo_tab4:
            st.subheader("Forecasting")
            
            # Get forecasting data from cargo analysis
            forecasting_data = cargo_analysis.get('forecasting_analysis', {})
            
            if forecasting_data:
                st.write("**Forecast Summary**")
                
                # Display forecast metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    forecast_period = forecasting_data.get('forecast_period', 'N/A')
                    st.metric("Forecast Period", forecast_period)
                
                with col2:
                    model_accuracy = forecasting_data.get('model_accuracy', 0)
                    st.metric("Model Accuracy", f"{model_accuracy:.1%}" if model_accuracy else "N/A")
                
                with col3:
                    trend_direction = forecasting_data.get('trend_direction', 'stable')
                    st.metric("Trend Direction", trend_direction.title())
                
                # Display forecast charts if available
                forecast_charts = forecasting_data.get('charts', {})
                if forecast_charts:
                    for chart_name, chart_data in forecast_charts.items():
                        st.write(f"**{chart_name.replace('_', ' ').title()}**")
                        if isinstance(chart_data, pd.DataFrame):
                            st.line_chart(chart_data)
                        else:
                            st.info(f"Chart data for {chart_name} not available")
            else:
                st.info("No forecasting analysis available")
                st.warning("Please ensure the cargo analysis module is properly configured.")

        with cargo_tab5:
            st.subheader("Cargo Types")
            
            # Get cargo type data from analysis
            cargo_types_data = cargo_analysis.get('cargo_types_analysis', {})
            
            if cargo_types_data:
                # Display cargo type breakdown
                breakdown = cargo_types_data.get('breakdown', {})
                if breakdown:
                    st.write("**Cargo Type Distribution**")
                    
                    # Create DataFrame for display
                    cargo_df = pd.DataFrame(list(breakdown.items()), 
                                          columns=['Cargo Type', 'Volume (000 tonnes)'])
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.dataframe(cargo_df, use_container_width=True)
                    
                    with col2:
                        # Create pie chart
                        import plotly.express as px
                        fig = px.pie(cargo_df, values='Volume (000 tonnes)', names='Cargo Type',
                                   title="Cargo Type Distribution")
                        st.plotly_chart(fig, use_container_width=True)
                
                # Display trends if available
                trends = cargo_types_data.get('trends', {})
                if trends:
                    st.write("**Cargo Type Trends**")
                    for cargo_type, trend_data in trends.items():
                        if isinstance(trend_data, pd.DataFrame):
                            st.write(f"**{cargo_type.title()}**")
                            st.line_chart(trend_data)
            else:
                st.info("No cargo types analysis available")
                st.warning("Please ensure the cargo analysis module is properly configured.")

        with cargo_tab6:
            st.subheader("Locations")
            
            # Get location data from analysis
            locations_data = cargo_analysis.get('locations_analysis', {})
            
            if locations_data:
                # Display location breakdown
                breakdown = locations_data.get('breakdown', {})
                if breakdown:
                    st.write("**Handling Location Distribution**")
                    
                    # Create DataFrame for display
                    location_df = pd.DataFrame(list(breakdown.items()), 
                                             columns=['Location', 'Volume (000 tonnes)'])
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.dataframe(location_df, use_container_width=True)
                    
                    with col2:
                        # Create bar chart
                        import plotly.express as px
                        fig = px.bar(location_df, x='Location', y='Volume (000 tonnes)',
                                   title="Volume by Handling Location")
                        fig.update_xaxes(tickangle=45)
                        st.plotly_chart(fig, use_container_width=True)
                
                # Display location trends if available
                trends = locations_data.get('trends', {})
                if trends:
                    st.write("**Location Trends**")
                    for location, trend_data in trends.items():
                        if isinstance(trend_data, pd.DataFrame):
                            st.write(f"**{location}**")
                            st.line_chart(trend_data)
            else:
                st.info("No locations analysis available")
                st.warning("Please ensure the cargo analysis module is properly configured.")
    
    with tab4:
        st.subheader("🚢 Live Vessel Arrivals")
        st.markdown("Real-time vessel arrival data and analytics for Hong Kong port")
        
        # Load combined vessel data (both arriving and arrived vessels)
        try:
            vessel_data = load_combined_vessel_data()
            if vessel_data is None or vessel_data.empty:
                st.warning("⚠️ No vessel data available")
                st.info("Please ensure vessel data files are available in the data directory.")
                vessel_data = pd.DataFrame()
        except Exception as e:
            st.error(f"Error loading combined vessel data: {str(e)}")
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
            
            # Recent activity
            st.subheader("⏰ Recent Activity")
            
            # Simulate recent arrivals data
            current_time = datetime.now()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                arrivals_6h = max(0, len(vessel_data) // 4)
                st.metric("Arrivals (6h)", arrivals_6h)
            
            with col2:
                arrivals_12h = max(0, len(vessel_data) // 3)
                st.metric("Arrivals (12h)", arrivals_12h)
            
            with col3:
                arrivals_24h = max(0, len(vessel_data) // 2)
                st.metric("Arrivals (24h)", arrivals_24h)
            
            with col4:
                st.write("**Activity Trend**")
                # Create a simple trend chart
                import numpy as np
                import plotly.graph_objects as go
                
                hours = list(range(24))
                arrivals = [max(0, int(len(vessel_data) * (0.3 + 0.7 * abs(np.sin(h/4))))) for h in hours]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=hours, y=arrivals, mode='lines+markers', name='Arrivals'))
                fig.update_layout(
                    title="24h Arrival Trend",
                    xaxis_title="Hour",
                    yaxis_title="Arrivals",
                    height=200,
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig, use_container_width=True, key="activity_trend_chart")
            
            # Detailed vessel table
            st.subheader("📋 Arriving and Departing Vessels - Detailed Information")
            
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
                show_all = st.checkbox("Show All Columns", value=False)
            
            # Apply filters
            filtered_data = vessel_data.copy()
            
            if selected_type != 'All' and ship_type_column in vessel_data.columns:
                filtered_data = filtered_data[filtered_data[ship_type_column] == selected_type]
            
            if selected_location != 'All' and location_column in vessel_data.columns:
                filtered_data = filtered_data[filtered_data[location_column] == selected_location]
            
            # Display table
            if not show_all:
                # Show only key columns
                display_columns = []
                for col in ['vessel_name', 'ship_type', 'location', 'arrival_time', 'status']:
                    if col in filtered_data.columns:
                        display_columns.append(col)
                
                if display_columns:
                    st.dataframe(filtered_data[display_columns], use_container_width=True)
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

    with tab5:
        st.subheader("Analytics")
        
        # Check if data is properly loaded
        if not data or 'berths' not in data:
            st.error("❌ Data loading failed. Please check the scenario selection and try again.")
            st.info("💡 Try switching to a different scenario or refreshing the page.")
            return
        
        # Data Export Section
        st.subheader("📥 Data Export")
        export_col1, export_col2, export_col3, export_col4 = st.columns(4)
        
        with export_col1:
            # Export berth data
            berth_csv = data['berths'].to_csv(index=False)
            st.download_button(
                label="📊 Export Berth Data",
                data=berth_csv,
                file_name=f"berth_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with export_col2:
            # Export queue data
            queue_csv = data['queue'].to_csv(index=False)
            st.download_button(
                label="🚢 Export Queue Data",
                data=queue_csv,
                file_name=f"queue_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with export_col3:
            # Export timeline data
            timeline_csv = data['timeline'].to_csv(index=False)
            st.download_button(
                label="📈 Export Timeline Data",
                data=timeline_csv,
                file_name=f"timeline_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with export_col4:
            # Export all data as JSON
            import json
            export_data = {
                'berths': data['berths'].to_dict('records'),
                'queue': data['queue'].to_dict('records'),
                'timeline': data['timeline'].to_dict('records'),
                'waiting': data['waiting'].to_dict('records'),
                'kpis': data['kpis'].to_dict('records'),
                'export_timestamp': datetime.now().isoformat()
            }
            json_data = json.dumps(export_data, indent=2, default=str)
            st.download_button(
                label="📋 Export All (JSON)",
                data=json_data,
                file_name=f"port_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Throughput Timeline")
            if create_throughput_timeline is not None:
                fig_timeline = create_throughput_timeline(data['timeline'])
                st.plotly_chart(fig_timeline, use_container_width=True, key="main_throughput_timeline_chart")
            else:
                st.warning("Throughput timeline visualization not available. Please check visualization module import.")
                st.dataframe(data['timeline'], use_container_width=True)
        
        with col2:
            st.subheader("Waiting Time Distribution")
            # Convert DataFrame to list for visualization
            waiting_times_list = data['waiting']['waiting_time'].tolist()
            if create_waiting_time_distribution is not None:
                fig_waiting = create_waiting_time_distribution(waiting_times_list)
                st.plotly_chart(fig_waiting, use_container_width=True, key="main_waiting_time_chart")
            else:
                st.warning("Waiting time distribution visualization not available. Please check visualization module import.")
                st.dataframe(data['waiting'], use_container_width=True)
    
    with tab6:
        # Ships & Berths - Operational Impact Analysis
        st.subheader("🚢 Ships & Berths")
        st.markdown("Real-time analysis of ships and berths including queue management, berth utilization, and vessel tracking.")
        
        # Create tabs for different operational views
        ops_tab1, ops_tab2, ops_tab3 = st.tabs(["🚢 Ship Queue", "🏗️ Berth Utilization", "📊 Live Operations"])
        
        with ops_tab1:
            st.subheader("🚢 Ship Queue Analysis")
            
            # Get simulation data if available
            simulation_data = getattr(st.session_state, 'simulation_data', None)
            
            if simulation_data and hasattr(simulation_data, 'ship_queue'):
                # Real simulation data
                queue_data = simulation_data.ship_queue
                
                # Queue metrics
                queue_col1, queue_col2, queue_col3, queue_col4 = st.columns(4)
                with queue_col1:
                    st.metric("Ships in Queue", len(queue_data))
                with queue_col2:
                    avg_wait = sum(ship.get('waiting_time', 0) for ship in queue_data) / max(len(queue_data), 1)
                    st.metric("Avg Wait Time", f"{avg_wait:.1f} hrs")
                with queue_col3:
                    priority_ships = sum(1 for ship in queue_data if ship.get('priority', 'normal') == 'high')
                    st.metric("Priority Ships", priority_ships)
                with queue_col4:
                    total_cargo = sum(ship.get('cargo_volume', 0) for ship in queue_data)
                    st.metric("Total Cargo", f"{total_cargo:,.0f} TEU")
                
                # Queue visualization
                if queue_data:
                    queue_df = pd.DataFrame(queue_data)
                    
                    # Queue timeline chart
                    import plotly.express as px
                    fig_queue = px.bar(
                        queue_df,
                        x='ship_id',
                        y='waiting_time',
                        color='ship_type',
                        title='Ship Queue - Waiting Times',
                        labels={'waiting_time': 'Waiting Time (hours)', 'ship_id': 'Ship ID'}
                    )
                    st.plotly_chart(fig_queue, use_container_width=True)
                    
                    # Detailed queue table
                    st.subheader("📋 Queue Details")
                    display_columns = ['ship_id', 'ship_type', 'arrival_time', 'waiting_time', 'cargo_volume', 'priority']
                    available_columns = [col for col in display_columns if col in queue_df.columns]
                    st.dataframe(queue_df[available_columns], use_container_width=True)
                else:
                    st.info("No ships currently in queue")
            else:
                # Sample data for demonstration
                st.info("📊 Using sample data - Start simulation for real-time queue data")
                
                # Generate sample queue data
                import numpy as np
                sample_queue = [
                    {'ship_id': f'SHIP-{i:03d}', 'ship_type': np.random.choice(['Container', 'Bulk', 'Tanker']),
                     'arrival_time': f'{np.random.randint(0, 24):02d}:00', 'waiting_time': np.random.exponential(2),
                     'cargo_volume': np.random.randint(500, 3000), 'priority': np.random.choice(['normal', 'high'], p=[0.8, 0.2])}
                    for i in range(np.random.randint(5, 15))
                ]
                
                # Sample metrics
                queue_col1, queue_col2, queue_col3, queue_col4 = st.columns(4)
                with queue_col1:
                    st.metric("Ships in Queue", len(sample_queue))
                with queue_col2:
                    avg_wait = sum(ship['waiting_time'] for ship in sample_queue) / len(sample_queue)
                    st.metric("Avg Wait Time", f"{avg_wait:.1f} hrs")
                with queue_col3:
                    priority_ships = sum(1 for ship in sample_queue if ship['priority'] == 'high')
                    st.metric("Priority Ships", priority_ships)
                with queue_col4:
                    total_cargo = sum(ship['cargo_volume'] for ship in sample_queue)
                    st.metric("Total Cargo", f"{total_cargo:,.0f} TEU")
                
                # Sample queue visualization
                queue_df = pd.DataFrame(sample_queue)
                import plotly.express as px
                fig_queue = px.bar(
                    queue_df,
                    x='ship_id',
                    y='waiting_time',
                    color='ship_type',
                    title='Ship Queue - Waiting Times (Sample Data)',
                    labels={'waiting_time': 'Waiting Time (hours)', 'ship_id': 'Ship ID'}
                )
                st.plotly_chart(fig_queue, use_container_width=True)
                
                # Sample queue table
                st.subheader("📋 Queue Details")
                st.dataframe(queue_df, use_container_width=True)
        
        with ops_tab2:
            st.subheader("🏗️ Berth Utilization Analysis")
            st.info("Berth utilization analysis will be displayed here when simulation is running.")
            
            # Sample berth data
            berth_data = {
                'Berth ID': ['B001', 'B002', 'B003', 'B004', 'B005'],
                'Status': ['Occupied', 'Available', 'Occupied', 'Maintenance', 'Occupied'],
                'Current Ship': ['SHIP-001', '-', 'SHIP-003', '-', 'SHIP-005'],
                'Utilization %': [85, 0, 92, 0, 78]
            }
            berth_df = pd.DataFrame(berth_data)
            st.dataframe(berth_df, use_container_width=True)
        
        with ops_tab3:
            st.subheader("📊 Live Operations")
            st.info("Live operations dashboard will be displayed here when simulation is running.")
            
            # Sample operations metrics
            ops_col1, ops_col2, ops_col3 = st.columns(3)
            with ops_col1:
                st.metric("Active Operations", "12")
            with ops_col2:
                st.metric("Throughput Today", "2,450 TEU")
            with ops_col3:
                st.metric("Efficiency Rate", "87.5%")
    
    with tab7:
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
                scenario1 = st.selectbox("Scenario 1", available_scenarios, key="scenario1_select")
                scenario2 = st.selectbox("Scenario 2", available_scenarios, key="scenario2_select", index=1 if len(available_scenarios) > 1 else 0)
            
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
    
    # Settings tab - now tab8 (was tab9)
    with tab8:
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
        with tab9:
            st.subheader("📊 Performance Analytics")
            st.markdown("Detailed performance metrics and analytics")
            st.info("Performance analytics content would be displayed here.")
        
        with tab10:
            st.subheader("📦 Cargo Analysis")
            st.markdown("Advanced cargo flow and logistics analysis")
            st.info("Cargo analysis content would be displayed here.")



if __name__ == "__main__":
    main()