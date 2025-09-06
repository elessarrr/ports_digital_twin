import streamlit as st
from ..components.vessel_movements import render_vessel_movements

class OperationsPage:
    def render(self, data):
        st.header("🚢 Operations")
        render_vessel_movements()