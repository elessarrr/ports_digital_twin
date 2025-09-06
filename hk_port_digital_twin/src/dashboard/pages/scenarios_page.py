import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from components.layout import LayoutManager
from styles.theme_manager import ThemeManager

# Import scenario management components
try:
    from src.scenarios.scenario_manager import ScenarioManager, create_scenario_manager
    from src.scenarios.scenario_parameters import (
        ScenarioParameters,
        ALL_SCENARIOS,
        SCENARIO_ALIASES,
        get_scenario_parameters,
        list_available_scenarios,
        validate_scenario_parameters
    )
except ImportError:
    # Fallback if scenario modules are not available
    ScenarioManager = None
    create_scenario_manager = None
    ALL_SCENARIOS = ['normal', 'peak', 'low']
    list_available_scenarios = lambda: ALL_SCENARIOS
    get_scenario_parameters = lambda x: {}

class ScenariosPage:
    """Scenarios page for simulation management and scenario analysis"""
    
    def __init__(self, layout_manager: LayoutManager):
        self.layout = layout_manager
        self._initialize_scenario_manager()
    
    def _initialize_scenario_manager(self):
        """Initialize scenario manager in session state"""
        if 'scenario_manager' not in st.session_state:
            if create_scenario_manager:
                st.session_state.scenario_manager = create_scenario_manager()
            else:
                st.session_state.scenario_manager = None
    
    def render(self, data: Dict[str, Any]) -> None:
        """Render the scenarios page"""
        # Apply theme and layout
        self.layout.apply_custom_css()
        
        # Page header
        self.layout.create_section_header(
            "Scenarios Management",
            "Simulation controls and scenario analysis",
            "🎯"
        )
        
        # Render main sections
        self._render_scenario_controls(data)
        self.layout.add_spacing('lg')
        
        self._render_active_scenarios(data)
        self.layout.add_spacing('lg')
        
        self._render_scenario_comparison(data)
    
    def _render_scenario_controls(self, data: Dict[str, Any]) -> None:
        """Render scenario control interface"""
        with self.layout.create_card("🎯 Scenario Controls"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Scenario selection dropdown
                scenarios = [
                    "Current State",
                    "Peak Season", 
                    "Weather Disruption",
                    "Equipment Maintenance",
                    "Custom Scenario"
                ]
                
                selected_scenario = st.selectbox(
                    "Select Scenario",
                    scenarios,
                    help="Choose a predefined scenario or create a custom one"
                )
                
                # Scenario description
                scenario_descriptions = {
                    "Current State": "Real-time port operations with current parameters",
                    "Peak Season": "High traffic scenario with increased vessel arrivals",
                    "Weather Disruption": "Operations during adverse weather conditions",
                    "Equipment Maintenance": "Reduced capacity due to equipment maintenance",
                    "Custom Scenario": "User-defined parameters and conditions"
                }
                
                st.info(scenario_descriptions.get(selected_scenario, "No description available"))
            
            with col2:
                # Simulation controls
                st.markdown("**Simulation Parameters**")
                
                duration = st.slider("Simulation Duration (hours)", 1, 168, 24)
                speed = st.selectbox("Simulation Speed", ["1x", "2x", "5x", "10x"])
                
                if st.button("🚀 Start Simulation", type="primary"):
                    st.success(f"Starting {selected_scenario} simulation for {duration} hours at {speed} speed")
    
    def _render_active_scenarios(self, data: Dict[str, Any]) -> None:
        """Render active scenarios section"""
        with self.layout.create_card("📊 Active Scenarios"):
            # Mock active scenarios data
            active_scenarios = [
                {
                    'name': 'Peak Season Analysis',
                    'status': 'Running',
                    'progress': 75,
                    'eta': '2 hours',
                    'type': 'Strategic'
                },
                {
                    'name': 'Weather Impact Study',
                    'status': 'Queued',
                    'progress': 0,
                    'eta': 'Pending',
                    'type': 'Operational'
                },
                {
                    'name': 'Berth Optimization',
                    'status': 'Completed',
                    'progress': 100,
                    'eta': 'Completed',
                    'type': 'Tactical'
                }
            ]
            
            for scenario in active_scenarios:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{scenario['name']}**")
                        st.caption(f"Type: {scenario['type']}")
                    
                    with col2:
                        status_color = {
                            'Running': '🟡',
                            'Queued': '🔵', 
                            'Completed': '🟢'
                        }
                        st.write(f"{status_color.get(scenario['status'], '⚪')} {scenario['status']}")
                    
                    with col3:
                        if scenario['progress'] > 0:
                            st.progress(scenario['progress'] / 100)
                            st.caption(f"{scenario['progress']}%")
                    
                    with col4:
                        st.write(scenario['eta'])
                    
                    st.divider()
    

    
    def _render_scenario_comparison(self, data: Dict[str, Any]) -> None:
        """Render scenario comparison section"""
        with self.layout.create_card("📊 Scenario Comparison"):
            # Mock comparison data
            comparison_data = {
                'Scenario': ['Current State', 'Peak Season', 'Weather Disruption', 'Equipment Maintenance'],
                'Avg Waiting Time (h)': [2.5, 4.2, 6.8, 3.1],
                'Berth Utilization (%)': [78, 92, 60, 65],
                'Daily Throughput (TEU)': [1200, 1800, 800, 950],
                'Vessels per Day': [15, 25, 8, 12],
                'Efficiency Score': [85, 78, 45, 68]
            }
            
            df = pd.DataFrame(comparison_data)
            
            # Display comparison table
            st.dataframe(df, use_container_width=True)
            
            # Comparison charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Waiting time comparison
                fig_waiting = px.bar(
                    df, 
                    x='Scenario', 
                    y='Avg Waiting Time (h)',
                    color='Avg Waiting Time (h)',
                    color_continuous_scale='RdYlBu_r'
                )
                fig_waiting.update_layout(height=400)
                st.plotly_chart(fig_waiting, use_container_width=True)
            
            with col2:
                # Efficiency score comparison
                fig_efficiency = px.bar(
                    df, 
                    x='Scenario', 
                    y='Efficiency Score',
                    color='Efficiency Score',
                    color_continuous_scale='RdYlGn'
                )
                fig_efficiency.update_layout(height=400)
                st.plotly_chart(fig_efficiency, use_container_width=True)
    


def create_scenarios_page(layout_manager: LayoutManager) -> ScenariosPage:
    """Factory function to create a scenarios page instance"""
    return ScenariosPage(layout_manager)