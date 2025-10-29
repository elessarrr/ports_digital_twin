# Reference Implementation Analysis - Scenarios Tab Restoration
**Date:** October 29, 2024
**Purpose:** Analyze differences between reference and current implementations

## Key Differences Identified

### 1. Tab Structure and Positioning
**Reference Implementation:**
- Scenarios tab is `tab7` (7th tab)
- Uses `with tab7:` block
- Settings tab is `tab8` (8th tab)
- Additional tabs for original structure: `tab9` (Performance Analytics), `tab10` (Cargo Analysis)

**Current Implementation:**
- Scenarios tab is `tab4` (4th tab)
- Uses `with tab4:` block
- Different tab ordering and structure

### 2. Scenarios Tab Content Differences
**Reference Implementation (lines 1456-1520):**
```python
with tab7:
    if use_consolidated:
        # Initialize and render the consolidated scenarios tab
        consolidated_tab = ConsolidatedScenariosTab()
        # Get current scenario from session state
        current_scenario = st.session_state.get('scenario', 'normal')
        scenario_data = {'name': current_scenario}
        consolidated_tab.render_consolidated_tab(scenario_data)
    else:
        # Original Scenario Analysis tab content
        st.subheader("🎯 Scenario Analysis & Comparison")
        st.markdown("Compare different operational scenarios and their impact on port performance")
        
        # Scenario selection for comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Select Scenarios to Compare**")
            available_scenarios = list_available_scenarios()
            scenario1 = st.selectbox("Scenario 1", available_scenarios, key="scenario1_select")
            scenario2 = st.selectbox("Scenario 2", available_scenarios, key="scenario2_select", index=1 if len(available_scenarios) > 1 else 0)
        
        with col2:
            st.write("**Comparison Parameters**")
            compare_metrics = st.multiselect(
                "Metrics to Compare",
                ["Ship Arrival Rate", "Processing Efficiency", "Berth Utilization", "Waiting Times"],
                default=["Ship Arrival Rate", "Processing Efficiency"]
            )
        
        # ... rest of comparison logic
```

**Current Implementation (lines 2052-2120):**
```python
with tab4:
    if use_consolidated:
        # Similar consolidated tab logic
    else:
        # Enhanced scenario selection with display names and emojis
        scenario_display_options = [get_scenario_display_name(scenario) for scenario in available_scenarios]
        scenario1_display = st.selectbox("Scenario 1", scenario_display_options, key="scenario1_select")
        # ... enhanced display logic with get_scenario_key_from_display()
```

### 3. Dependencies and Imports
**Both implementations use similar imports:**
- `from hk_port_digital_twin.src.scenarios import ScenarioManager, list_available_scenarios`
- `from hk_port_digital_twin.src.dashboard.scenario_tab_consolidation import ConsolidatedScenariosTab`
- Standard libraries: `pandas`, `plotly.express`, `streamlit`

**Current implementation has additional helper functions:**
- `get_scenario_display_name(scenario_key: str) -> str`
- `get_scenario_key_from_display(display_name: str) -> str`

### 4. Key Functional Differences
**Reference Implementation:**
- Simple scenario selection using raw scenario keys
- Basic comparison logic with hardcoded sample data
- Straightforward UI without enhanced display names

**Current Implementation:**
- Enhanced scenario selection with emoji display names
- Helper functions for display name conversion
- More sophisticated UI presentation

## Required Changes for Restoration

### 1. Code Replacement Strategy
**Target:** Replace current `tab4` scenarios content with reference `tab7` content

**Approach:**
1. Extract the entire `with tab7:` block from reference (lines 1456-1520)
2. Replace the current `with tab4:` block (lines 2052-2120)
3. Update tab reference from `tab7` to `tab4` to maintain current tab structure

### 2. Dependencies to Maintain
**Keep these imports (already present in current):**
- `list_available_scenarios` from scenarios module
- `ConsolidatedScenariosTab` from scenario_tab_consolidation
- `plotly.express` for visualization
- `pandas` for data handling

### 3. Helper Functions to Remove/Modify
**Current helper functions that may become unused:**
- `get_scenario_display_name()` - may not be needed in reference implementation
- `get_scenario_key_from_display()` - may not be needed in reference implementation

**Action:** Keep these functions as they may be used elsewhere, but scenarios tab will use simpler approach

### 4. Integration Points
**Tab Structure:**
- Maintain current tab numbering (tab4 for scenarios)
- Ensure `use_consolidated` flag continues to work
- Preserve settings tab functionality

**Session State:**
- Maintain `st.session_state.scenario_comparison_data` handling
- Preserve `st.session_state.get('scenario', 'normal')` logic
- Keep consolidated tab session state management

## Implementation Plan

### Step 1: Extract Reference Code
- Copy lines 1456-1520 from reference `streamlit_app.py`
- Modify `tab7` references to `tab4`
- Preserve the exact logic and structure

### Step 2: Replace Current Implementation
- Replace current `with tab4:` block entirely
- Maintain proper indentation and structure
- Ensure no syntax errors

### Step 3: Test Integration
- Verify tab switching works correctly
- Test both consolidated and original modes
- Ensure other tabs remain unaffected

## Risk Assessment

### Low Risk
- Code structure is very similar between versions
- Dependencies are already present
- Tab logic is straightforward

### Medium Risk
- Tab numbering change (tab7 → tab4) needs careful handling
- Session state compatibility needs verification

### Mitigation
- Comprehensive backups already created
- Incremental testing approach
- Rollback plan documented

---
**Status:** Analysis complete, ready for implementation