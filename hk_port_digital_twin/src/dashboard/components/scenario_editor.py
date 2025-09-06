import streamlit as st
import pandas as pd
from typing import Dict, Any

def render_scenario_editor():
    """
    Renders a scenario editor component that allows users to define and customize
    simulation scenarios by adjusting various operational parameters.
    """
    with st.expander("🔧 Customize Scenario Parameters", expanded=False):
        st.markdown("#### Define Your Custom Scenario")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Scenario Name", "Custom Scenario 1")
            vessel_arrival_rate = st.slider(
                "Vessel Arrival Rate (per hour)", 0.1, 5.0, 1.0, 0.1,
                help="Average number of vessels arriving at the port each hour."
            )
            container_throughput_multiplier = st.slider(
                "Container Throughput Multiplier", 0.5, 2.0, 1.0, 0.1,
                help="Adjust the container handling capacity of the port."
            )

        with col2:
            berth_availability = st.slider(
                "Berth Availability (%)", 50, 100, 100, 5,
                help="Percentage of berths that are operational."
            )
            crane_efficiency = st.slider(
                "Crane Efficiency (%)", 50, 100, 90, 5,
                help="Efficiency of quay cranes in loading/unloading containers."
            )

        st.markdown("---")
        
        st.markdown("##### Advanced Settings")
        
        enable_weather_effects = st.checkbox(
            "Enable Weather Effects", value=False,
            help="Simulate the impact of weather on port operations."
        )
        
        if enable_weather_effects:
            wind_speed_factor = st.slider(
                "Wind Speed Factor", 1.0, 3.0, 1.5, 0.1,
                help="Multiplier for wind speed to simulate storms."
            )
            wave_height_factor = st.slider(
                "Wave Height Factor", 1.0, 4.0, 2.0, 0.1,
                help="Multiplier for wave height to simulate rough seas."
            )

        if st.button("💾 Save Scenario"):
            st.success("Scenario saved successfully!")