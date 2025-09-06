import streamlit as st
import pandas as pd
from ...utils.data_loader import load_container_throughput

def render_data_table(enhanced_analysis):
    """
    Renders the data table view with enhanced cargo analysis data.
    
    Args:
        enhanced_analysis (pd.DataFrame): DataFrame containing enhanced cargo analysis data.
    """
    st.subheader("Enhanced Cargo Analysis Data")
    
    if enhanced_analysis is not None and not enhanced_analysis.empty:
        st.dataframe(enhanced_analysis)
    else:
        st.warning("No enhanced cargo analysis data available to display.")

    # Load data
    container_throughput = load_container_throughput()

    if not container_throughput.empty:
        st.dataframe(container_throughput)