import streamlit as st
from ..components.layout import LayoutManager
from ..styles.theme_manager import ThemeManager
from ..components.simulation_controls import render_simulation_controls

class SimulationPage:
    def render(self):
        st.header("🔬 Simulation")
        render_simulation_controls()