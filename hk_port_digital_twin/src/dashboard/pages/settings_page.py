import streamlit as st
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

from components.layout import LayoutManager
from styles.theme_manager import ThemeManager
from components.user_preferences import UserPreferences

class SettingsPage:
    """Settings page for user preferences, system configuration, and theme settings"""
    
    def __init__(self, layout_manager: LayoutManager):
        self.layout = layout_manager
        self.user_preferences = UserPreferences()
    
    def render(self, data: Dict[str, Any]) -> None:
        """Render the settings page"""
        # Apply custom CSS
        self.layout.apply_custom_css()
        
        # Page header
        self.layout.create_section_header(
            "Settings & Configuration",
            "Customize your dashboard experience and system preferences",
            "⚙️"
        )
        
        # Create tabs for different settings categories
        tab_names = ["General", "Display", "Notifications", "Data Sources", "Advanced"]
        tab_icons = ["🏠", "🎨", "🔔", "📊", "🔧"]
        
        tabs = self.layout.create_tabs_container(tab_names, tab_icons)
        
        with tabs[0]:
            self._render_general_settings()
        
        with tabs[1]:
            self._render_display_settings()
        
        with tabs[2]:
            self._render_notification_settings()
        
        with tabs[3]:
            self._render_data_source_settings()
        
        with tabs[4]:
            self._render_advanced_settings()
        
        # Save settings button
        self.layout.add_spacing('lg')
        
        cols = st.columns([1, 2, 1])
        with cols[1]:
            if st.button("💾 Save All Settings", type="primary", use_container_width=True):
                self._save_settings()
                st.success("Settings saved successfully!")
                st.rerun()
    
    def _render_general_settings(self) -> None:
        """Render general settings section"""
        self.layout.add_spacing('md')
        
        st.markdown("### 🏠 General Settings")
        
        # Load current settings
        current_settings = self._load_settings()
        general_settings = current_settings.get('settings_general', {})
        
        with self.layout.create_card("User Preferences"):
        
            cols = self.layout.create_columns('half')
            
            with cols[0]:
                # Default page
                default_page = st.selectbox(
                    "Default Landing Page",
                    options=["Dashboard", "Operations", "Analytics", "Settings"],
                    index=self._get_option_index(
                        ["Dashboard", "Operations", "Analytics", "Settings"],
                        general_settings.get('default_page', 'Dashboard')
                    ),
                    key="default_page",
                    help="Page to display when opening the dashboard"
                )
                
                # Auto-refresh interval
                refresh_interval = st.selectbox(
                    "Auto-refresh Interval",
                    options=["Off", "30 seconds", "1 minute", "5 minutes", "10 minutes"],
                    index=self._get_option_index(
                        ["Off", "30 seconds", "1 minute", "5 minutes", "10 minutes"],
                        general_settings.get('refresh_interval', '5 minutes')
                    ),
                    key="refresh_interval",
                    help="How often to automatically refresh data"
                )
            
            with cols[1]:
                # Language
                language = st.selectbox(
                    "Language",
                    options=["English", "中文", "Español", "Français"],
                    index=self._get_option_index(
                        ["English", "中文", "Español", "Français"],
                        general_settings.get('language', 'English')
                    ),
                    key="language",
                    help="Dashboard display language"
                )
                
                # Timezone
                timezone = st.selectbox(
                    "Timezone",
                    options=["UTC", "Asia/Hong_Kong", "America/New_York", "Europe/London", "Asia/Shanghai"],
                    index=self._get_option_index(
                        ["UTC", "Asia/Hong_Kong", "America/New_York", "Europe/London", "Asia/Shanghai"],
                        general_settings.get('timezone', 'Asia/Hong_Kong')
                    ),
                    key="timezone",
                    help="Timezone for displaying dates and times"
                )
        
        self.layout.add_spacing('md')
        
        with self.layout.create_card("Performance Settings"):
        
            cols = self.layout.create_columns('half')
            
            with cols[0]:
                # Cache duration
                cache_duration = st.slider(
                    "Data Cache Duration (minutes)",
                    min_value=1,
                    max_value=60,
                    value=general_settings.get('cache_duration', 10),
                    key="cache_duration",
                    help="How long to cache data before refreshing"
                )
            
            with cols[1]:
                # Max data points
                max_data_points = st.slider(
                    "Max Chart Data Points",
                    min_value=50,
                    max_value=1000,
                    value=general_settings.get('max_data_points', 200),
                    step=50,
                    key="max_data_points",
                    help="Maximum number of data points to display in charts"
                )
        
        # Update session state
        self._update_session_state('general', {
            'default_page': default_page,
            'refresh_interval': refresh_interval,
            'language': language,
            'timezone': timezone,
            'cache_duration': cache_duration,
            'max_data_points': max_data_points
        })
    
    def _render_display_settings(self) -> None:
        """Render display settings section"""
        self.layout.add_spacing('md')
        
        st.markdown("### 🎨 Display Settings")
        
        current_settings = self._load_settings()
        display_settings = current_settings.get('settings_display', {})
        
        with self.layout.create_card("Theme & Appearance"):
            
            cols = self.layout.create_columns('half')
            
            with cols[0]:
                # Theme selection
                theme = st.selectbox(
                    "Theme",
                    options=["Light", "Dark", "Auto"],
                    index=self._get_option_index(
                        ["Light", "Dark", "Auto"],
                        display_settings.get('theme', 'Light')
                    ),
                    key="theme",
                    help="Choose the dashboard's color theme"
                )
                
                # Color scheme
                color_scheme = st.selectbox(
                    "Color Scheme",
                    options=["Default", "Blue", "Green", "Purple", "Orange"],
                    index=self._get_option_index(
                        ["Default", "Blue", "Green", "Purple", "Orange"],
                        display_settings.get('color_scheme', 'Default')
                    ),
                    key="color_scheme",
                    help="Primary color scheme for charts and UI elements"
                )
            
            with cols[1]:
                # Font size
                font_size = st.selectbox(
                    "Font Size",
                    options=["Small", "Medium", "Large", "Extra Large"],
                    index=self._get_option_index(
                        ["Small", "Medium", "Large", "Extra Large"],
                        display_settings.get('font_size', 'Medium')
                    ),
                    key="font_size",
                    help="Base font size for the dashboard"
                )
                
                # Sidebar width
                sidebar_width = st.selectbox(
                    "Sidebar Width",
                    options=["Narrow", "Medium", "Wide"],
                    index=self._get_option_index(
                        ["Narrow", "Medium", "Wide"],
                        display_settings.get('sidebar_width', 'Medium')
                    ),
                    key="sidebar_width",
                    help="Width of the navigation sidebar"
                )
        
        self.layout.add_spacing('md')
        
        with self.layout.create_card("Layout Settings"):
        
            cols = self.layout.create_columns('half')
            
            with cols[0]:
                # Compact mode
                compact_mode = st.checkbox(
                    "Compact Mode",
                    value=display_settings.get('compact_mode', False),
                    key="compact_mode",
                    help="Reduce spacing and padding for more content"
                )
                
                # Show grid lines
                show_grid_lines = st.checkbox(
                    "Show Grid Lines in Charts",
                    value=display_settings.get('show_grid_lines', True),
                    key="show_grid_lines",
                    help="Display grid lines in charts and graphs"
                )
            
            with cols[1]:
                # Animation
                enable_animations = st.checkbox(
                    "Enable Animations",
                    value=display_settings.get('enable_animations', True),
                    key="enable_animations",
                    help="Enable smooth transitions and animations"
                )
                
                # High contrast
                high_contrast = st.checkbox(
                    "High Contrast Mode",
                    value=display_settings.get('high_contrast', False),
                    key="high_contrast",
                    help="Increase contrast for better accessibility"
                )
        
        # Update session state
        self._update_session_state('display', {
            'theme': theme,
            'color_scheme': color_scheme,
            'font_size': font_size,
            'sidebar_width': sidebar_width,
            'compact_mode': compact_mode,
            'show_grid_lines': show_grid_lines,
            'enable_animations': enable_animations,
            'high_contrast': high_contrast
        })
    
    def _render_notification_settings(self) -> None:
        """Render notification settings section"""
        self.layout.add_spacing('md')
        
        st.markdown("### 🔔 Notification Settings")
        
        current_settings = self._load_settings()
        notification_settings = current_settings.get('settings_notifications', {})
        
        with self.layout.create_card("Alert Preferences"):
        
            cols = self.layout.create_columns('half')
            
            with cols[0]:
                # Enable notifications
                enable_notifications = st.checkbox(
                    "Enable Notifications",
                    value=notification_settings.get('enable_notifications', True),
                    key="enable_notifications",
                    help="Receive system notifications and alerts"
                )
                
                # Email notifications
                email_notifications = st.checkbox(
                    "Email Notifications",
                    value=notification_settings.get('email_notifications', False),
                    key="email_notifications",
                    help="Receive notifications via email",
                    disabled=not enable_notifications
                )
                
                # Sound alerts
                sound_alerts = st.checkbox(
                    "Sound Alerts",
                    value=notification_settings.get('sound_alerts', True),
                    key="sound_alerts",
                    help="Play sound for important alerts",
                    disabled=not enable_notifications
                )
            
            with cols[1]:
                # Alert types
                st.markdown("**Alert Types:**")
                
                system_alerts = st.checkbox(
                    "System Alerts",
                    value=notification_settings.get('system_alerts', True),
                    key="system_alerts",
                    help="Alerts for system status and errors",
                    disabled=not enable_notifications
                )
                
                operational_alerts = st.checkbox(
                    "Operational Alerts",
                    value=notification_settings.get('operational_alerts', True),
                    key="operational_alerts",
                    help="Alerts for operational events and thresholds",
                    disabled=not enable_notifications
                )
                
                performance_alerts = st.checkbox(
                    "Performance Alerts",
                    value=notification_settings.get('performance_alerts', False),
                    key="performance_alerts",
                    help="Alerts for performance metrics and KPIs",
                    disabled=not enable_notifications
                )
        
        self.layout.add_spacing('md')
        
        # Threshold settings
        st.markdown("#### Alert Thresholds")
        
        if enable_notifications:
            cols = self.layout.create_columns('third')
            
            with cols[0]:
                berth_utilization_threshold = st.slider(
                    "Berth Utilization Alert (%)",
                    min_value=50,
                    max_value=100,
                    value=notification_settings.get('berth_utilization_threshold', 85),
                    key="berth_utilization_threshold",
                    help="Alert when berth utilization exceeds this percentage"
                )
            
            with cols[1]:
                vessel_queue_threshold = st.slider(
                    "Vessel Queue Alert",
                    min_value=1,
                    max_value=20,
                    value=notification_settings.get('vessel_queue_threshold', 5),
                    key="vessel_queue_threshold",
                    help="Alert when vessel queue exceeds this number"
                )
            
            with cols[2]:
                efficiency_threshold = st.slider(
                    "Efficiency Alert (%)",
                    min_value=50,
                    max_value=100,
                    value=notification_settings.get('efficiency_threshold', 75),
                    key="efficiency_threshold",
                    help="Alert when efficiency drops below this percentage"
                )
        else:
            st.info("Enable notifications to configure alert thresholds")
        
        # Update session state
        self._update_session_state('notifications', {
            'enable_notifications': enable_notifications,
            'email_notifications': email_notifications,
            'sound_alerts': sound_alerts,
            'system_alerts': system_alerts,
            'operational_alerts': operational_alerts,
            'performance_alerts': performance_alerts,
            'berth_utilization_threshold': notification_settings.get('berth_utilization_threshold', 85) if enable_notifications else 85,
            'vessel_queue_threshold': notification_settings.get('vessel_queue_threshold', 5) if enable_notifications else 5,
            'efficiency_threshold': notification_settings.get('efficiency_threshold', 75) if enable_notifications else 75
        })
    
    def _render_data_source_settings(self) -> None:
        """Render data sources settings section"""
        self.layout.add_spacing('md')
        
        st.markdown("### 📊 Data Sources Settings")
        
        current_settings = self._load_settings()
        data_sources_settings = current_settings.get('settings_data_sources', {})
        
        with self.layout.create_card("Data Source Configuration"):
        
            # Data source selection
            data_source = st.selectbox(
                "Primary Data Source",
                options=["Real-time API", "Database (Simulation)", "CSV (Static)"],
                index=self._get_option_index(
                    ["Real-time API", "Database (Simulation)", "CSV (Static)"],
                    data_sources_settings.get('primary_data_source', "Database (Simulation)")
                ),
                key="primary_data_source",
                help="Select the primary source for dashboard data"
            )
            
            self.layout.add_spacing('sm')
            
            # API endpoint
            api_endpoint = st.text_input(
                "API Endpoint",
                value=data_sources_settings.get('api_endpoint', "https://api.example.com/port-data"),
                key="api_endpoint",
                help="URL for the real-time data API",
                disabled=(data_source != "Real-time API")
            )
            
            # Database connection string
            db_connection_string = st.text_input(
                "Database Connection String",
                value=data_sources_settings.get('db_connection_string', "postgresql://user:password@host:port/database"),
                key="db_connection_string",
                help="Connection string for the simulation database",
                disabled=(data_source != "Database (Simulation)")
            )
            
            self.layout.add_spacing('sm')
            
            # Data refresh interval
            refresh_interval = st.slider(
                "Data Refresh Interval (seconds)",
                min_value=10,
                max_value=300,
                value=data_sources_settings.get('refresh_interval', 60),
                step=10,
                key="refresh_interval",
                help="How often to refresh data from the source"
            )
        
        # Update session state
        self._update_session_state('data_sources', {
            'primary_data_source': data_source,
            'api_endpoint': api_endpoint,
            'db_connection_string': db_connection_string,
            'refresh_interval': refresh_interval
        })
    
    def _render_advanced_settings(self) -> None:
        """Render advanced settings section"""
        self.layout.add_spacing('md')
        
        st.markdown("### 🔧 Advanced Settings")
        
        current_settings = self._load_settings()
        advanced_settings = current_settings.get('settings_advanced', {})
        
        self.layout.add_spacing('md')

        with self.layout.create_card("A/B Testing"):
            st.markdown("Switch between different UI variants to compare performance and user experience.")

            ui_variant = st.selectbox(
                "UI Variant",
                options=["Variant A (Control)", "Variant B (New)"],
                index=0,
                key="ui_variant",
                help="Select a UI variant to display."
            )

        self.layout.add_spacing('md')

        self.layout.add_spacing('md')

        with self.layout.create_card("Monitoring"):
            st.markdown("Configure real-time monitoring settings.")

            cols = self.layout.create_columns('half')

            with cols[0]:
                enable_monitoring = st.checkbox(
                    "Enable Real-Time Monitoring",
                    value=True,
                    key="enable_monitoring",
                    help="Enable or disable real-time data monitoring."
                )

            with cols[1]:
                refresh_interval = st.slider(
                    "Refresh Interval (seconds)",
                    min_value=5,
                    max_value=60,
                    value=10,
                    step=5,
                    key="refresh_interval",
                    help="Set the refresh interval for real-time data."
                )

        with self.layout.create_card("Logging"):
            st.markdown("Configure logging levels and download log files.")

            cols = self.layout.create_columns('half')

            with cols[0]:
                log_level = st.selectbox(
                    "Log Level",
                    options=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                    index=1,
                    key="log_level",
                    help="Set the minimum level of logs to record."
                )

            with cols[1]:
                st.download_button(
                    label="Download Log File",
                    data="", # This should be replaced with the actual log file content
                    file_name="dashboard.log",
                    mime="text/plain"
                )

        with self.layout.create_card("Developer Options"):
            st.markdown("These settings are intended for developers and may impact performance.")
            
            cols = self.layout.create_columns('half')
            
            with cols[0]:
                enable_debug_mode = st.checkbox(
                    "Enable Debug Mode",
                    value=advanced_settings.get('enable_debug_mode', False),
                    key="enable_debug_mode",
                    help="Show detailed error messages and logs"
                )
            
            with cols[1]:
                show_performance_metrics = st.checkbox(
                    "Show Performance Metrics",
                    value=advanced_settings.get('show_performance_metrics', False),
                    key="show_performance_metrics",
                    help="Display rendering times and memory usage"
                )

        self.layout.add_spacing('md')

        with self.layout.create_card("Feature Flags"):
            st.markdown("Enable or disable experimental features. Use with caution.")

            cols = self.layout.create_columns('half')

            with cols[0]:
                enable_ai_forecasts = st.checkbox(
                    "Enable Alpha Features",
                    value=advanced_settings.get('enable_alpha_features', False),
                    key="enable_alpha_features",
                    help="Get access to the earliest, most unstable features."
                )

            with cols[1]:
                enable_simulation_scenarios = st.checkbox(
                    "Enable Beta Features",
                    value=advanced_settings.get('enable_beta_features', True),
                    key="enable_beta_features",
                    help="Try out new features before they are officially released."
                )
        
        self.layout.add_spacing('md')
        
        with self.layout.create_card("Data Management"):
            st.markdown("Export or import your application settings.")
            
            cols = self.layout.create_columns('half')
            
            with cols[0]:
                self._export_settings()
            
            with cols[1]:
                uploaded_file = st.file_uploader(
                    "Import Settings File",
                    type=['json'],
                    key="import_settings_uploader"
                )
                if uploaded_file is not None:
                    self._import_settings(uploaded_file)
        
        self.layout.add_spacing('md')
        
        with self.layout.create_card("System Reset", border_color="#FF4B4B"):
            
            cols = self.layout.create_columns([1, 1, 1])
            
            with cols[0]:
                if st.button("Reset All Settings", key="reset_settings"):
                    self._reset_to_defaults()
                    st.success("All settings have been reset to their defaults!")
                    st.rerun()
            
            with cols[1]:
                if st.button("Clear All Cached Data", key="clear_cache"):
                    self._clear_all_cache()
                    st.success("All cached data has been cleared!")
            
            with cols[2]:
                if st.button("Factory Reset", key="factory_reset"):
                    self._factory_reset()
                    st.success("Application has been reset to its initial state.")
                    st.rerun()

        # Update session state
        self._update_session_state('advanced', {
            'enable_debug_mode': enable_debug_mode,
            'show_performance_metrics': show_performance_metrics,
            'enable_alpha_features': enable_alpha,
            'enable_beta_features': enable_beta,
            'ui_variant': ui_variant,
            'log_level': log_level,
            'enable_monitoring': enable_monitoring,
            'refresh_interval': refresh_interval
        })
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from session state or file via UserPreferences"""
        if 'dashboard_settings' not in st.session_state:
            st.session_state.dashboard_settings = self.user_preferences.load_settings()
        return st.session_state.dashboard_settings

    def _save_settings(self) -> None:
        """Save current settings using UserPreferences"""
        try:
            # Collect all settings from session state
            all_settings = {
                'settings_general': st.session_state.get('settings_general', {}),
                'settings_display': st.session_state.get('settings_display', {}),
                'settings_notifications': st.session_state.get('settings_notifications', {}),
                'settings_data_sources': st.session_state.get('settings_data_sources', {}),
                'settings_advanced': st.session_state.get('settings_advanced', {})
            }

            # Save using the UserPreferences object
            self.user_preferences.save_settings(all_settings)

            # Update session state
            st.session_state.dashboard_settings = all_settings

        except Exception as e:
            st.error(f"Error saving settings: {e}")
    
    def _factory_reset(self) -> None:
        """Perform a factory reset, clearing all settings and cache"""
        self._reset_to_defaults()
        self._clear_all_cache()

        """Update session state with new settings"""
        if f'settings_{category}' not in st.session_state:
            st.session_state[f'settings_{category}'] = {}
        st.session_state[f'settings_{category}'].update(settings)

    def _get_option_index(self, options: List[str], value: Optional[str]) -> int:
        """Get the index of a value in a list of options"""
        try:
            return options.index(value)
        except (ValueError, TypeError):
            return 0

    def _clear_all_cache(self) -> None:
        """Clear all cached data"""
        # This would typically involve clearing st.cache_data or other caching mechanisms
        st.cache_data.clear()
        st.success("All cached data has been cleared!")
    
    def _export_settings(self) -> None:
        """Export current settings"""
        try:
            current_settings = self._load_settings()
            
            # Create download data
            settings_json = json.dumps(current_settings, indent=2, default=str)
            
            st.download_button(
                label="Download Settings File",
                data=settings_json,
                file_name=f"dashboard_settings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"Error exporting settings: {e}")
    
    def _import_settings(self, uploaded_file) -> None:
        """Import settings from uploaded file"""
        try:
            # Read uploaded file
            settings_data = json.load(uploaded_file)
            
            # Validate settings (basic validation)
            if isinstance(settings_data, dict):
                # Save imported settings
                self.user_preferences.save_settings(settings_data)
                
                # Update session state
                st.session_state.dashboard_settings = settings_data
                
                st.success("Settings imported successfully!")
                st.rerun()
            else:
                st.error("Invalid settings file format")
                
        except Exception as e:
            st.error(f"Error importing settings: {e}")
    
    def _reset_to_defaults(self) -> None:
        """Reset all settings to defaults"""
        try:
            default_settings = self.user_preferences.get_default_settings()

            # Save default settings using the UserPreferences object
            self.user_preferences.save_settings(default_settings)

            # Clear session state to force a reload from file on the next run
            for key in list(st.session_state.keys()):
                if key.startswith('settings_') or key == 'dashboard_settings':
                    del st.session_state[key]

        except Exception as e:
            st.error(f"Error resetting settings: {e}")

def create_settings_page(layout_manager: LayoutManager) -> SettingsPage:
    """Factory function to create settings page"""
    return SettingsPage(layout_manager)