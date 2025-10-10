# Wait Time Enhancement Plan: Scenario-Based Threshold Implementation

## Executive Summary

This plan addresses the logical inconsistency where peak season wait times can be zero hours, which contradicts real-world port operations. The enhancement will implement scenario-based wait time thresholds ensuring that:
- **Low Season**: Can have zero wait times (0-2 hours range)
- **Normal Season**: Always higher than low season (1.5-4 hours range)  
- **Peak Season**: Always higher than normal season (3-8 hours range)

The solution will enhance the existing multiplier system with threshold bands while maintaining backward compatibility.

## 1. Understanding the Goal

### Current Problem
- Peak season wait times can be 0.0 hours, which is unrealistic during high-demand periods
- No guaranteed ordering: peak > normal > low wait times
- Current logic uses simple multipliers without minimum thresholds

### Business Logic Requirements
- **Zero wait times**: Only possible during low season
- **Hierarchical wait times**: Peak > Normal > Low (always)
- **Random assignment within bands**: Maintain variability while respecting thresholds
- **Preserve multiplier system**: Enhance, don't replace existing logic

### Success Criteria
- Peak season wait times are never below normal season minimums
- Normal season wait times are never below low season minimums
- Low season can still achieve zero wait times
- Existing dashboard functionality remains intact

## 2. Conservative Approach

### Existing Functionality Preservation
- Keep current `waiting_time_multiplier` system intact
- Maintain existing exponential distribution logic
- Preserve all current dashboard displays and calculations
- Ensure backward compatibility with existing scenario parameters

### Rollback Strategy
- Implement changes as separate utility functions
- Use feature flags to enable/disable new logic
- Keep original logic as fallback option
- Isolate changes to minimize impact on working components

### Risk Mitigation
- Test with existing scenarios before deployment
- Validate that all current metrics still calculate correctly
- Ensure no breaking changes to dashboard UI
- Maintain existing data structures and interfaces

## 3. Implementation Strategy

### Modular Design
- Create new `wait_time_calculator.py` utility module
- Implement scenario-aware wait time generation functions
- Import only where needed (dashboard components)
- Keep business logic separate from UI components

### Integration Points
- **Primary**: `scenario_tab_consolidation.py` (lines 577-578)
- **Secondary**: `streamlit_app.py` (lines 346, 353)
- **Validation**: Existing metrics collection and display logic

### Backward Compatibility
- New functions will accept same parameters as current logic
- Default behavior matches current implementation when thresholds disabled
- Gradual migration path for different dashboard sections

## 4. Pre-Creation Checks

### Existing Code Analysis
✅ **Current Implementation Locations Identified:**
- `scenario_tab_consolidation.py`: Uses `np.random.exponential(base_wait)` 
- `streamlit_app.py`: Uses `np.random.exponential(2, 20) * params['waiting_time_multiplier']`
- Multiple backup files with similar patterns

✅ **Existing Infrastructure:**
- Scenario parameters system in `scenario_parameters.py`
- Multiplier system already in place
- Exponential distribution logic established

✅ **Reusable Components:**
- Scenario detection logic (get_scenario_values functions)
- Parameter validation systems
- Metrics collection infrastructure

### Dependencies Check
- **NumPy**: Already used for random generation ✅
- **Scenario Parameters**: Already defined in `scenario_parameters.py` ✅
- **Dashboard Integration**: Existing hooks available ✅

## 5. Code Minimalism Principle

### Minimal Code Approach
- Single utility function for enhanced wait time calculation
- Reuse existing scenario parameter detection
- Leverage current exponential distribution logic
- Add only threshold validation layer

### Avoid Feature Creep
- Focus solely on wait time threshold enforcement
- Don't modify other operational parameters
- Maintain existing UI/UX patterns
- No additional dashboard components needed

### Efficient Implementation
- ~50 lines of new code maximum
- Reuse existing validation patterns
- Minimal performance impact
- No new dependencies required

## 6. Detailed Step-by-Step Implementation Plan

### Step 1: Create Wait Time Calculator Utility
**File**: `src/utils/wait_time_calculator.py`

**Purpose**: Create a centralized utility for scenario-aware wait time calculation that enforces hierarchical thresholds while maintaining the existing multiplier system.

**Context**: This utility will replace the current simple exponential distribution calls with threshold-aware logic. It needs to integrate seamlessly with existing scenario detection and parameter systems.

**Implementation Details**:
- Create `calculate_scenario_aware_wait_time()` function
- Accept parameters: scenario_name, base_wait_time, multiplier, ship_count
- Define threshold bands for each scenario type
- Implement random assignment within appropriate bands
- Ensure peak > normal > low ordering is always maintained

**Validation**: Function should return values that respect scenario hierarchy and never violate threshold constraints.

### Step 2: Define Scenario-Specific Threshold Bands
**Location**: Within the new utility function

**Purpose**: Establish clear wait time ranges for each scenario that ensure proper hierarchical ordering while allowing for realistic variability.

**Context**: These bands replace the current unlimited exponential distribution with bounded ranges that reflect real-world port operations during different seasons.

**Threshold Definitions**:
- **Low Season**: 0.0 - 2.5 hours (allows zero wait times)
- **Normal Season**: 1.5 - 4.5 hours (minimum 1.5h ensures > low season minimum)
- **Peak Season**: 3.0 - 8.0 hours (minimum 3.0h ensures > normal season minimum)

**Implementation**: Use scenario name detection to select appropriate band, then apply random generation within that band.

### Step 3: Integrate Threshold Logic with Existing Multipliers
**Purpose**: Enhance the current multiplier system rather than replacing it, ensuring backward compatibility while adding threshold enforcement.

**Context**: The existing `waiting_time_multiplier` values (peak: 1.5, normal: 1.0, low: 0.7) should still influence wait times but within the constraint of scenario thresholds.

**Logic Flow**:
1. Calculate base wait time using existing exponential distribution
2. Apply existing multiplier
3. Check if result falls within scenario-appropriate threshold band
4. If outside band, adjust to nearest valid value within band
5. Add small random variation to maintain realistic distribution

**Validation**: Multiplier effects should still be visible while respecting absolute threshold constraints.

### Step 4: Update Scenario Tab Consolidation
**File**: `src/dashboard/scenario_tab_consolidation.py`
**Lines**: 577-578 (current exponential calculation)

**Purpose**: Replace the current simple exponential wait time calculation with the new scenario-aware function.

**Context**: This is the primary location where wait times are calculated for the scenario analysis dashboard. The change should be transparent to the UI while providing more realistic wait time distributions.

**Changes Required**:
- Import the new wait time calculator utility
- Replace `np.random.exponential(base_wait)` call
- Pass scenario context and existing parameters
- Maintain same variable names and data structures

**Testing**: Verify that dashboard displays update correctly and show appropriate wait time ranges for each scenario.

### Step 5: Update Main Streamlit App
**File**: `src/dashboard/streamlit_app.py`
**Lines**: 346, 353 (waiting_time calculations)

**Purpose**: Apply the same enhanced wait time logic to the main dashboard to ensure consistency across all views.

**Context**: The main app currently uses a simpler calculation that may not respect scenario thresholds. This update ensures all dashboard sections show consistent, realistic wait times.

**Changes Required**:
- Import the new utility function
- Update both ship queue and waiting data calculations
- Preserve existing data structure formats
- Maintain compatibility with existing metrics displays

**Validation**: All dashboard metrics should continue to calculate correctly while showing more realistic wait time distributions.

### Step 6: Add Validation and Error Handling
**Purpose**: Ensure the new logic handles edge cases gracefully and provides clear error messages for debugging.

**Context**: Port operations can have unexpected scenarios, and the wait time calculator should handle these robustly without breaking dashboard functionality.

**Error Handling Requirements**:
- Validate scenario name inputs (handle unknown scenarios)
- Check for negative wait times and correct them
- Handle zero ship counts gracefully
- Provide fallback to original logic if new logic fails

**Logging**: Add debug logging to track threshold adjustments and validation corrections.

### Step 7: Create Unit Tests
**File**: `tests/test_wait_time_calculator.py`

**Purpose**: Ensure the new wait time logic works correctly across all scenarios and edge cases.

**Context**: Automated testing will validate that the threshold enforcement works correctly and that the hierarchical ordering (peak > normal > low) is always maintained.

**Test Cases Required**:
- Verify threshold ranges for each scenario
- Test hierarchical ordering enforcement
- Validate multiplier integration
- Test edge cases (zero ships, unknown scenarios)
- Performance testing with large ship counts

**Success Criteria**: All tests pass and demonstrate that wait time constraints are properly enforced.

### Step 8: Integration Testing
**Purpose**: Verify that the enhanced wait time logic integrates correctly with existing dashboard functionality.

**Context**: The changes should be transparent to users while providing more realistic and logically consistent wait time displays.

**Testing Scenarios**:
- Load each scenario type and verify wait time ranges
- Check that metrics calculations remain accurate
- Validate that charts and displays show expected patterns
- Test scenario switching to ensure proper threshold application

**Validation**: Dashboard should show realistic wait time patterns with peak > normal > low ordering consistently maintained.

### Step 9: Documentation Updates
**Files**: Code comments, function docstrings

**Purpose**: Document the new logic for future developers and explain the business reasoning behind threshold implementation.

**Context**: Clear documentation ensures that future modifications maintain the logical consistency and business requirements.

**Documentation Requirements**:
- Function docstrings explaining threshold logic
- Code comments explaining business reasoning
- Examples of expected wait time ranges
- Migration notes for future developers

**Format**: Follow existing code documentation patterns and include practical examples.

### Step 10: Performance Validation
**Purpose**: Ensure the enhanced logic doesn't negatively impact dashboard performance.

**Context**: The new calculations should add minimal overhead while providing more accurate wait time modeling.

**Performance Checks**:
- Measure calculation time for large ship queues
- Verify memory usage remains acceptable
- Test dashboard responsiveness with new logic
- Compare performance against original implementation

**Acceptance Criteria**: Performance impact should be negligible (< 5% increase in calculation time).

## 7. Project and User Rule Compliance

### User-Specified Rules Adherence
✅ **Conservative approach**: Enhancing existing system, not replacing
✅ **Rollback capability**: New logic isolated in separate utility
✅ **Minimal code**: Single utility function with focused responsibility
✅ **Existing infrastructure reuse**: Leveraging current scenario and parameter systems

### Project Standards Compliance
✅ **Code organization**: New utility in appropriate `/utils/` directory
✅ **Testing requirements**: Unit tests and integration tests planned
✅ **Documentation standards**: Comprehensive docstrings and comments
✅ **Performance considerations**: Minimal overhead design

### Business Logic Compliance
✅ **Realistic operations**: Wait times reflect actual port congestion patterns
✅ **Scenario consistency**: Hierarchical ordering always maintained
✅ **Operational flexibility**: Random variation within realistic bounds
✅ **System integration**: Seamless integration with existing dashboard

## 8. Risk Assessment and Mitigation

### Technical Risks
- **Risk**: Breaking existing dashboard functionality
- **Mitigation**: Isolated implementation with fallback logic

- **Risk**: Performance degradation
- **Mitigation**: Efficient algorithm design and performance testing

- **Risk**: Inconsistent wait time displays
- **Mitigation**: Centralized utility ensures consistency across all views

### Business Risks
- **Risk**: Wait times too high/low for realistic operations
- **Mitigation**: Threshold bands based on real-world port operation patterns

- **Risk**: Loss of existing multiplier system benefits
- **Mitigation**: Integration approach preserves multiplier effects within threshold constraints

### Operational Risks
- **Risk**: Difficult rollback if issues arise
- **Mitigation**: Feature flag approach allows instant reversion to original logic

## 9. Success Metrics

### Functional Validation
- [ ] Peak season wait times never below 3.0 hours
- [ ] Normal season wait times never below 1.5 hours  
- [ ] Low season can achieve 0.0 hour wait times
- [ ] Hierarchical ordering maintained: Peak > Normal > Low
- [ ] Existing dashboard metrics calculate correctly

### Performance Validation
- [ ] Dashboard load time increase < 5%
- [ ] Wait time calculation overhead < 10ms for 100 ships
- [ ] Memory usage increase < 2%

### User Experience Validation
- [ ] Dashboard displays remain visually consistent
- [ ] Scenario switching works smoothly
- [ ] No error messages or broken functionality
- [ ] Wait time patterns appear realistic and logical

## 10. Implementation Timeline

### Phase 1: Core Development (Day 1)
- Create wait time calculator utility
- Define threshold bands and validation logic
- Implement basic unit tests

### Phase 2: Integration (Day 1)
- Update scenario tab consolidation
- Update main streamlit app
- Integration testing

### Phase 3: Validation (Day 1)
- Performance testing
- User acceptance testing
- Documentation completion

### Total Estimated Time: 1 Day
The modular approach and reuse of existing infrastructure allows for rapid implementation while maintaining quality and reliability.

---

**Next Steps**: Upon user confirmation of this plan, proceed with Step 1 implementation of the wait time calculator utility.