import streamlit as st
import time

class RealTimeUpdater:
    """
    A class to handle real-time data updates in the Streamlit app.
    """
    def __init__(self, update_interval=5):
        self.update_interval = update_interval

    def run(self):
        """
        Runs the real-time update loop.
        """
        if 'last_update' not in st.session_state:
            st.session_state.last_update = time.time()

        if time.time() - st.session_state.last_update > self.update_interval:
            st.session_state.last_update = time.time()
            st.rerun()