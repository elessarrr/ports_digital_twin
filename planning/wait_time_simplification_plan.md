# Wait Time Calculation Simplification Plan

This plan details the steps to simplify the `wait_time_calculator.py` module. The goal is to ensure a clear, noticeable, and logical difference between wait times for "Peak," "Normal," and "Low" scenarios (Peak > Normal > Low) by reducing complexity.

### 1. Understand the Goal
The current implementation, while statistically sophisticated, produces wait times that are too close together (e.g., Peak at 8 hours, Normal at 9 hours), which is counterintuitive. The goal is to simplify the logic to make the distinctions between scenarios obvious and robust.

### 2. Adopt a Conservative Approach
- We will modify the existing `WaitTimeCalculator` class without changing its public interface (`calculate_wait_time` method).
- This ensures that the rest of the application, which depends on this calculator, continues to function without any changes.
- The simplification will be contained entirely within `wait_time_calculator.py`.

### 3. Implementation Strategy
The core idea is to replace the complex normal distribution calculation with a simple uniform distribution. This guarantees that the generated wait times fall squarely within the defined bands for each scenario.

### 4. Detailed Step-by-Step Plan

#### Step 1: Simplify Threshold Band Definitions
- **What:** In `_define_threshold_bands`, we will remove the keys that are no longer needed: `mean_hours`, `std_hours`, and `distribution`. We will only keep `min_hours` and `max_hours`.
- **Why:** This simplifies the configuration and makes it clear that we are only defining a range, not a complex statistical distribution.

#### Step 2: Widen the Threshold Bands for Clearer Distinction
- **What:** We will adjust the `min_hours` and `max_hours` to create a much wider and more distinct gap between the scenarios. The proposed new bands are:
  - **Peak:** 12 to 24 hours
  - **Normal:** 6 to 11 hours
  - **Low:** 1 to 5 hours
- **Why:** This will make the difference in average wait times between the scenarios much more pronounced and immediately obvious to the user.

#### Step 3: Simplify the Calculation Logic
- **What:** In `_calculate_threshold_wait_time`, we will replace the `np.random.normal` and `np.clip` logic with a single, simple call to `np.random.uniform`.
- **Why:** This is the core of the simplification. It's easier to understand, more performant, and directly achieves the goal of generating a random wait time within the specified `min` and `max` hours.

#### Step 4: Remove Unnecessary Helper Functions
- **What:** We will remove the `get_scenario_statistics` and `validate_logical_ordering` methods from the `WaitTimeCalculator` class.
- **Why:** These functions were built to support the more complex statistical approach. With our simplified logic, they are no longer necessary and removing them contributes to a cleaner, more minimal codebase.

#### Step 5: Update Documentation
- **What:** We will update the docstrings and comments at the top of `wait_time_calculator.py` to reflect the new, simplified approach.
- **Why:** This ensures that any future developer can quickly understand the module's purpose and logic.

### 5. User Confirmation
After you approve this plan, I will proceed with the implementation, following these steps.