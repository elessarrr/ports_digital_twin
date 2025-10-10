# Learnings from Debugging the "Avg Wait Time" Issue

This document summarizes the debugging process and key findings from resolving the issue where the "Avg Wait Time" in the Streamlit dashboard was static.

## Problem Description

The "Avg Wait Time" displayed on the dashboard remained constant regardless of the selected scenario (Peak, Normal, Low). This indicated that the wait time calculation was not being updated correctly when the scenario changed.

## Debugging Process

1.  **Initial Hypothesis:** The initial thought was that a `try...except` block was catching an error and returning a default value. To test this, the `try...except` blocks in `wait_time_calculator.py` within the `calculate_wait_time` and `_calculate_threshold_wait_time` functions were temporarily removed to expose any underlying errors.

2.  **Exposing the Error:** After removing the error handling and restarting the application, a `KeyError` was expected in the logs. However, the application logs did not show the error, even after interacting with the application preview. This suggested the error was being handled somewhere else or the interaction was not triggering the error as expected.

3.  **Code Inspection:** Since the error was not appearing in the logs, the code was inspected more closely. The investigation focused on how the `WaitTimeCalculator` was being initialized and how the `threshold_bands` were being defined and accessed.

4.  **Identifying the Root Cause:** The root cause was discovered to be a mismatch between the scenario names used in the `streamlit_app.py` and the keys expected by the `WaitTimeCalculator`.
    *   `hk_port_digital_twin/src/utils/wait_time_calculator.py`: The `WaitTimeCalculator` expected scenario names like "Peak Season", "Normal Operations", and "Low Season".
    *   `hk_port_digital_twin/src/utils/scenario_helpers.py`: The `get_wait_time_scenario_name` function was returning different values like "peak_season", "normal_operations", and "low_season".

5.  **The Silent `KeyError`:** The `KeyError` was being silently caught by a `try...except` block in `streamlit_app.py`, which then caused the `calculate_wait_time` function to use a default value, resulting in the static "Avg Wait Time".

6.  **The Fix:** The issue was resolved by modifying the `get_wait_time_scenario_name` function in `hk_port_digital_twin/src/utils/scenario_helpers.py` to return the correct scenario names that the `WaitTimeCalculator` expects.

7.  **Restoring Error Handling:** After confirming the fix, the `try...except` blocks in `wait_time_calculator.py` were restored to ensure robust error handling.

## Issue: Incorrect "Avg Wait Time" in Streamlit App (Part 2)

**Date:** 2025-10-06

### Problem Description

Even after simplifying the `wait_time_calculator.py` and removing multipliers, the "Avg Wait Time" for "PEAK" and "NORMAL" scenarios remained incorrect, displaying values around 8.3 and 8.5 hours respectively. This was inconsistent with the expected values (12-24 hours for PEAK).

### Debugging Process

1.  **Re-examination of `streamlit_app.py`**: I suspected the issue was still within `streamlit_app.py`. I reviewed the file in sections due to its size.
2.  **Discovery of Fallback Logic**: I identified a fallback mechanism in the `main()` function that was being triggered when real forecast data was unavailable. This fallback logic was calculating the wait time by calling `calculate_wait_time` only once, not averaging it over multiple samples. This was the source of the inconsistent and incorrect values.
3.  **Initial Fix Attempt**: I modified the fallback logic to calculate the average wait time from 100 samples, mirroring the primary calculation logic. This ensured a stable average would be displayed.
4.  **Further Investigation**: The issue persisted. A regex search for `avg_waiting_time` revealed a hardcoded fallback value: `avg_waiting_time = 2.5`. This was overriding the corrected calculation.
5.  **Final Fix**: I removed the hardcoded value. This initially caused a syntax error, which I resolved by setting a more reasonable default of `8.0` in the `else` block.

### Root Cause

There were two issues:

1.  The fallback logic for the KPI summary chart was not calculating a proper average, but using a single, random sample.
2.  A hardcoded fallback value was overriding the corrected calculation.

### Solution

1.  The fallback logic in `streamlit_app.py` was updated to calculate the average wait time from 100 samples.
2.  The hardcoded `avg_waiting_time = 2.5` was removed and replaced with a more appropriate default in the `else` block to resolve the syntax error.


## Key Takeaways

*   **Silent Errors:** Be cautious of `try...except` blocks that might be hiding underlying issues. While important for production, they can make debugging difficult.
*   **Configuration Mismatches:** Inconsistencies in configuration, such as enum values or dictionary keys across different parts of an application, can lead to subtle bugs that are hard to trace.
*   **Code Review:** A thorough code review of the data flow and how different components interact can often reveal issues that are not immediately apparent from logs or testing.