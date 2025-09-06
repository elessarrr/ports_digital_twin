import streamlit as st
from ..components.layout import LayoutManager
from ..styles.theme_manager import ThemeManager
from ..components.user_preferences import UserPreferences

class SettingsPage:
    def __init__(self, theme_manager: ThemeManager, user_preferences: UserPreferences):
        self.theme_manager = theme_manager
        self.user_preferences = user_preferences

    def render(self, data):
        LayoutManager.create_section_header("⚙️ Settings", "Adjust application settings and preferences")

        with LayoutManager.create_card("Display Settings"):
            st.write("Theme")
            current_theme = self.theme_manager.get_current_theme()
            theme_options = self.theme_manager.get_available_themes()
            selected_theme = st.selectbox(
                "Theme", 
                theme_options, 
                index=theme_options.index(current_theme) if current_theme in theme_options else 0
            )
            if selected_theme != current_theme:
                self.theme_manager.set_theme(selected_theme)
                st.rerun()

        LayoutManager.add_spacing("lg")

        with LayoutManager.create_card("Notification Settings"):
            settings = self.user_preferences.load_settings()
            enable_notifications = st.checkbox("Enable real-time notifications", value=settings.get('enable_notifications', True))
            notification_frequency = st.slider("Notification frequency (minutes)", 1, 60, settings.get('notification_frequency', 5))
            
            if enable_notifications != settings.get('enable_notifications') or notification_frequency != settings.get('notification_frequency'):
                self.user_preferences.save_settings({
                    'enable_notifications': enable_notifications,
                    'notification_frequency': notification_frequency
                })


        LayoutManager.add_spacing("lg")

        with LayoutManager.create_card("Data Settings"):
            settings = self.user_preferences.load_settings()
            auto_refresh = st.checkbox("Auto-refresh data", value=settings.get('auto_refresh', True))
            refresh_interval = st.slider("Refresh interval (seconds)", 10, 300, settings.get('refresh_interval', 60))

            if auto_refresh != settings.get('auto_refresh') or refresh_interval != settings.get('refresh_interval'):
                self.user_preferences.save_settings({
                    'auto_refresh': auto_refresh,
                    'refresh_interval': refresh_interval
                })