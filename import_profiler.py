#!/usr/bin/env python3
"""
Import profiler to identify heavy imports causing startup delays.
This script measures the time taken to import each module from streamlit_app.py.
"""

import time
import sys
import os

# Add the project path
sys.path.insert(0, '/Users/Bhavesh/Documents/GitHub/ports_digital_twin')

def time_import(module_name, import_statement):
    """Time how long it takes to import a module."""
    start_time = time.time()
    try:
        exec(import_statement)
        end_time = time.time()
        return end_time - start_time, None
    except Exception as e:
        end_time = time.time()
        return end_time - start_time, str(e)

def main():
    """Profile imports from streamlit_app.py."""
    print("Import Performance Analysis")
    print("=" * 50)
    
    # List of imports from streamlit_app.py (based on our analysis)
    imports_to_test = [
        ("sys", "import sys"),
        ("os", "import os"),
        ("time", "import time"),
        ("streamlit", "import streamlit as st"),
        ("pandas", "import pandas as pd"),
        ("datetime", "from datetime import datetime, timedelta"),
        ("logging", "import logging"),
        ("numpy", "import numpy as np"),
        ("simpy", "import simpy"),
        ("data_loader", "from hk_port_digital_twin.src.utils import data_loader"),
        ("config", "from hk_port_digital_twin.src.config import config"),
        ("core_simulation", "from hk_port_digital_twin.src.core import core_simulation"),
        ("scenario_manager", "from hk_port_digital_twin.src.scenarios import scenario_manager"),
        ("visualization", "from hk_port_digital_twin.src.visualization import visualization"),
        ("dashboard_components", "from hk_port_digital_twin.src.dashboard import dashboard_components"),
        ("guided_tour", "from hk_port_digital_twin.src.dashboard import guided_tour"),
        ("scenario_aware_calculator", "from hk_port_digital_twin.src.utils import scenario_aware_calculator"),
        ("analysis_components", "from hk_port_digital_twin.src.analysis import analysis_components"),
    ]
    
    results = []
    
    for module_name, import_stmt in imports_to_test:
        print(f"Testing import: {module_name}...")
        import_time, error = time_import(module_name, import_stmt)
        results.append((module_name, import_time, error))
        
        if error:
            print(f"  ❌ {module_name}: {import_time:.4f}s (ERROR: {error})")
        else:
            print(f"  ✅ {module_name}: {import_time:.4f}s")
    
    print("\n" + "=" * 50)
    print("SUMMARY - Sorted by Import Time")
    print("=" * 50)
    
    # Sort by import time (descending)
    results.sort(key=lambda x: x[1], reverse=True)
    
    for module_name, import_time, error in results:
        status = "ERROR" if error else "OK"
        print(f"{module_name:25} | {import_time:8.4f}s | {status}")
    
    print("\n" + "=" * 50)
    print("HEAVY IMPORTS (>0.1s)")
    print("=" * 50)
    
    heavy_imports = [(name, t, err) for name, t, err in results if t > 0.1 and not err]
    if heavy_imports:
        for module_name, import_time, _ in heavy_imports:
            print(f"🔥 {module_name}: {import_time:.4f}s")
    else:
        print("No imports taking longer than 0.1s detected.")

if __name__ == "__main__":
    main()