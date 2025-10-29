# Import Analysis: streamlit_app.py

**File:** `/Users/Bhavesh/Documents/GitHub/ports_digital_twin/hk_port_digital_twin/src/dashboard/streamlit_app.py`  
**Analysis Date:** 2025-01-28  
**Lines Analyzed:** 1-60 (and additional imports found up to line 87)  

## Current Import Structure

### Standard Library Imports (Lines 1-9)
```python
import sys
import os
import time
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import logging
import numpy as np
import simpy
```

**Analysis:**
- **Heavy imports:** `pandas`, `numpy`, `streamlit` - These are loaded immediately on startup
- **Impact:** High - These are essential but contribute to initial load time
- **Optimization potential:** Low - These are core dependencies

### Path Management (Lines 11-29)
```python
from pathlib import Path

def find_project_root(marker_file='streamlit_app.py'):
    # Function implementation for finding project root
```

**Analysis:**
- **Purpose:** Dynamic project root discovery
- **Impact:** Low - Minimal performance impact
- **Optimization potential:** Low - Necessary for path resolution

### Core Data Loading Imports (Lines 31-32)
```python
from hk_port_digital_twin.src.utils.data_loader import RealTimeDataConfig, get_real_time_manager, load_container_throughput, load_vessel_arrivals, load_berth_configurations, initialize_vessel_data_pipeline, load_all_vessel_data, get_comprehensive_vessel_analysis, load_combined_vessel_data, load_all_vessel_data_with_backups
```

**Analysis:**
- **Heavy imports:** `data_loader` module (3493 lines) with multiple functions
- **Impact:** Very High - This is likely the biggest performance bottleneck
- **Optimization potential:** Very High - Prime candidate for lazy loading
- **Functions imported:** 9 different data loading functions

### Configuration Imports (Line 33)
```python
from hk_port_digital_twin.config.settings import SIMULATION_CONFIG, get_enhanced_simulation_config
```

**Analysis:**
- **Impact:** Low-Medium - Configuration loading
- **Optimization potential:** Medium - Could be loaded conditionally

### Core Simulation Imports (Lines 34-37)
```python
from hk_port_digital_twin.src.core.port_simulation import PortSimulation
from hk_port_digital_twin.src.core.simulation_controller import SimulationController
from hk_port_digital_twin.src.core.berth_manager import BerthManager
from hk_port_digital_twin.src.scenarios import ScenarioManager, list_available_scenarios
```

**Analysis:**
- **Impact:** High - Core simulation components
- **Optimization potential:** High - Could be loaded only when simulation tabs are accessed
- **Usage:** Primarily used in scenarios tab

### Visualization Imports (Lines 38-39)
```python
from hk_port_digital_twin.src.utils.visualization import create_kpi_summary_chart, create_port_layout_chart, create_ship_queue_chart, create_berth_utilization_chart, create_throughput_timeline, create_waiting_time_distribution
```

**Analysis:**
- **Impact:** Medium-High - Multiple chart creation functions
- **Optimization potential:** High - Could be loaded conditionally per chart type
- **Functions imported:** 6 different visualization functions

### Weather Integration (Lines 40-42) - DISABLED
```python
# Weather integration disabled for feature removal
# from hk_port_digital_twin.src.utils.weather_integration import HKObservatoryIntegration
HKObservatoryIntegration = None  # Disabled
```

**Analysis:**
- **Impact:** None - Already disabled
- **Optimization potential:** None - Can be removed entirely

### Additional Data Loading (Line 43)
```python
from hk_port_digital_twin.src.utils.data_loader import load_focused_cargo_statistics, get_enhanced_cargo_analysis, get_time_series_data
```

**Analysis:**
- **Impact:** Medium - Additional data loading functions from same heavy module
- **Optimization potential:** High - Same as core data loading imports
- **Note:** Duplicate import from same module as line 31

### Dashboard Component Imports (Lines 44-47)
```python
from hk_port_digital_twin.src.dashboard.scenario_tab_consolidation import ConsolidatedScenariosTab
from hk_port_digital_twin.src.dashboard.vessel_charts import render_vessel_analytics_dashboard
from hk_port_digital_twin.src.dashboard.executive_dashboard import ExecutiveDashboard
from hk_port_digital_twin.src.analysis.roi_calculator import render_roi_calculator
```

**Analysis:**
- **Impact:** High - Heavy dashboard components
- **Optimization potential:** Very High - Perfect candidates for lazy loading
- **Usage:** Each used only when specific tabs are accessed

### Guided Tour Import (Line 48)
```python
from hk_port_digital_twin.src.dashboard import guided_tour
```

**Analysis:**
- **Impact:** Medium - Guided tour functionality
- **Optimization potential:** Very High - Only needed when tour is activated
- **Usage:** Conditional based on user interaction

### Strategic Components (Lines 49-51)
```python
from hk_port_digital_twin.src.utils.strategic_visualization import StrategicVisualization, render_strategic_controls
from hk_port_digital_twin.src.core.strategic_simulation_controller import StrategicSimulationController
from hk_port_digital_twin.src.utils.scenario_aware_calculator import ScenarioAwareCalculator, ValueType, ScenarioType
```

**Analysis:**
- **Impact:** High - Strategic analysis components
- **Optimization potential:** Very High - Used only in specific scenarios
- **Usage:** Primarily in ROI calculator and strategic simulations

### Duplicate Import (Line 52)
```python
from hk_port_digital_twin.src.analysis.roi_calculator import render_roi_calculator
```

**Analysis:**
- **Impact:** None - Duplicate of line 47
- **Optimization potential:** High - Should be removed
- **Issue:** Redundant import

### Scenario Helpers (Line 53)
```python
from hk_port_digital_twin.src.utils.scenario_helpers import get_wait_time_scenario_name
```

**Analysis:**
- **Impact:** Low-Medium - Helper functions
- **Optimization potential:** Medium - Could be loaded conditionally

### Conditional Import with Error Handling (Lines 55-64)
```python
try:
    from hk_port_digital_twin.src.utils.wait_time_calculator import WaitTimeCalculator, calculate_wait_time
except (ImportError, NameError, AttributeError) as e:
    WaitTimeCalculator = None
    calculate_wait_time = None
    st.sidebar.warning(f"Wait time calculator not available. Features disabled. Error: {e}")
```

**Analysis:**
- **Impact:** Medium - Wait time calculation functionality
- **Optimization potential:** Medium - Already has error handling, could be made lazy
- **Note:** Good example of graceful degradation

### Additional Conditional Import (Lines 84-87)
```python
try:
    from hk_port_digital_twin.src.dashboard.marine_traffic_integration import MarineTrafficIntegration
except ImportError:
    MarineTrafficIntegration = None
```

**Analysis:**
- **Impact:** Low-Medium - Marine traffic integration
- **Optimization potential:** Medium - Already conditional, could be made lazy
- **Note:** Good example of optional feature loading

## Summary of Performance Impact

### High Impact Imports (Prime Optimization Targets)
1. **data_loader module** (Lines 31, 43) - Very heavy module with 3493 lines
2. **Dashboard components** (Lines 44-47) - Heavy UI components
3. **Strategic components** (Lines 49-51) - Complex analysis modules
4. **Simulation core** (Lines 34-37) - Heavy simulation engine
5. **Visualization functions** (Lines 38-39) - Multiple chart functions

### Medium Impact Imports
1. **guided_tour** (Line 48) - UI enhancement
2. **scenario_helpers** (Line 53) - Helper functions
3. **wait_time_calculator** (Lines 55-64) - Calculation module

### Low Impact Imports
1. **Standard libraries** (Lines 1-9) - Essential dependencies
2. **Configuration** (Line 33) - Lightweight config
3. **Marine traffic** (Lines 84-87) - Optional feature

### Issues Identified
1. **Duplicate import:** `render_roi_calculator` imported twice (lines 47, 52)
2. **Heavy module multiple imports:** `data_loader` imported twice with different functions
3. **Disabled feature:** Weather integration code should be removed entirely

## Optimization Recommendations

### Immediate Actions
1. Remove duplicate `render_roi_calculator` import
2. Consolidate `data_loader` imports into single import
3. Remove disabled weather integration code

### Lazy Loading Candidates (High Priority)
1. Dashboard components (scenario_tab_consolidation, vessel_charts, executive_dashboard)
2. Strategic components (strategic_visualization, strategic_simulation_controller, scenario_aware_calculator)
3. Guided tour module
4. ROI calculator
5. Simulation core components

### Conditional Loading Candidates (Medium Priority)
1. Visualization functions (load only needed chart types)
2. Data loading functions (load only when data is needed)
3. Scenario helpers (load only when scenarios are used)

This analysis provides the foundation for implementing the import optimization strategy outlined in the task list.