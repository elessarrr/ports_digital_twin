import streamlit as st
import pandas as pd
from ...utils.data_loader import load_vessel_arrivals, load_arriving_ships

def render_vessel_movements():
    st.subheader("Vessel Movements")

    # Load data
    arrived_vessels = load_vessel_arrivals()
    expected_arrivals = load_arriving_ships()

    col1, col2 = st.columns(2)

    with col1:
        st.info("Recent Arrivals")
        if not arrived_vessels.empty:
            st.dataframe(arrived_vessels.head())
        else:
            st.write("No recent arrivals data available.")

        st.info("Expected Arrivals")
        if not expected_arrivals.empty:
            st.dataframe(expected_arrivals.head())
        else:
            st.write("No expected arrivals data available.")

    with col2:
        st.info("Recent Departures")
        st.write("Data source for recent departures is currently unavailable.")

        st.info("Expected Departures")
        st.write("Data source for expected departures is currently unavailable.")