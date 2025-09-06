import streamlit as st
import pandas as pd

def render_operational_view(data):
    """
    Renders the operational view, combining vessel movements and berth occupancy.

    Args:
        data (dict): A dictionary containing the data for the view.
    """
    st.subheader("Vessel Movements")
    vessel_arrivals = data.get('vessel_arrivals')
    arriving_ships = data.get('arriving_ships')

    if vessel_arrivals is not None and not vessel_arrivals.empty:
        st.write("Vessel Arrivals:", vessel_arrivals)
    else:
        st.warning("No vessel arrival data available.")

    if arriving_ships is not None and not arriving_ships.empty:
        st.write("Arriving Ships:", arriving_ships)
    else:
        st.warning("No arriving ships data available.")

    st.subheader("Berth Occupancy")
    st.warning("Berth occupancy data is not yet available.")