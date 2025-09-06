# hk_port_digital_twin/src/dashboard/styles/themes.py

def get_light_theme():
    """
    Returns the light theme configuration for the dashboard.
    """
    return {
        "theme": {
            "primaryColor": "#1c83e1",
            "backgroundColor": "#ffffff",
            "secondaryBackgroundColor": "#f0f2f6",
            "textColor": "#262730",
            "font": "sans serif"
        }
    }

def get_dark_theme():
    """
    Returns the dark theme configuration for the dashboard.
    """
    return {
        "theme": {
            "primaryColor": "#1c83e1",
            "backgroundColor": "#0e1117",
            "secondaryBackgroundColor": "#262730",
            "textColor": "#fafafa",
            "font": "sans serif"
        }
    }