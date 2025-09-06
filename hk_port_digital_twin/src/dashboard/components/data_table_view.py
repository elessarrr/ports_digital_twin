import streamlit as st
import pandas as pd
from ...utils.data_loader import load_container_throughput

def render_data_table():
    """
    Renders an interactive data table of the container throughput data.

    This function loads the container throughput data and displays it in a 
    Streamlit dataframe, allowing for easy sorting, filtering, and exploration 
    of the raw data.
    """
    st.subheader("Container Throughput Data")

    # Load data
    container_throughput = load_container_throughput()

    if not container_throughput.empty:
        st.dataframe(container_throughput)