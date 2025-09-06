import json
import os
from typing import Dict, Any

class UserPreferences:
    """Manages user preferences and settings."""

    def __init__(self, settings_file: str = "user_settings.json"):
        self.settings_file = settings_file

    def load_settings(self) -> Dict[str, Any]:
        """Load user settings from a JSON file."""
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        return self.get_default_settings()

    def save_settings(self, settings: Dict[str, Any]) -> None:
        """Save user settings to a JSON file."""
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=4)

    def get_default_settings(self) -> Dict[str, Any]:
        """Get the default dashboard settings."""
        return {
            "settings_general": {
                "default_page": "Dashboard",
                "refresh_interval": "5 minutes",
                "language": "English",
                "timezone": "Asia/Hong_Kong",
                "cache_duration": 10,
                "max_data_points": 200
            },
            "settings_display": {
                "theme": "Light",
                "color_scheme": "Default",
                "font_size": "Medium",
                "sidebar_width": "Medium",
                "compact_mode": False,
                "show_grid_lines": True,
                "enable_animations": True,
                "high_contrast": False
            },
            "settings_notifications": {
                "enable_notifications": True,
                "email_notifications": False,
                "slack_notifications": False,
                "alert_threshold_critical": 95,
                "alert_threshold_warning": 85
            },
            "settings_data_sources": {
                "data_source": "Sample",
                "uploaded_file": None
            },
            "settings_advanced": {
                "debug_mode": False,
                "show_performance_metrics": False,
                "enable_ai_forecasts": True,
                "enable_simulation_scenarios": False
            }
        }