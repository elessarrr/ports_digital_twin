"""
This module contains the ROI calculator for the Digital Twin.
"""

import streamlit as st

def render_roi_calculator():
    """
    Renders the ROI calculator section in the Streamlit dashboard.
    """
    st.header("ROI Calculator")
    st.write("This section allows you to calculate the potential return on investment (ROI) from using the Digital Twin to optimize port operations.")

    # Input fields for operational costs
    cost_per_hour_waiting = st.number_input("Cost per hour of vessel waiting time ($)", min_value=0, value=1000)
    fuel_cost_per_hour = st.number_input("Fuel cost per hour per vessel ($)", min_value=0, value=500)

    # Placeholder for simulation results
    # In a real application, this would be dynamically loaded from the simulation engine
    baseline_waiting_hours = 1000
    optimized_waiting_hours = 700

    # Calculate cost savings
    waiting_time_reduction = baseline_waiting_hours - optimized_waiting_hours
    cost_savings_waiting_time = waiting_time_reduction * cost_per_hour_waiting
    cost_savings_fuel = (baseline_waiting_hours - optimized_waiting_hours) * fuel_cost_per_hour # Simplified fuel cost calculation

    total_savings = cost_savings_waiting_time + cost_savings_fuel

    # Display results
    st.subheader("Projected Annual Savings")
    col1, col2, col3 = st.columns(3)
    col1.metric("Waiting Time Reduction", f"{waiting_time_reduction} hours")
    col2.metric("Cost Savings (Waiting Time)", f"${cost_savings_waiting_time:,.0f}")
    col3.metric("Cost Savings (Fuel)", f"${cost_savings_fuel:,.0f}")

    st.success(f"**Total Projected Annual Savings: ${total_savings:,.0f}**")

    st.info("Note: These are estimated savings based on a simplified model. The actual savings may vary depending on the specific operational conditions.")