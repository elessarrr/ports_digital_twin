import streamlit as st
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

from components.layout import LayoutManager
from styles.theme_manager import ThemeManager

class SettingsPage:
    """Settings page for user preferences, system configuration, and theme settings"""
    
    def __init__(self, layout_manager: LayoutManager):
        self.layout = layout_manager
        self.settings_file = "dashboard_settings.json"
    
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
        
        # User preferences
        st.markdown("#### User Preferences")
        
        cols = self.layout.create_columns('half')
        
        with cols[0]:
            # Default page
            default_page = st.selectbox(
                "Default Landing Page",
                options=["Dashboard", "Operations", "Analytics", "Settings"],
                index=self._get_option_index(
                    ["Dashboard", "Operations", "Analytics", "Settings"],
                    current_settings.get('default_page', 'Dashboard')
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
                    current_settings.get('refresh_interval', '5 minutes')
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
                    current_settings.get('language', 'English')
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
                    current_settings.get('timezone', 'Asia/Hong_Kong')
                ),
                key="timezone",
                help="Timezone for displaying dates and times"
            )
        
        self.layout.add_spacing('md')
        
        # Performance settings
        st.markdown("#### Performance Settings")
        
        cols = self.layout.create_columns('half')
        
        with cols[0]:
            # Cache duration
            cache_duration = st.slider(
                "Data Cache Duration (minutes)",
                min_value=1,
                max_value=60,
                value=current_settings.get('cache_duration', 10),
                key="cache_duration",
                help="How long to cache data before refreshing"
            )
        
        with cols[1]:
            # Max data points
            max_data_points = st.slider(
                "Max Chart Data Points",
                min_value=50,
                max_value=1000,
                value=current_settings.get('max_data_points', 200),
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
        
        # Theme settings
        st.markdown("#### Theme & Appearance")
        
        cols = self.layout.create_columns('half')
        
        with cols[0]:
            # Theme
            theme = st.selectbox(
                "Theme",
                options=["Light", "Dark", "Auto"],
                index=self._get_option_index(
                    ["Light", "Dark", "Auto"],
                    current_settings.get('theme', 'Light')
                ),
                key="theme",
                help="Dashboard color theme"
            )
            
            # Color scheme
            color_scheme = st.selectbox(
                "Color Scheme",
                options=["Default", "Blue", "Green", "Purple", "Orange"],
                index=self._get_option_index(
                    ["Default", "Blue", "Green", "Purple", "Orange"],
                    current_settings.get('color_scheme', 'Default')
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
                    current_settings.get('font_size', 'Medium')
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
                    current_settings.get('sidebar_width', 'Medium')
                ),
                key="sidebar_width",
                help="Width of the navigation sidebar"
            )
        
        self.layout.add_spacing('md')
        
        # Layout settings
        st.markdown("#### Layout Settings")
        
        cols = self.layout.create_columns('half')
        
        with cols[0]:
            # Compact mode
            compact_mode = st.checkbox(
                "Compact Mode",
                value=current_settings.get('compact_mode', False),
                key="compact_mode",
                help="Reduce spacing and padding for more content"
            )
            
            # Show grid lines
            show_grid_lines = st.checkbox(
                "Show Grid Lines in Charts",
                value=current_settings.get('show_grid_lines', True),
                key="show_grid_lines",
                help="Display grid lines in charts and graphs"
            )
        
        with cols[1]:
            # Animation
            enable_animations = st.checkbox(
                "Enable Animations",
                value=current_settings.get('enable_animations', True),
                key="enable_animations",
                help="Enable smooth transitions and animations"
            )
            
            # High contrast
            high_contrast = st.checkbox(
                "High Contrast Mode",
                value=current_settings.get('high_contrast', False),
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
        
        # Alert settings
        st.markdown("#### Alert Preferences")
        
        cols = self.layout.create_columns('half')
        
        with cols[0]:
            # Enable notifications
            enable_notifications = st.checkbox(
                "Enable Notifications",
                value=current_settings.get('enable_notifications', True),
                key="enable_notifications",
                help="Receive system notifications and alerts"
            )
            
            # Email notifications
            email_notifications = st.checkbox(
                "Email Notifications",
                value=current_settings.get('email_notifications', False),
                key="email_notifications",
                help="Receive notifications via email",
                disabled=not enable_notifications
            )
            
            # Sound alerts
            sound_alerts = st.checkbox(
                "Sound Alerts",
                value=current_settings.get('sound_alerts', True),
                key="sound_alerts",
                help="Play sound for important alerts",
                disabled=not enable_notifications
            )
        
        with cols[1]:
            # Alert types
            st.markdown("**Alert Types:**")
            
            system_alerts = st.checkbox(
                "System Alerts",
                value=current_settings.get('system_alerts', True),
                key="system_alerts",
                help="Alerts for system status and errors",
                disabled=not enable_notifications
            )
            
            operational_alerts = st.checkbox(
                "Operational Alerts",
                value=current_settings.get('operational_alerts', True),
                key="operational_alerts",
                help="Alerts for operational events and thresholds",
                disabled=not enable_notifications
            )
            
            performance_alerts = st.checkbox(
                "Performance Alerts",
                value=current_settings.get('performance_alerts', False),
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
                    value=current_settings.get('berth_utilization_threshold', 85),
                    key="berth_utilization_threshold",
                    help="Alert when berth utilization exceeds this percentage"
                )
            
            with cols[1]:
                vessel_queue_threshold = st.slider(
                    "Vessel Queue Alert",
                    min_value=1,
                    max_value=20,
                    value=current_settings.get('vessel_queue_threshold', 5),
                    key="vessel_queue_threshold",
                    help="Alert when vessel queue exceeds this number"
                )
            
            with cols[2]:
                efficiency_threshold = st.slider(
                    "Efficiency Alert (%)",
                    min_value=50,
                    max_value=100,
                    value=current_settings.get('efficiency_threshold', 75),
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
            'berth_utilization_threshold': current_settings.get('berth_utilization_threshold', 85) if enable_notifications else 85,
            'vessel_queue_threshold': current_settings.get('vessel_queue_threshold', 5) if enable_notifications else 5,
            'efficiency_threshold': current_settings.get('efficiency_threshold', 75) if enable_notifications else 75
        })
    
    def _render_data_source_settings(self) -> None:
        """Render data source settings section"""
        self.layout.add_spacing('md')
        
        st.markdown("### 📊 Data Source Settings")
        
        current_settings = self._load_settings()
        
        # Data connection settings
        st.markdown("#### Data Connections")
        
        cols = self.layout.create_columns('half')
        
        with cols[0]:
            # Primary data source
            primary_data_source = st.selectbox(
                "Primary Data Source",
                options=["Simulation", "Live Database", "API Endpoint", "File Upload"],
                index=self._get_option_index(
                    ["Simulation", "Live Database", "API Endpoint", "File Upload"],
                    current_settings.get('primary_data_source', 'Simulation')
                ),
                key="primary_data_source",
                help="Primary source for dashboard data"
            )
            
            # Update frequency
            data_update_frequency = st.selectbox(
                "Data Update Frequency",
                options=["Real-time", "Every 30 seconds", "Every minute", "Every 5 minutes", "Manual"],
                index=self._get_option_index(
                    ["Real-time", "Every 30 seconds", "Every minute", "Every 5 minutes", "Manual"],
                    current_settings.get('data_update_frequency', 'Every minute')
                ),
                key="data_update_frequency",
                help="How often to fetch new data"
            )
        
        with cols[1]:
            # Data retention
            data_retention_days = st.slider(
                "Data Retention (days)",
                min_value=7,
                max_value=365,
                value=current_settings.get('data_retention_days', 90),
                key="data_retention_days",
                help="How long to keep historical data"
            )
            
            # Enable data validation
            enable_data_validation = st.checkbox(
                "Enable Data Validation",
                value=current_settings.get('enable_data_validation', True),
                key="enable_data_validation",
                help="Validate incoming data for accuracy and completeness"
            )
        
        self.layout.add_spacing('md')
        
        # API settings (if applicable)
        if primary_data_source == "API Endpoint":
            st.markdown("#### API Configuration")
            
            api_endpoint = st.text_input(
                "API Endpoint URL",
                value=current_settings.get('api_endpoint', ''),
                key="api_endpoint",
                help="URL for the API endpoint"
            )
            
            cols = self.layout.create_columns('half')
            
            with cols[0]:
                api_key = st.text_input(
                    "API Key",
                    value=current_settings.get('api_key', ''),
                    type="password",
                    key="api_key",
                    help="API key for authentication"
                )
            
            with cols[1]:
                api_timeout = st.slider(
                    "API Timeout (seconds)",
                    min_value=5,
                    max_value=60,
                    value=current_settings.get('api_timeout', 30),
                    key="api_timeout",
                    help="Timeout for API requests"
                )
        
        # Database settings (if applicable)
        elif primary_data_source == "Live Database":
            st.markdown("#### Database Configuration")
            
            cols = self.layout.create_columns('half')
            
            with cols[0]:
                db_host = st.text_input(
                    "Database Host",
                    value=current_settings.get('db_host', 'localhost'),
                    key="db_host"
                )
                
                db_port = st.number_input(
                    "Database Port",
                    min_value=1,
                    max_value=65535,
                    value=current_settings.get('db_port', 5432),
                    key="db_port"
                )
            
            with cols[1]:
                db_name = st.text_input(
                    "Database Name",
                    value=current_settings.get('db_name', 'port_db'),
                    key="db_name"
                )
                
                db_username = st.text_input(
                    "Username",
                    value=current_settings.get('db_username', ''),
                    key="db_username"
                )
            
            db_password = st.text_input(
                "Password",
                value=current_settings.get('db_password', ''),
                type="password",
                key="db_password"
            )
        
        # Update session state
        data_settings = {
            'primary_data_source': primary_data_source,
            'data_update_frequency': data_update_frequency,
            'data_retention_days': data_retention_days,
            'enable_data_validation': enable_data_validation
        }
        
        if primary_data_source == "API Endpoint":
            data_settings.update({
                'api_endpoint': current_settings.get('api_endpoint', ''),
                'api_key': current_settings.get('api_key', ''),
                'api_timeout': current_settings.get('api_timeout', 30)
            })
        elif primary_data_source == "Live Database":
            data_settings.update({
                'db_host': current_settings.get('db_host', 'localhost'),
                'db_port': current_settings.get('db_port', 5432),
                'db_name': current_settings.get('db_name', 'port_db'),
                'db_username': current_settings.get('db_username', ''),
                'db_password': current_settings.get('db_password', '')
            })
        
        self._update_session_state('data_sources', data_settings)
    
    def _render_advanced_settings(self) -> None:
        """Render advanced settings section"""
        self.layout.add_spacing('md')
        
        st.markdown("### 🔧 Advanced Settings")
        
        current_settings = self._load_settings()
        
        # System settings
        st.markdown("#### System Configuration")
        
        cols = self.layout.create_columns('half')
        
        with cols[0]:
            # Debug mode
            debug_mode = st.checkbox(
                "Debug Mode",
                value=current_settings.get('debug_mode', False),
                key="debug_mode",
                help="Enable debug logging and error details"
            )
            
            # Enable logging
            enable_logging = st.checkbox(
                "Enable Logging",
                value=current_settings.get('enable_logging', True),
                key="enable_logging",
                help="Log system events and user actions"
            )
            
            # Performance monitoring
            performance_monitoring = st.checkbox(
                "Performance Monitoring",
                value=current_settings.get('performance_monitoring', False),
                key="performance_monitoring",
                help="Monitor and log performance metrics"
            )
        
        with cols[1]:
            # Memory limit
            memory_limit = st.slider(
                "Memory Limit (MB)",
                min_value=512,
                max_value=4096,
                value=current_settings.get('memory_limit', 1024),
                step=256,
                key="memory_limit",
                help="Maximum memory usage for the dashboard"
            )
            
            # CPU limit
            cpu_limit = st.slider(
                "CPU Usage Limit (%)",
                min_value=25,
                max_value=100,
                value=current_settings.get('cpu_limit', 80),
                step=5,
                key="cpu_limit",
                help="Maximum CPU usage percentage"
            )
        
        self.layout.add_spacing('md')
        
        # Export/Import settings
        st.markdown("#### Settings Management")
        
        cols = self.layout.create_columns('third')
        
        with cols[0]:
            if st.button("📤 Export Settings", use_container_width=True):
                self._export_settings()
        
        with cols[1]:
            uploaded_file = st.file_uploader(
                "📥 Import Settings",
                type=['json'],
                key="import_settings"
            )
            
            if uploaded_file is not None:
                if st.button("Import", use_container_width=True):
                    self._import_settings(uploaded_file)
        
        with cols[2]:
            if st.button("🔄 Reset to Defaults", use_container_width=True):
                if st.session_state.get('confirm_reset', False):
                    self._reset_to_defaults()
                    st.success("Settings reset to defaults!")
                    st.session_state.confirm_reset = False
                    st.rerun()
                else:
                    st.session_state.confirm_reset = True
                    st.warning("Click again to confirm reset")
        
        # Update session state
        self._update_session_state('advanced', {
            'debug_mode': debug_mode,
            'enable_logging': enable_logging,
            'performance_monitoring': performance_monitoring,
            'memory_limit': memory_limit,
            'cpu_limit': cpu_limit
        })
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file or session state"""
        # First try to load from session state
        if 'dashboard_settings' in st.session_state:
            return st.session_state.dashboard_settings
        
        # Then try to load from file
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    st.session_state.dashboard_settings = settings
                    return settings
        except Exception as e:
            st.error(f"Error loading settings: {e}")
        
        # Return default settings
        default_settings = self._get_default_settings()
        st.session_state.dashboard_settings = default_settings
        return default_settings
    
    def _save_settings(self) -> None:
        """Save current settings to file"""
        try:
            # Collect all settings from session state
            all_settings = {}
            
            for category in ['general', 'display', 'notifications', 'data_sources', 'advanced']:
                if f'settings_{category}' in st.session_state:
                    all_settings.update(st.session_state[f'settings_{category}'])
            
            # Save to file
            with open(self.settings_file, 'w') as f:
                json.dump(all_settings, f, indent=2, default=str)
            
            # Update session state
            st.session_state.dashboard_settings = all_settings
            
        except Exception as e:
            st.error(f"Error saving settings: {e}")
    
    def _update_session_state(self, category: str, settings: Dict[str, Any]) -> None:
        """Update session state with new settings"""
        st.session_state[f'settings_{category}'] = settings
    
    def _get_option_index(self, options: List[str], value: str) -> int:
        """Get index of value in options list"""
        try:
            return options.index(value)
        except ValueError:
            return 0
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings"""
        return {
            # General
            'default_page': 'Dashboard',
            'refresh_interval': '5 minutes',
            'language': 'English',
            'timezone': 'Asia/Hong_Kong',
            'cache_duration': 10,
            'max_data_points': 200,
            
            # Display
            'theme': 'Light',
            'color_scheme': 'Default',
            'font_size': 'Medium',
            'sidebar_width': 'Medium',
            'compact_mode': False,
            'show_grid_lines': True,
            'enable_animations': True,
            'high_contrast': False,
            
            # Notifications
            'enable_notifications': True,
            'email_notifications': False,
            'sound_alerts': True,
            'system_alerts': True,
            'operational_alerts': True,
            'performance_alerts': False,
            'berth_utilization_threshold': 85,
            'vessel_queue_threshold': 5,
            'efficiency_threshold': 75,
            
            # Data Sources
            'primary_data_source': 'Simulation',
            'data_update_frequency': 'Every minute',
            'data_retention_days': 90,
            'enable_data_validation': True,
            
            # Advanced
            'debug_mode': False,
            'enable_logging': True,
            'performance_monitoring': False,
            'memory_limit': 1024,
            'cpu_limit': 80
        }
    
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
                with open(self.settings_file, 'w') as f:
                    json.dump(settings_data, f, indent=2, default=str)
                
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
            default_settings = self._get_default_settings()
            
            # Save default settings
            with open(self.settings_file, 'w') as f:
                json.dump(default_settings, f, indent=2, default=str)
            
            # Clear session state
            for key in list(st.session_state.keys()):
                if key.startswith('settings_') or key == 'dashboard_settings':
                    del st.session_state[key]
            
            # Set default settings in session state
            st.session_state.dashboard_settings = default_settings
            
        except Exception as e:
            st.error(f"Error resetting settings: {e}")

def create_settings_page(layout_manager: LayoutManager) -> SettingsPage:
    """Factory function to create settings page"""
    return SettingsPage(layout_manager)