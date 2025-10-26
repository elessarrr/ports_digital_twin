"""
This module provides utilities for tracking user experience metrics.
"""

import time
import streamlit as st

def track_time_on_page():
    """Tracks the time a user spends on the current page."""
    if 'start_time' not in st.session_state:
        st.session_state.start_time = time.time()

    # This is a placeholder for a more sophisticated implementation
    # that would send this data to a tracking service.
    time_on_page = time.time() - st.session_state.start_time
    return time_on_page

def get_user_feedback():
    """Gets user feedback on the dashboard."""
    feedback = st.radio("Did you find this dashboard useful?", ("Yes", "No"))
    if st.button("Submit Feedback"):
        # In a real application, this feedback would be stored.
        st.write("Thank you for your feedback!")
    return feedback