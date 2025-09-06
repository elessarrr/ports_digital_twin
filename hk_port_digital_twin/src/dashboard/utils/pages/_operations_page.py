import streamlit as st
from ..components.operational_view import render_operational_view
from ..components.layout import LayoutManager

class OperationsPage:
    def render(self, data):
        LayoutManager.create_section_header("🚢 Operations", "Real-time vessel and berth status")
        
        with st.container():
            with LayoutManager.create_card():
                render_operational_view(data)