import streamlit as st
from ..components.kpi_summary import render_kpi_summary
from ..components.interactive_charts import render_interactive_charts
from ..components.data_table_view import render_data_table

class DashboardPage:
    def render(self, data):
        st.header("🏠 Dashboard")
        st.write("Welcome to the new and improved Hong Kong Port Digital Twin dashboard!")
        
        render_kpi_summary()
        render_interactive_charts()
        render_data_table()