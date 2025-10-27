"""
Load tests for the Streamlit dashboard.
"""

import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import patch
import pandas as pd
import time

# --- Constants ---
NUM_USERS = 2
RUN_INTERVAL_SECONDS = 2

@pytest.fixture
def mock_data_loading():
    """Fixture to mock data loading functions."""
    with patch("hk_port_digital_twin.dashboard.streamlit_app.load_data") as mock_load:
        mock_load.return_value = pd.DataFrame({
            'vessel_name': ['Vessel A', 'Vessel B'],
            'arrival_time': ['2023-01-01 10:00', '2023-01-01 11:00'],
            'departure_time': ['2023-01-01 18:00', '2023-01-01 19:00'],
            'berth_number': [1, 2]
        })
        yield

def simulate_user_interaction(at: AppTest):
    """Simulates a single user interacting with the dashboard."""
    try:
        # 1. Initial run and select Scenarios tab
        at.run()
        at.radio(key="main_menu").set_value("Scenarios").run()
        assert at.radio(key="main_menu").value == "Scenarios"

        # 2. Interact with a widget
        at.selectbox(key="Select Scenario").select("Custom Scenario").run()
        assert at.selectbox(key="Select Scenario").value == "Custom Scenario"

        # 3. Simulate some thinking time
        time.sleep(1)

        # 4. Interact with another widget
        at.slider(key="Throughput Multiplier").set_value(1.8).run()
        assert at.slider(key="Throughput Multiplier").value == 1.8

    except Exception as e:
        pytest.fail(f"User simulation failed: {e}")

@pytest.mark.load
def test_dashboard_load_sequentially(mock_data_loading):
    """
    Runs a sequential load test to ensure stability without threading.
    This avoids potential race conditions with GUI libraries.
    """
    
    at = AppTest.from_file("hk_port_digital_twin/dashboard/streamlit_app.py")
    
    for i in range(NUM_USERS):
        print(f"Running simulation {i + 1}/{NUM_USERS}")
        simulate_user_interaction(at)
        time.sleep(RUN_INTERVAL_SECONDS)

    # A successful run without exceptions is considered a pass.
    assert True