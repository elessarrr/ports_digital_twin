import streamlit as st
from components.navigation import NavigationFramework
from pages.dashboard_page import DashboardPage
from pages.operations_page import OperationsPage
from pages.simulation_page import SimulationPage
from pages.analysis_page import AnalysisPage
from pages.settings_page import SettingsPage

class MainApp:
    def __init__(self):
        self.nav = NavigationFramework()
        self.pages = {
            "dashboard": DashboardPage(),
            "operations": OperationsPage(),
            "simulation": SimulationPage(),
            "analysis": AnalysisPage(),
            "settings": SettingsPage(),
        }
        self.setup_page()

    def setup_page(self):
        st.set_page_config(
            page_title="HK Port Digital Twin",
            page_icon="🏗️",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    def run(self):
        selected_section = self.nav.render_sidebar_navigation()
        self.nav.render_breadcrumb(selected_section)

        if selected_section in self.pages:
            self.pages[selected_section].render()
        else:
            st.header(f"{self.nav.get_section_config(selected_section).get('icon', '')} {self.nav.get_section_config(selected_section).get('title', 'Unknown')}")
            st.write(f"Content for {selected_section} coming soon.")

        self.nav.render_quick_actions()
        self.nav.render_system_status()

if __name__ == "__main__":
    app = MainApp()
    app.run()