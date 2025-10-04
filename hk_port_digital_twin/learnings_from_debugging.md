# Learnings from Debugging and Development

## Error 8: Streamlit Cloud Path Duplication in `exec()` Context

### Symptom
- **Error**: `FileNotFoundError` with a duplicated path component when running in Streamlit Cloud.
- **Example**: `/mount/src/ports/Ports_23Aug_v2.2_demo_working_streamlit_optimised/hk_port_digital_twin/Ports_23Aug_v2.2_demo_working_streamlit_optimised/streamlit_app.py`
- **Context**: This error occurred when the application was deployed to Streamlit Cloud, but not locally.

### Root Cause
- **`exec()` and `__file__`**: The use of `exec()` to run the dashboard script from a different entry point (`streamlit_app.py`) caused confusion in how the `__file__` attribute was resolved within the executed code.
- **Hardcoded Path Resolution**: The dashboard script used `Path(__file__).resolve().parents[3]` to find the project root. This assumed a fixed directory structure that was not consistent between the local environment and the Streamlit Cloud environment.
- **Streamlit File Watcher**: The dynamic execution with `exec()` and string manipulation of the code before execution was likely interfering with Streamlit's file watcher, leading to incorrect path resolution.

### Resolution
The solution involved a combination of simplifying the entry point and making the project root discovery more robust.

1.  **Simplified Entry Point**: The root `streamlit_app.py` was simplified to use `runpy.run_path()` to execute the dashboard script. This is a more robust way to run a Python script as it correctly handles `sys.path` and other module-level attributes.

    ```python
    # streamlit_app.py (root)
    import runpy
    from pathlib import Path

    dashboard_path = Path(__file__).resolve().parent / "hk_port_digital_twin" / "src" / "dashboard" / "streamlit_app.py"
    runpy.run_path(str(dashboard_path), run_name="__main__")
    ```

2.  **Robust Project Root Discovery**: The hardcoded `parents[3]` was replaced with a dynamic `find_project_root()` function in the dashboard's `streamlit_app.py`. This function searches up the directory tree for a known marker (in this case, the presence of both `streamlit_app.py` and the `hk_port_digital_twin` directory), making the logic independent of the environment's specific file structure.

    ```python
    # hk_port_digital_twin/src/dashboard/streamlit_app.py
    from pathlib import Path
    import sys

    def find_project_root(marker_file='streamlit_app.py'):
        current_path = Path(__file__).resolve()
        for parent in current_path.parents:
            if (parent / marker_file).exists() and (parent / 'hk_port_digital_twin').exists():
                return str(parent)
        # Fallback
        for parent in current_path.parents:
            if (parent / 'hk_port_digital_twin').exists():
                return str(parent)
        raise FileNotFoundError("Project root not found.")

    project_root = find_project_root()
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    ```

### Key Learnings
- **Avoid `exec()` for File-Based Scripts**: `exec()` can have subtle side effects on path resolution, especially in cloud environments. `runpy.run_path()` is a much safer and more predictable alternative for running scripts.
- **Dynamic Path Resolution**: Never rely on hardcoded directory structures (`parents[n]`). Always use a dynamic method to find project roots, such as searching for marker files or directories. This makes the code more portable and less prone to environment-specific errors.
- **Streamlit Cloud Environment**: Be aware that the file system structure in Streamlit Cloud can differ from a local development environment. Code that relies on specific path structures is likely to break upon deployment.

## Scenario-Dependent Performance Analytics Implementation

### Issue Resolved
- **Problem**: Performance Analytics section displayed static values regardless of selected scenario (Peak, Normal, Low)
- **Root Cause**: Hardcoded values in data generation methods instead of using scenario-specific parameters
- **Solution**: Implemented dynamic value ranges based on selected scenario

### Changes Made

#### 1. Enhanced Scenario Parameters (`_get_scenario_performance_params`)
Added comprehensive cargo-specific parameters for each scenario:

**Peak Season:**
- Cargo Volume Range: 200,000 - 400,000 TEU
- Revenue Range: $50M - $120M
- Handling Time Range: 8 - 20 hours
- Trade Balance Range: -$80K to +$80K

**Normal Operations:**
- Cargo Volume Range: 120,000 - 280,000 TEU
- Revenue Range: $30M - $80M
- Handling Time Range: 4 - 15 hours
- Trade Balance Range: -$50K to +$50K

**Low Season:**
- Cargo Volume Range: 80,000 - 180,000 TEU
- Revenue Range: $20M - $60M
- Handling Time Range: 3 - 10 hours
- Trade Balance Range: -$30K to +$30K

#### 2. Updated Data Export Section
- Modified berth data generation to use scenario-specific utilization and throughput ranges
- Updated queue data to use scenario-specific waiting time scales
- Enhanced timeline data to reflect scenario parameters

#### 3. Enhanced Cargo Analysis Section
- **New Volume & Revenue Analysis Tab**: Displays scenario-dependent metrics including total cargo volume, revenue, handling times, and trade balance
- **Updated Cargo Types Analysis**: Uses scenario-specific ranges for volume, revenue, and handling time generation
- **Updated Geographic Analysis**: Applies scenario parameters to import/export volume calculations

#### 4. Performance Metrics Integration
- Performance metrics already used scenario-specific KPI ranges
- Radar charts now reflect scenario-dependent performance targets

### Technical Implementation Details

#### Key Methods Modified:
1. `_render_data_export_section()` - Added scenario parameter retrieval and usage
2. `render_cargo_analysis_section()` - Complete restructure with scenario-aware tabs
3. `_render_cargo_volume_revenue_analysis()` - New method with scenario-dependent metrics
4. `_render_cargo_types_analysis()` - Updated to accept and use scenario parameters
5. `_render_locations_analysis()` - Enhanced with scenario-specific volume ranges

#### Data Generation Strategy:
- All random value generation now uses scenario-specific ranges
- Consistent scaling factors applied (e.g., 0.1x to 0.8x of base ranges for different cargo types)
- Maintains realistic relationships between different metrics

### Verification
- Application successfully restarts without errors
- Preview shows no browser errors
- All sections now display values that change based on selected scenario
- Data ranges are appropriate for each scenario type (Peak > Normal > Low)

### Future Enhancements
- Consider adding seasonal variations within scenarios
- Implement historical trend analysis
- Add scenario comparison features
- Include confidence intervals for forecasted values

## Error 9: Missing 'Arriving' Vessels in Streamlit UI

### Symptom
- **Issue**: 'Arriving' vessels were not appearing in the Streamlit dashboard despite being present in the raw data files
- **Context**: The `Expected_arrivals.xml` file contained vessel data, but these vessels were not showing up with 'arriving' status in the UI
- **Impact**: Users could not see incoming vessels, limiting the dashboard's real-time monitoring capabilities

### Root Cause Analysis
- **Data Loading Path**: The Streamlit app used `load_all_vessel_data_with_backups()` by default (for "Last 7 days" selection), which internally calls `load_vessel_data_from_xml()`
- **Status Assignment Logic**: In `load_vessel_data_from_xml()` function, the status assignment logic had a flaw:
  ```python
  # Problematic logic in data_loader.py (lines 1532-1540)
  if 'departed' in file_name:
      vessel_data['status'] = 'departed'
  elif 'expected' in file_name:  # This caught Expected_arrivals.xml incorrectly
      vessel_data['status'] = 'expected'
  elif vessel_data.get('remark') == 'Departed':
      vessel_data['status'] = 'departed'
  else:
      vessel_data['status'] = 'in_port'
  ```
- **The Problem**: `Expected_arrivals.xml` contains the substring 'expected', so it was being assigned 'expected' status instead of 'arriving'

### Debugging Process
1. **Initial Investigation**: Used `debug_backup_data.py` to analyze what `load_all_vessel_data_with_backups()` was returning
2. **Data Verification**: Confirmed that 0 'arriving' vessels were found in the default data loading path
3. **Comparison Analysis**: Verified that `load_combined_vessel_data()` correctly identified 'arriving' vessels
4. **Code Inspection**: Traced the data flow to identify the exact location of the status assignment issue

### Resolution
**Solution**: Added a specific condition for 'arriving' vessels in the status assignment logic:

```python
# Fixed logic in load_vessel_data_from_xml() function
if 'departed' in file_name:
    vessel_data['status'] = 'departed'
elif 'expected_arrivals' in file_name:  # ✅ NEW: Specific handling for arriving vessels
    vessel_data['status'] = 'arriving'
elif 'expected' in file_name:
    vessel_data['status'] = 'expected'
elif vessel_data.get('remark') == 'Departed':
    vessel_data['status'] = 'departed'
else:
    vessel_data['status'] = 'in_port'
```

**Implementation Details**:
- **File Modified**: `/hk_port_digital_twin/src/utils/data_loader.py`
- **Lines Changed**: 1532-1540 (added 3 lines)
- **Backup Created**: `data_loader.py.backup` for safety
- **Minimal Impact**: Only affects status assignment for `Expected_arrivals.xml`

### Verification Results
**Before Fix**:
- departed: 1010, expected: 633, in_port: 153, **arriving: 0**

**After Fix**:
- departed: 1008, expected: 372, in_port: 160, **arriving: 288** ✅

### Key Learnings
1. **Order Matters in Conditional Logic**: When using substring matching for file names, more specific conditions must come before general ones
2. **Default Data Loading Paths**: Understanding which data loading function the UI uses by default is crucial for debugging display issues
3. **Status Assignment Consistency**: Different data loading functions (`load_combined_vessel_data()` vs `load_all_vessel_data_with_backups()`) should assign statuses consistently
4. **Debug Script Value**: Creating targeted debug scripts helps isolate data loading issues without UI complexity
5. **Conservative Approach**: When multiple solutions exist (replace function vs modify function), choose the one that preserves existing functionality and historical data capabilities

### Technical Notes
- **Preserved Functionality**: The fix maintains all existing historical data pipelining and backup file processing
- **Minimal Code Change**: Only 3 lines added, reducing risk of introducing new bugs
- **Backward Compatibility**: All existing vessel statuses ('departed', 'expected', 'in_port') continue to work as before
- **Performance Impact**: Negligible - only adds one additional string comparison per vessel record

### Prevention Strategy
- **Unit Tests**: Add specific tests for status assignment logic with different XML file names
- **Integration Tests**: Verify that all data loading paths produce consistent vessel status assignments
- **Documentation**: Document the expected status values and their corresponding data sources