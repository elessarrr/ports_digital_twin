import streamlit as st
from datetime import datetime
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import components
from .components.navigation import NavigationFramework
from .components.layout import LayoutManager
from .components.user_preferences import UserPreferences
from .styles.theme_manager import ThemeManager
from .pages.dashboard_page import DashboardPage
from .pages.operations_page import OperationsPage
from .pages.analytics_page import AnalyticsPage
from .pages.scenarios_page import ScenariosPage
from .pages.settings_page import SettingsPage

# Import data utilities
try:
    from src.data.data_loader import DataLoader
    from src.data.sample_data_generator import SampleDataGenerator
except ImportError:
    # Fallback if data modules are not available
    DataLoader = None
    SampleDataGenerator = None

class PortDashboardApp:
    """Main application class for the Hong Kong Port Digital Twin Dashboard"""
    
    def __init__(self):
        self.navigation = NavigationFramework()
        self.layout = LayoutManager()
        self.theme_manager = ThemeManager()
        self.user_preferences = UserPreferences()
        self.data_loader = DataLoader() if DataLoader else None
        self.sample_generator = SampleDataGenerator() if SampleDataGenerator else None
        
        # Initialize pages
        self.pages = {
            'dashboard': DashboardPage(),
            'operations': OperationsPage(),
            'analytics': AnalyticsPage(self.layout),
            'scenarios': ScenariosPage(self.layout),
            'settings': SettingsPage()
        }
        
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state variables"""
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'dashboard'
        
        if 'dashboard_settings' not in st.session_state:
            st.session_state.dashboard_settings = self.user_preferences.load_settings()
        
        if 'data_cache' not in st.session_state:
            st.session_state.data_cache = {}
        
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = None
        
        if 'notifications' not in st.session_state:
            st.session_state.notifications = []
        
        if 'user_preferences' not in st.session_state:
            st.session_state.user_preferences = {
                'favorite_charts': [],
                'dashboard_layout': 'default',
                'quick_actions': ['refresh_data', 'export_report', 'view_alerts']
            }
    
    def configure_page(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="Hong Kong Port Digital Twin",
            page_icon="🚢",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': 'https://github.com/your-repo/help',
                'Report a bug': 'https://github.com/your-repo/issues',
                'About': "# Hong Kong Port Digital Twin Dashboard\n\nA comprehensive dashboard for monitoring and analyzing port operations."
            }
        )
    
    def load_data(self):
        """Load data for the dashboard"""
        try:
            if self.data_loader:
                # Try to load real data
                data = self.data_loader.load_all_data()
                st.session_state.data_cache.update(data)
            elif self.sample_generator:
                # Fallback to sample data
                data = {
                    'vessel_data': self.sample_generator.generate_vessel_data(),
                    'cargo_data': self.sample_generator.generate_cargo_data(),
                    'berth_data': self.sample_generator.generate_berth_data(),
                    'performance_data': self.sample_generator.generate_performance_data()
                }
                st.session_state.data_cache.update(data)
            else:
                # Use minimal fallback data
                self._load_fallback_data()
                
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            self._load_fallback_data()
    
    def _load_fallback_data(self):
        """Load minimal fallback data when other sources fail"""
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        # Generate basic sample data
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        
        fallback_data = {
            'vessel_data': pd.DataFrame({
                'vessel_id': [f'V{i:03d}' for i in range(1, 21)],
                'vessel_name': [f'Vessel {i}' for i in range(1, 21)],
                'status': np.random.choice(['Docked', 'Anchored', 'Departed'], 20),
                'berth': np.random.choice(['B1', 'B2', 'B3', 'B4', 'B5'], 20),
                'arrival_time': pd.to_datetime(np.random.choice(dates, 20)),
                'cargo_volume': np.random.randint(1000, 10000, 20)
            }),
            'cargo_data': pd.DataFrame({
                'date': dates,
                'containers_handled': np.random.randint(5000, 15000, len(dates)),
                'bulk_cargo': np.random.randint(2000, 8000, len(dates)),
                'general_cargo': np.random.randint(1000, 5000, len(dates))
            }),
            'berth_data': pd.DataFrame({
                'berth_id': ['B1', 'B2', 'B3', 'B4', 'B5'],
                'status': ['Occupied', 'Available', 'Occupied', 'Maintenance', 'Occupied'],
                'utilization': [85, 0, 92, 0, 78],
                'current_vessel': ['V001', None, 'V003', None, 'V005']
            }),
            'performance_data': pd.DataFrame({
                'date': dates,
                'throughput': np.random.randint(8000, 12000, len(dates)),
                'efficiency': np.random.uniform(75, 95, len(dates)),
                'turnaround_time': np.random.uniform(18, 36, len(dates))
            })
        }
        
        st.session_state.data_cache.update(fallback_data)
    
    def handle_navigation(self):
        """Handle navigation and page routing"""
        # Render navigation sidebar
        selected_page = self.navigation.render_sidebar_navigation()
        
        # Update current page if changed
        if selected_page and selected_page != st.session_state.current_page:
            st.session_state.current_page = selected_page
            st.rerun()
        
        # Render breadcrumbs
        self.navigation.render_breadcrumb(st.session_state.current_page)
        
        # Render quick actions
        self.navigation.render_quick_actions()
    
    def render_page_content(self):
        """Render the content for the current page"""
        current_page = st.session_state.current_page
        
        try:
            if current_page in self.pages:
                # Load fresh data if needed
                if self._should_refresh_data():
                    self.load_data()
                
                # Render the page with data
                self.pages[current_page].render(st.session_state.data_cache)
            else:
                st.error(f"Page '{current_page}' not found")
                
        except Exception as e:
            st.error(f"Error rendering page: {str(e)}")
            st.exception(e)
    
    def _should_refresh_data(self) -> bool:
        """Check if data should be refreshed"""
        settings = st.session_state.dashboard_settings
        
        if not settings.get('auto_refresh', True):
            return False
        
        if st.session_state.last_refresh is None:
            return True
        
        refresh_interval = settings.get('refresh_interval', 30)
        time_since_refresh = (datetime.now() - st.session_state.last_refresh).total_seconds()
        
        return time_since_refresh > refresh_interval
    
    def render_system_status(self):
        """Render system status in sidebar"""
        if st.session_state.dashboard_settings.get('show_system_status', True):
            self.navigation.render_system_status()
    
    def handle_notifications(self):
        """Handle and display notifications"""
        if st.session_state.dashboard_settings.get('show_notifications', True):
            notifications = st.session_state.get('notifications', [])
            
            if notifications:
                with st.sidebar:
                    st.markdown("### 🔔 Notifications")
                    for i, notification in enumerate(notifications[-5:]):  # Show last 5
                        with st.expander(f"{notification.get('title', 'Notification')}", expanded=False):
                            st.write(notification.get('message', ''))
                            if st.button(f"Dismiss", key=f"dismiss_{i}"):
                                st.session_state.notifications.remove(notification)
                                st.rerun()
    
    def add_notification(self, title: str, message: str, type: str = 'info'):
        """Add a notification to the system"""
        notification = {
            'title': title,
            'message': message,
            'type': type,
            'timestamp': datetime.now()
        }
        
        if 'notifications' not in st.session_state:
            st.session_state.notifications = []
        
        st.session_state.notifications.append(notification)
        
        # Keep only last 20 notifications
        if len(st.session_state.notifications) > 20:
            st.session_state.notifications = st.session_state.notifications[-20:]
    
    def _apply_theme(self):
        """Apply the selected theme from user settings"""
        theme_settings = st.session_state.dashboard_settings.get('display', {})
        theme = theme_settings.get('theme', 'Light')
        self.theme_manager.apply_theme(theme)

    def run(self):
        """Main application entry point"""
        # Note: Page configuration is handled by the parent streamlit_app.py
        # to avoid "set_page_config() can only be called once" error
        
        # Apply theme
        self._apply_theme()
        
        # Load initial data
        if not st.session_state.data_cache:
            with st.spinner("Loading dashboard data..."):
                self.load_data()
        
        # Handle navigation
        self.handle_navigation()
        
        # Render system status
        self.render_system_status()
        
        # Handle notifications
        self.handle_notifications()
        
        # Render main content
        self.render_page_content()
        
        # Update last refresh time
        st.session_state.last_refresh = datetime.now()

def main():
    """Main function to run the application"""
    app = PortDashboardApp()
    app.run()

if __name__ == "__main__":
    main()