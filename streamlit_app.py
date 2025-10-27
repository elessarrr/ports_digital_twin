#!/usr/bin/env python3
"""
Streamlit Community Cloud Entry Point for Hong Kong Port Digital Twin Dashboard
"""

import sys
from pathlib import Path
import runpy
import os

# This is the crucial part. We add the project root to the python path.
# This ensures that when runpy executes the dashboard, the dashboard code can find its modules.
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

try:
    # Run the dashboard as a module to ensure correct package context for imports
    runpy.run_module("hk_port_digital_twin.dashboard.executive_dashboard", run_name="__main__")

except ImportError as e:
    import streamlit as st
    st.error(f"Error importing dashboard module: {e}")
    st.info(f"Current working directory: {os.getcwd()}")
    st.info(f"Python path: {sys.path[:3]}...")
except Exception as e:
    import streamlit as st
    st.error(f"Error running dashboard: {e}")
    st.info(f"Current working directory: {os.getcwd()}")
    st.info(f"Python path: {sys.path[:3]}...")


import streamlit as st


def load_data():
    pass


# Add a selectbox for navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox(
    "Choose the app mode",
    [
        "Home",
        "Vessel Monitoring",
        "Scenario Analysis",
        "Vessel Trajectory Analysis",
    ],
)

# Load data
data = load_data()
