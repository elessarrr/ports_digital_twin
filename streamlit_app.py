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
    dashboard_path = project_root / "hk_port_digital_twin" / "src" / "dashboard" / "streamlit_app.py"
    
    if not dashboard_path.exists():
        raise FileNotFoundError(f"Dashboard file not found at: {dashboard_path}")

    # This is a more robust way to run a script, as it handles sys.path and other things correctly.
    # It should also play nicer with Streamlit's file watcher.
    runpy.run_path(str(dashboard_path), run_name="__main__")

except FileNotFoundError as e:
    import streamlit as st
    st.error(f"Dashboard file not found: {e}")
    st.info(f"Current working directory: {os.getcwd()}")
    st.info(f"Looking for dashboard at: {Path(__file__).resolve().parent / 'hk_port_digital_twin' / 'src' / 'dashboard' / 'streamlit_app.py'}")
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
