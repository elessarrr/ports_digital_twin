## Product Requirements Document: Remove ROI Calculator

### 1. Introduction/Overview
This document outlines the requirements for the complete removal of the "ROI Calculator" feature from the port digital twin application. The feature is being removed because it is considered too simplistic and does not provide significant value to the end-users.

### 2. Goals
- To simplify the user interface by removing unnecessary components.
- To reduce cognitive load on users by eliminating a feature that does not offer deep, actionable insights.
- To streamline the codebase by removing the logic, UI elements, and any related configurations associated with the ROI Calculator.

### 3. User Stories
- As a port operator, I want a clean and focused interface so that I can concentrate on the most critical operational data and scenarios.
- As a system administrator, I want to reduce the application's complexity so that it is easier to maintain and update.

### 4. Functional Requirements
1. The "ROI Calculator" section, including its title, description, input fields ("Cost per hour of vessel waiting time" and "Fuel cost per hour per vessel"), and "Projected Annual Savings" display, must be entirely removed from the user interface.
2. All backend logic associated with calculating the ROI, including any functions or data models, must be removed from the codebase.
3. Any configuration files or settings related to the ROI Calculator must be removed.
4. The application should continue to function correctly without the ROI Calculator, with no broken links or errors.

### 5. Non-Goals (Out of Scope)
- Replacing the ROI Calculator with another feature. The space it occupied will be left empty.
- Archiving the ROI Calculator code for future use. It is to be deleted permanently.

### 6. Design Considerations (Optional)
- The removal of the ROI Calculator should not negatively impact the layout or styling of the remaining components on the page. The surrounding UI elements should adjust gracefully to the change.

### 7. Technical Considerations (Optional)
- The removal should be comprehensive, ensuring no dead code related to the ROI Calculator remains in the application.

### 8. Success Metrics
- The "ROI Calculator" is no longer visible in the application's user interface.
- A code review confirms that all files and code related to the ROI Calculator have been successfully removed.
- The application remains stable and fully functional after the removal, with no new bugs or errors introduced.

### 9. Open Questions
- None at this time.