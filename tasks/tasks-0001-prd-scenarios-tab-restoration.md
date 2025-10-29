# Task List: Scenarios Tab Restoration

Based on PRD: `0001-prd-scenarios-tab-restoration.md`

## Relevant Files

- `hk_port_digital_twin/src/dashboard/streamlit_app.py` - Main dashboard file containing the scenarios tab implementation that needs to be restored (lines ~2050-2118).
- `hk_port_digital_twin/src/dashboard/scenario_tab_consolidation.py` - Current consolidated scenarios tab module that may become obsolete after restoration.
- `/Users/Bhavesh/Downloads/[reference for scenarios tab] ports_digital_twin-main/hk_port_digital_twin/src/dashboard/streamlit_app.py` - Reference implementation containing the older working scenarios tab code.
- `/Users/Bhavesh/Downloads/[reference for scenarios tab] ports_digital_twin-main/hk_port_digital_twin/src/dashboard/scenario_tab_consolidation.py` - Reference consolidated scenarios module for comparison.
- `backups/scenarios_tab_backup_*` - Backup directories for preserving current implementation before changes.

### Notes

- The main restoration work involves replacing the scenarios tab logic in `streamlit_app.py` within the `with tab4:` block.
- The current implementation uses `ConsolidatedScenariosTab()` which should be replaced with the reference implementation.
- Backup files should be created before making any changes to ensure rollback capability.
- Testing should focus on verifying that only the scenarios tab is affected while other tabs remain functional.

## Tasks

- [x] 1.0 Prepare Environment and Create Backups
  - [x] 1.1 Create timestamped backup of current `streamlit_app.py`
  - [x] 1.2 Create timestamped backup of current `scenario_tab_consolidation.py`
  - [x] 1.3 Verify backup integrity and file accessibility
  - [x] 1.4 Document current implementation state for rollback reference

- [x] 2.0 Extract and Analyze Reference Implementation
  - [x] 2.1 Extract scenarios tab code from reference `streamlit_app.py` (lines ~1400-1647)
  - [x] 2.2 Identify all dependencies and imports used by reference implementation
  - [x] 2.3 Analyze differences between reference and current implementation
  - [x] 2.4 Document required code changes and integration points

- [ ] 3.0 Replace Scenarios Tab Implementation
  - [x] 3.1 Replace current scenarios tab code in `streamlit_app.py` with reference implementation
  - [x] 3.2 Update import statements to match reference implementation requirements
  - [x] 3.3 Ensure proper integration with existing dashboard structure
  - [x] 3.4 Verify that other tabs remain unaffected by the changes

- [ ] 4.0 Clean Up Dependencies and Imports
  - [ ] 4.1 Remove unused imports related to `ConsolidatedScenariosTab`
  - [ ] 4.2 Clean up any orphaned code or comments
  - [ ] 4.3 Update any configuration flags or settings if needed
  - [ ] 4.4 Verify all required dependencies are properly imported

- [x] 5.0 Test and Validate Restoration
  - [x] 5.1 Run the Streamlit application to verify it starts without errors
  - [x] 5.2 Test scenarios tab functionality matches reference behavior
  - [x] 5.3 Verify other tabs (Overview, Performance Analytics, etc.) remain functional
  - [x] 5.4 Perform end-to-end testing of scenario selection and analysis features
    - Verified available scenarios: `peak`, `normal`, `low` from scenario_parameters.py
    - Confirmed scenario selection functionality is working with direct scenario keys
    - Application preview opened successfully without errors
    - Streamlit application running properly on localhost:8501
  - [x] 5.5 Document any issues found and resolution steps

---

**Implementation Status:** Ready to begin implementation. Starting with Task 1.0.