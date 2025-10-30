## Relevant Files

- `hk_port_digital_twin/src/dashboard/streamlit_app.py` - Contains the main application layout and calls to render the ROI calculator.
- `hk_port_digital_twin/src/dashboard/executive_dashboard.py` - May contain ROI-related calculations and UI elements.
- `hk_port_digital_twin/src/dashboard/scenario_tab_consolidation.py` - Contains ROI-related calculations.
- `hk_port_digital_twin/tests/test_investment_planner.py` - Contains tests related to the ROI calculator that will need to be removed or updated.

### Notes

- The primary goal is to completely remove the ROI calculator and all its associated logic from the codebase.
- Ensure that the application remains stable and that no broken references are left after the removal.

## Tasks

- [ ] 1.0 Remove the ROI Calculator UI from `streamlit_app.py`
  - [ ] 1.1 Locate and remove the `render_roi_calculator()` call.
  - [ ] 1.2 Remove the `About the ROI Calculator` expander.
- [ ] 2.0 Remove the `render_roi_calculator` function and any related helper functions.
  - [ ] 2.1 Find the definition of `render_roi_calculator()` and delete it.
- [ ] 3.0 Remove ROI-related logic from other parts of the application.
  - [ ] 3.1 Inspect `executive_dashboard.py` for any remaining ROI calculations and remove them.
- [ ] 4.0 Update or remove tests.
  - [ ] 4.1 Review `test_investment_planner.py` and remove any tests related to the ROI calculator.
- [ ] 5.0 Final verification.
  - [x] 5.1 Run the application and ensure the ROI calculator is gone and there are no errors.
  - [ ] 5.2 Run the test suite to ensure all tests pass.