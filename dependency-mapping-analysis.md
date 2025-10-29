# Import Dependencies and Usage Patterns Analysis
## streamlit_app.py - Comprehensive Mapping

*Generated: 2024-12-19*

## Executive Summary

This analysis maps all import dependencies and their usage patterns in `streamlit_app.py` to identify optimization opportunities for lazy loading, conditional imports, and module splitting.

## Import Categories and Usage Analysis

### 1. Critical Heavy Imports (High Priority for Optimization)

#### 1.1 data_loader Module (1.2685s import time)
**Import Lines:**
- Line 34: `from hk_port_digital_twin.src.utils.data_loader import RealTimeDataConfig, get_real_time_manager, load_container_throughput, load_vessel_arrivals, load_berth_configurations, initialize_vessel_data_pipeline, load_all_vessel_data, get_comprehensive_vessel_analysis, load_combined_vessel_data, load_all_vessel_data_with_backups`
- Line 44: `from hk_port_digital_twin.src.utils.data_loader import load_focused_cargo_statistics, get_enhanced_cargo_analysis, get_time_series_data`

**Usage Patterns:**
- `load_container_throughput()` - Used at line 326 in main dashboard
- `load_berth_configurations()` - Used at line 519 in simulation setup
- Other functions: **NOT USED** in current streamlit_app.py

**Optimization Opportunity:** 🔴 **CRITICAL**
- Only 2 out of 12 imported functions are actually used
- 83% of imports are unused and causing unnecessary startup delay
- Immediate lazy loading candidate

#### 1.2 pandas (0.7879s import time)
**Import Line:** Line 5: `import pandas as pd`

**Usage Patterns:**
- Used throughout the application for data manipulation
- Essential for data processing operations
- Cannot be lazy loaded due to widespread usage

**Optimization Opportunity:** 🟡 **MEDIUM**
- Consider importing only when data operations are needed
- Potential for conditional loading in specific tabs

### 2. Dashboard Components (Medium Priority)

#### 2.1 ConsolidatedScenariosTab
**Import Line:** Line 45: `from hk_port_digital_twin.src.dashboard.scenario_tab_consolidation import ConsolidatedScenariosTab`

**Usage Patterns:**
- Used at line 2054: `consolidated_tab = ConsolidatedScenariosTab()`
- Only used in "Scenarios" tab
- Perfect candidate for lazy loading

**Optimization Opportunity:** 🟢 **HIGH**
- Load only when "Scenarios" tab is accessed
- Significant startup improvement potential

#### 2.2 ExecutiveDashboard
**Import Line:** Line 47: `from hk_port_digital_twin.src.dashboard.executive_dashboard import ExecutiveDashboard`

**Usage Patterns:**
- **NOT USED** in current streamlit_app.py
- Imported but never instantiated or called

**Optimization Opportunity:** 🔴 **CRITICAL**
- Remove unused import immediately
- Zero impact on functionality

#### 2.3 render_vessel_analytics_dashboard
**Import Line:** Line 46: `from hk_port_digital_twin.src.dashboard.vessel_charts import render_vessel_analytics_dashboard`

**Usage Patterns:**
- **NOT USED** in current streamlit_app.py
- Previously used in backup versions but removed

**Optimization Opportunity:** 🔴 **CRITICAL**
- Remove unused import immediately
- Zero impact on functionality

### 3. Visualization Functions

#### 3.1 Visualization Utils
**Import Line:** Line 40: `from hk_port_digital_twin.src.utils.visualization import create_kpi_summary_chart, create_port_layout_chart, create_ship_queue_chart, create_berth_utilization_chart, create_throughput_timeline, create_waiting_time_distribution`

**Usage Patterns:**
- `create_kpi_summary_chart()` - Used at lines 787, 813
- Other functions: **NOT USED** in current version

**Optimization Opportunity:** 🟡 **MEDIUM**
- Import only `create_kpi_summary_chart`
- Remove unused visualization functions

### 4. Strategic Components

#### 4.1 StrategicVisualization & StrategicSimulationController
**Import Lines:**
- Line 50: `from hk_port_digital_twin.src.utils.strategic_visualization import StrategicVisualization, render_strategic_controls`
- Line 51: `from hk_port_digital_twin.src.core.strategic_simulation_controller import StrategicSimulationController`

**Usage Patterns:**
- Used in strategic analysis sections
- Tab-specific functionality
- Good candidates for lazy loading

**Optimization Opportunity:** 🟢 **HIGH**
- Load only when strategic tabs are accessed

### 5. Core Simulation Components

#### 5.1 Simulation Core
**Import Lines:**
- Line 36: `from hk_port_digital_twin.src.core.port_simulation import PortSimulation`
- Line 37: `from hk_port_digital_twin.src.core.simulation_controller import SimulationController`
- Line 38: `from hk_port_digital_twin.src.core.berth_manager import BerthManager`

**Usage Patterns:**
- Used in simulation tabs
- Heavy computational modules
- Tab-specific usage

**Optimization Opportunity:** 🟢 **HIGH**
- Lazy load when simulation tabs are accessed

### 6. Unused/Disabled Imports

#### 6.1 Completely Unused
- `ExecutiveDashboard` - Line 47
- `render_vessel_analytics_dashboard` - Line 46
- Multiple `data_loader` functions (10 out of 12)
- Multiple `visualization` functions (5 out of 6)

#### 6.2 Disabled/Commented
- `HKObservatoryIntegration` - Line 43 (explicitly disabled)
- `UnifiedSimulationsTab` - Commented out

## Dependency Tree Analysis

### High-Level Dependencies
```
streamlit_app.py
├── Standard Libraries (fast)
│   ├── sys, os, time
│   ├── datetime, logging
│   └── pathlib
├── Heavy External Libraries
│   ├── streamlit (0.4456s)
│   ├── pandas (0.7879s)
│   └── numpy, simpy
├── Project Core (heavy)
│   ├── data_loader (1.2685s) ⚠️
│   ├── config.settings
│   └── core.* modules
├── Dashboard Components (tab-specific)
│   ├── ConsolidatedScenariosTab 🎯
│   ├── ExecutiveDashboard ❌ (unused)
│   └── vessel_charts ❌ (unused)
└── Analysis Components (conditional)
    ├── roi_calculator
    ├── strategic_visualization 🎯
    └── scenario_helpers
```

## Optimization Recommendations

### Immediate Actions (0-effort, high impact)
1. **Remove unused imports** (Lines 46, 47)
   - `ExecutiveDashboard`
   - `render_vessel_analytics_dashboard`
   - Expected improvement: ~200-300ms

2. **Consolidate data_loader imports**
   - Import only used functions: `load_container_throughput`, `load_berth_configurations`
   - Expected improvement: ~800ms

3. **Clean visualization imports**
   - Import only `create_kpi_summary_chart`
   - Expected improvement: ~100-200ms

### High-Priority Lazy Loading (medium effort, high impact)
1. **ConsolidatedScenariosTab** - Load on "Scenarios" tab access
2. **Strategic components** - Load on strategic tab access
3. **Core simulation modules** - Load on simulation tab access

### Expected Performance Improvements
- **Immediate cleanup**: 40-50% faster startup (1.1-1.3s reduction)
- **With lazy loading**: 60-70% faster startup (1.5-1.8s reduction)
- **Total potential**: From ~2.5s to ~0.7-1.0s startup time

## Implementation Priority Matrix

| Component | Impact | Effort | Priority | Expected Savings |
|-----------|--------|--------|----------|------------------|
| Remove unused imports | High | Low | 🔴 Critical | 1.0-1.3s |
| Lazy load ConsolidatedScenariosTab | High | Medium | 🟢 High | 0.3-0.5s |
| Lazy load strategic components | Medium | Medium | 🟡 Medium | 0.2-0.3s |
| Conditional pandas loading | Low | High | 🔵 Low | 0.1-0.2s |

## Next Steps
1. Implement immediate cleanup (remove unused imports)
2. Implement lazy loading for tab-specific components
3. Create conditional import patterns for heavy modules
4. Monitor and measure performance improvements