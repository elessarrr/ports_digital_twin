import os
import sys
from unittest.mock import patch

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Mock streamlit and data_loader
patch('streamlit.cache_data', lambda func: func).start()
patch('hk_port_digital_twin.utils.data_loader', lambda: None).start()