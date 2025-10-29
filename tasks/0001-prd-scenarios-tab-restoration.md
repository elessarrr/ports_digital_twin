# Product Requirements Document: Scenarios Tab Restoration

## Introduction/Overview

This PRD outlines the requirements for restoring the "Scenarios" tab in the Hong Kong Port Digital Twin Dashboard to an older, working version. The current implementation uses a complex consolidated scenarios tab (`ConsolidatedScenariosTab`) that has become problematic, while the reference workspace contains a simpler, more functional implementation that provides better user experience and reliability.

The goal is to replace the current scenarios tab implementation with the proven working version from the reference workspace, ensuring that only the scenarios tab content is affected while preserving all other dashboard functionality.

## Goals

1. **Restore Functional Scenarios Tab**: Replace the current consolidated scenarios tab with the older, working implementation that provides reliable scenario analysis and comparison functionality.

2. **Maintain Dashboard Integrity**: Ensure that the restoration only affects the scenarios tab (tab4) and does not impact other dashboard tabs or core functionality.

3. **Preserve User Experience**: Maintain the existing tab structure and navigation while improving the scenarios tab content and functionality.

4. **Ensure Compatibility**: Verify that the restored scenarios tab works seamlessly with the existing codebase, including imports, dependencies, and session state management.

5. **Maintain Performance**: Ensure the restored implementation performs well and does not introduce performance regressions.

## User Stories

### Primary User Stories

**US1**: As a port operations manager, I want to access a reliable scenarios tab so that I can analyze different operational scenarios without encountering errors or complex interfaces.

**US2**: As a data analyst, I want to compare different scenarios using simple, intuitive controls so that I can quickly assess the impact of various operational changes.

**US3**: As a dashboard user, I want the scenarios tab to load quickly and display relevant information so that I can make informed decisions about port operations.

**US4**: As a system administrator, I want the scenarios tab to work consistently with the rest of the dashboard so that users have a seamless experience across all tabs.

### Secondary User Stories

**US5**: As a junior developer, I want the scenarios tab code to be simple and maintainable so that I can understand and modify it when needed.

**US6**: As a quality assurance tester, I want the scenarios tab to function reliably so that I can validate its behavior during testing cycles.

## Functional Requirements

### Core Functionality Requirements

**FR1**: The system must replace the current `ConsolidatedScenariosTab` implementation with the reference implementation from the older workspace.

**FR2**: The system must maintain the existing tab structure where the scenarios tab is tab4 in the dashboard.

**FR3**: The system must preserve the conditional logic that switches between consolidated and original tab structures based on user preferences.

**FR4**: The system must implement scenario analysis and comparison functionality as defined in the reference implementation.

**FR5**: The system must support scenario selection with display names and emojis as shown in the reference code.

**FR6**: The system must provide comparison parameters selection (Ship Arrival Rate, Processing Efficiency, Berth Utilization, Waiting Times).

**FR7**: The system must display comparison results in both tabular and chart formats using Plotly visualizations.

**FR8**: The system must maintain session state for scenario comparison data.

### Integration Requirements

**FR9**: The system must preserve all existing imports and dependencies in the main `streamlit_app.py` file.

**FR10**: The system must maintain compatibility with the existing scenario management system (`ScenarioManager`).

**FR11**: The system must work with existing helper functions (`get_scenario_display_name`, `get_scenario_key_from_display`, `list_available_scenarios`).

**FR12**: The system must integrate properly with the existing data loading and visualization systems.

### User Interface Requirements

**FR13**: The system must display "🎯 Scenario Analysis & Comparison" as the main header for the scenarios tab.

**FR14**: The system must provide two-column layout for scenario selection and comparison parameters.

**FR15**: The system must include a "🔄 Run Scenario Comparison" button with primary styling.

**FR16**: The system must show loading spinner during scenario comparison operations.

**FR17**: The system must display success messages when scenario comparison is completed.

**FR18**: The system must render comparison results with appropriate charts based on selected metrics.

## Non-Goals (Out of Scope)

**NG1**: This restoration will NOT modify any other dashboard tabs (Overview, Cargo Statistics, Vessel Insights, Settings).

**NG2**: This restoration will NOT create new custom implementations or features beyond what exists in the reference workspace.

**NG3**: This restoration will NOT modify the core simulation or scenario management systems.

**NG4**: This restoration will NOT change the overall dashboard structure or navigation.

**NG5**: This restoration will NOT involve creating new dependencies or external integrations.

**NG6**: This restoration will NOT modify the settings tab preferences for tab structure switching.

**NG7**: This restoration will NOT involve database schema changes or data migration.

## Design Considerations

### Reference Implementation Structure

The reference implementation is located in:
- **Primary file**: `/Users/Bhavesh/Downloads/[reference for scenarios tab] ports_digital_twin-main/hk_port_digital_twin/src/dashboard/streamlit_app.py` (lines 2061-2118)
- **Supporting file**: `/Users/Bhavesh/Downloads/[reference for scenarios tab] ports_digital_twin-main/hk_port_digital_twin/src/dashboard/scenario_tab_consolidation.py`

### UI/UX Considerations

- Maintain the existing two-column layout for scenario selection and parameters
- Preserve the existing button styling and interaction patterns
- Keep the current chart rendering approach using Plotly
- Maintain the existing color scheme and visual hierarchy

### Code Organization

- The scenarios tab logic should be embedded directly in the `streamlit_app.py` file within the `with tab4:` block
- Remove dependency on the current `ConsolidatedScenariosTab` class
- Preserve the conditional logic for `use_consolidated` preference

## Technical Considerations

### Dependencies

- The implementation relies on existing imports: `pandas`, `plotly.express`, `streamlit`
- Must maintain compatibility with existing scenario helper functions
- Should work with the current session state management approach

### File Modifications

**Primary Target**: `/Users/Bhavesh/Documents/GitHub/ports_digital_twin/hk_port_digital_twin/src/dashboard/streamlit_app.py`
- Replace the content within the `with tab4:` block (approximately lines 2050-2118)
- Remove or comment out the import for `ConsolidatedScenariosTab` if no longer needed

**Secondary Consideration**: The current `scenario_tab_consolidation.py` file may become obsolete after the restoration.

### Compatibility Requirements

- Must work with Python 3.13 environment
- Must be compatible with current Streamlit version
- Must integrate with existing data loading and caching mechanisms
- Must respect existing session state variables and patterns

## Success Metrics

### Functional Success Metrics

**SM1**: The scenarios tab loads without errors and displays the expected interface.

**SM2**: Scenario selection dropdowns populate correctly with available scenarios and display names.

**SM3**: Comparison parameter selection works as expected with multi-select functionality.

**SM4**: The "Run Scenario Comparison" button triggers the comparison logic successfully.

**SM5**: Comparison results display correctly in both table and chart formats.

**SM6**: The tab switching between consolidated and original modes works without affecting the scenarios tab functionality.

### Performance Success Metrics

**SM7**: The scenarios tab loads within 2 seconds of tab selection.

**SM8**: Scenario comparison operations complete within 5 seconds.

**SM9**: Chart rendering completes without noticeable delays.

### Quality Success Metrics

**SM10**: No console errors or warnings are generated when using the scenarios tab.

**SM11**: The scenarios tab works consistently across multiple browser sessions.

**SM12**: All other dashboard tabs continue to function normally after the restoration.

## Open Questions

**OQ1**: Should the current `scenario_tab_consolidation.py` file be deleted, moved to a backup location, or kept for reference?

**OQ2**: Are there any specific scenario data or comparison logic customizations in the current implementation that should be preserved?

**OQ3**: Should we create a backup of the current implementation before performing the restoration?

**OQ4**: Are there any additional testing requirements beyond functional verification?

**OQ5**: Should we update any documentation or comments to reflect the restoration?

## Implementation Notes

### Restoration Approach

1. **Backup Current Implementation**: Create a backup of the current scenarios tab implementation before making changes.

2. **Code Replacement**: Replace the scenarios tab logic in `streamlit_app.py` with the reference implementation.

3. **Import Cleanup**: Remove or update imports related to the `ConsolidatedScenariosTab` if no longer needed.

4. **Testing**: Verify that the restored tab works correctly and doesn't affect other functionality.

5. **Validation**: Ensure all success metrics are met before considering the restoration complete.

### Risk Mitigation

- Create comprehensive backups before making any changes
- Test the restoration in a development environment first
- Verify that all existing functionality remains intact
- Have a rollback plan in case issues arise during implementation

---

**Document Version**: 1.0  
**Created**: January 2025  
**Target Audience**: Junior Developer  
**Estimated Implementation Time**: 2-4 hours