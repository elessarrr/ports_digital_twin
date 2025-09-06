import streamlit as st
from typing import Dict, Any, Optional
import json

class ThemeManager:
    """Manages themes and styling for the dashboard"""
    
    def __init__(self):
        self.themes = self._get_available_themes()
        self.current_theme = self._load_current_theme()
    
    def apply_theme(self, theme_name: Optional[str] = None) -> None:
        """Apply the specified theme or current theme"""
        if theme_name:
            self.current_theme = theme_name
        
        theme_config = self.themes.get(self.current_theme, self.themes['light'])
        
        # Apply CSS styling
        css = self._generate_theme_css(theme_config)
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        
        # Store theme in session state
        st.session_state.current_theme = self.current_theme
    
    def get_theme_colors(self, theme_name: Optional[str] = None) -> Dict[str, str]:
        """Get color palette for the specified theme"""
        theme_name = theme_name or self.current_theme
        return self.themes.get(theme_name, self.themes['light'])['colors']
    
    def get_chart_colors(self, theme_name: Optional[str] = None) -> list:
        """Get chart color palette for the specified theme"""
        theme_name = theme_name or self.current_theme
        return self.themes.get(theme_name, self.themes['light'])['chart_colors']
    
    def _load_current_theme(self) -> str:
        """Load current theme from session state or settings"""
        # Check session state first
        if 'current_theme' in st.session_state:
            return st.session_state.current_theme
        
        # Check settings
        if 'dashboard_settings' in st.session_state:
            settings = st.session_state.dashboard_settings
            theme_mapping = {
                'Light': 'light',
                'Dark': 'dark',
                'Auto': 'auto'
            }
            return theme_mapping.get(settings.get('theme', 'Light'), 'light')
        
        return 'light'
    
    def _get_available_themes(self) -> Dict[str, Dict[str, Any]]:
        """Get all available themes"""
        return {
            'light': {
                'name': 'Light Theme',
                'colors': {
                    'primary': '#1f77b4',
                    'secondary': '#ff7f0e',
                    'success': '#2ca02c',
                    'warning': '#ff7f0e',
                    'error': '#d62728',
                    'info': '#17a2b8',
                    'background': '#ffffff',
                    'surface': '#f8f9fa',
                    'text_primary': '#212529',
                    'text_secondary': '#6c757d',
                    'border': '#dee2e6',
                    'accent': '#e9ecef'
                },
                'chart_colors': [
                    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
                ],
                'fonts': {
                    'primary': 'Inter, sans-serif',
                    'secondary': 'Roboto, sans-serif',
                    'monospace': 'Fira Code, monospace'
                }
            },
            'dark': {
                'name': 'Dark Theme',
                'colors': {
                    'primary': '#4dabf7',
                    'secondary': '#ffd43b',
                    'success': '#51cf66',
                    'warning': '#ffd43b',
                    'error': '#ff6b6b',
                    'info': '#74c0fc',
                    'background': '#1a1a1a',
                    'surface': '#2d2d2d',
                    'text_primary': '#ffffff',
                    'text_secondary': '#adb5bd',
                    'border': '#495057',
                    'accent': '#343a40'
                },
                'chart_colors': [
                    '#4dabf7', '#ffd43b', '#51cf66', '#ff6b6b', '#da77f2',
                    '#fd7e14', '#f783ac', '#868e96', '#fab005', '#22b8cf'
                ],
                'fonts': {
                    'primary': 'Inter, sans-serif',
                    'secondary': 'Roboto, sans-serif',
                    'monospace': 'Fira Code, monospace'
                }
            },
            'blue': {
                'name': 'Blue Theme',
                'colors': {
                    'primary': '#0066cc',
                    'secondary': '#4da6ff',
                    'success': '#28a745',
                    'warning': '#ffc107',
                    'error': '#dc3545',
                    'info': '#17a2b8',
                    'background': '#f8fbff',
                    'surface': '#e3f2fd',
                    'text_primary': '#1a365d',
                    'text_secondary': '#4a5568',
                    'border': '#bee3f8',
                    'accent': '#ebf8ff'
                },
                'chart_colors': [
                    '#0066cc', '#4da6ff', '#0080ff', '#3399ff', '#66b3ff',
                    '#99ccff', '#0052a3', '#004080', '#002d5c', '#001a39'
                ],
                'fonts': {
                    'primary': 'Inter, sans-serif',
                    'secondary': 'Roboto, sans-serif',
                    'monospace': 'Fira Code, monospace'
                }
            },
            'green': {
                'name': 'Green Theme',
                'colors': {
                    'primary': '#059669',
                    'secondary': '#34d399',
                    'success': '#10b981',
                    'warning': '#f59e0b',
                    'error': '#ef4444',
                    'info': '#06b6d4',
                    'background': '#f0fdf4',
                    'surface': '#dcfce7',
                    'text_primary': '#064e3b',
                    'text_secondary': '#374151',
                    'border': '#bbf7d0',
                    'accent': '#ecfdf5'
                },
                'chart_colors': [
                    '#059669', '#34d399', '#10b981', '#6ee7b7', '#a7f3d0',
                    '#d1fae5', '#047857', '#065f46', '#064e3b', '#022c22'
                ],
                'fonts': {
                    'primary': 'Inter, sans-serif',
                    'secondary': 'Roboto, sans-serif',
                    'monospace': 'Fira Code, monospace'
                }
            },
            'purple': {
                'name': 'Purple Theme',
                'colors': {
                    'primary': '#7c3aed',
                    'secondary': '#a78bfa',
                    'success': '#10b981',
                    'warning': '#f59e0b',
                    'error': '#ef4444',
                    'info': '#06b6d4',
                    'background': '#faf5ff',
                    'surface': '#f3e8ff',
                    'text_primary': '#581c87',
                    'text_secondary': '#374151',
                    'border': '#c4b5fd',
                    'accent': '#f5f3ff'
                },
                'chart_colors': [
                    '#7c3aed', '#a78bfa', '#8b5cf6', '#c4b5fd', '#ddd6fe',
                    '#ede9fe', '#6d28d9', '#5b21b6', '#4c1d95', '#3c1361'
                ],
                'fonts': {
                    'primary': 'Inter, sans-serif',
                    'secondary': 'Roboto, sans-serif',
                    'monospace': 'Fira Code, monospace'
                }
            },
            'orange': {
                'name': 'Orange Theme',
                'colors': {
                    'primary': '#ea580c',
                    'secondary': '#fb923c',
                    'success': '#10b981',
                    'warning': '#f59e0b',
                    'error': '#ef4444',
                    'info': '#06b6d4',
                    'background': '#fff7ed',
                    'surface': '#fed7aa',
                    'text_primary': '#9a3412',
                    'text_secondary': '#374151',
                    'border': '#fdba74',
                    'accent': '#ffedd5'
                },
                'chart_colors': [
                    '#ea580c', '#fb923c', '#f97316', '#fdba74', '#fed7aa',
                    '#ffedd5', '#dc2626', '#c2410c', '#9a3412', '#7c2d12'
                ],
                'fonts': {
                    'primary': 'Inter, sans-serif',
                    'secondary': 'Roboto, sans-serif',
                    'monospace': 'Fira Code, monospace'
                }
            }
        }
    
    def _generate_theme_css(self, theme_config: Dict[str, Any]) -> str:
        """Generate CSS for the theme"""
        colors = theme_config['colors']
        fonts = theme_config['fonts']
        
        css = f"""
        /* Theme Variables */
        :root {{
            --primary-color: {colors['primary']};
            --secondary-color: {colors['secondary']};
            --success-color: {colors['success']};
            --warning-color: {colors['warning']};
            --error-color: {colors['error']};
            --info-color: {colors['info']};
            --background-color: {colors['background']};
            --surface-color: {colors['surface']};
            --text-primary: {colors['text_primary']};
            --text-secondary: {colors['text_secondary']};
            --border-color: {colors['border']};
            --accent-color: {colors['accent']};
            --font-primary: {fonts['primary']};
            --font-secondary: {fonts['secondary']};
            --font-monospace: {fonts['monospace']};
        }}
        
        /* Global Styles */
        .main .block-container {{
            background-color: var(--background-color);
            color: var(--text-primary);
            font-family: var(--font-primary);
        }}
        
        /* Sidebar Styles */
        .css-1d391kg {{
            background-color: var(--surface-color);
            border-right: 1px solid var(--border-color);
        }}
        
        /* Card Styles */
        .dashboard-card {{
            background-color: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .dashboard-card h3 {{
            color: var(--primary-color);
            margin-bottom: 0.5rem;
            font-weight: 600;
        }}
        
        /* Metric Styles */
        .metric-container {{
            background-color: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 1rem;
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 2rem;
            font-weight: bold;
            color: var(--primary-color);
            margin-bottom: 0.25rem;
        }}
        
        .metric-label {{
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
        }}
        
        .metric-delta {{
            font-size: 0.75rem;
            font-weight: 500;
        }}
        
        .metric-delta.positive {{
            color: var(--success-color);
        }}
        
        .metric-delta.negative {{
            color: var(--error-color);
        }}
        
        /* Button Styles */
        .stButton > button {{
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        
        .stButton > button:hover {{
            background-color: var(--secondary-color);
            transform: translateY(-1px);
        }}
        
        /* Tab Styles */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background-color: var(--surface-color);
            border-radius: 8px;
            padding: 4px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: transparent;
            border-radius: 6px;
            color: var(--text-secondary);
            font-weight: 500;
            padding: 8px 16px;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: var(--primary-color) !important;
            color: white !important;
        }}
        
        /* Alert Styles */
        .alert {{
            border-radius: 6px;
            padding: 1rem;
            margin-bottom: 1rem;
            border-left: 4px solid;
        }}
        
        .alert-success {{
            background-color: rgba(16, 185, 129, 0.1);
            border-left-color: var(--success-color);
            color: var(--success-color);
        }}
        
        .alert-warning {{
            background-color: rgba(245, 158, 11, 0.1);
            border-left-color: var(--warning-color);
            color: var(--warning-color);
        }}
        
        .alert-error {{
            background-color: rgba(239, 68, 68, 0.1);
            border-left-color: var(--error-color);
            color: var(--error-color);
        }}
        
        .alert-info {{
            background-color: rgba(6, 182, 212, 0.1);
            border-left-color: var(--info-color);
            color: var(--info-color);
        }}
        
        /* Chart Container */
        .chart-container {{
            background-color: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        }}
        
        /* Status Indicator */
        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        
        .status-online {{
            background-color: var(--success-color);
        }}
        
        .status-warning {{
            background-color: var(--warning-color);
        }}
        
        .status-offline {{
            background-color: var(--error-color);
        }}
        
        /* Progress Bar */
        .progress-bar {{
            background-color: var(--accent-color);
            border-radius: 4px;
            overflow: hidden;
            height: 8px;
        }}
        
        .progress-fill {{
            background-color: var(--primary-color);
            height: 100%;
            transition: width 0.3s ease;
        }}
        
        /* Navigation */
        .nav-item {{
            padding: 0.5rem 1rem;
            border-radius: 6px;
            margin-bottom: 0.25rem;
            cursor: pointer;
            transition: all 0.2s ease;
            color: var(--text-secondary);
        }}
        
        .nav-item:hover {{
            background-color: var(--accent-color);
            color: var(--text-primary);
        }}
        
        .nav-item.active {{
            background-color: var(--primary-color);
            color: white;
        }}
        
        /* Section Header */
        .section-header {{
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 0.5rem;
            margin-bottom: 1.5rem;
        }}
        
        .section-header h1 {{
            color: var(--primary-color);
            margin: 0;
            font-weight: 700;
        }}
        
        .section-header p {{
            color: var(--text-secondary);
            margin: 0.25rem 0 0 0;
            font-size: 1rem;
        }}
        
        /* Data Table */
        .dataframe {{
            background-color: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: 6px;
        }}
        
        .dataframe th {{
            background-color: var(--accent-color);
            color: var(--text-primary);
            font-weight: 600;
        }}
        
        .dataframe td {{
            color: var(--text-primary);
        }}
        
        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: var(--accent-color);
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--border-color);
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--text-secondary);
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .dashboard-card {{
                margin-bottom: 0.5rem;
                padding: 0.75rem;
            }}
            
            .metric-value {{
                font-size: 1.5rem;
            }}
            
            .section-header h1 {{
                font-size: 1.5rem;
            }}
        }}
        
        /* Animation Classes */
        .fade-in {{
            animation: fadeIn 0.3s ease-in;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .slide-in {{
            animation: slideIn 0.3s ease-out;
        }}
        
        @keyframes slideIn {{
            from {{ transform: translateX(-20px); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        
        /* Utility Classes */
        .text-center {{ text-align: center; }}
        .text-left {{ text-align: left; }}
        .text-right {{ text-align: right; }}
        
        .mb-1 {{ margin-bottom: 0.25rem; }}
        .mb-2 {{ margin-bottom: 0.5rem; }}
        .mb-3 {{ margin-bottom: 1rem; }}
        .mb-4 {{ margin-bottom: 1.5rem; }}
        .mb-5 {{ margin-bottom: 2rem; }}
        
        .mt-1 {{ margin-top: 0.25rem; }}
        .mt-2 {{ margin-top: 0.5rem; }}
        .mt-3 {{ margin-top: 1rem; }}
        .mt-4 {{ margin-top: 1.5rem; }}
        .mt-5 {{ margin-top: 2rem; }}
        
        .p-1 {{ padding: 0.25rem; }}
        .p-2 {{ padding: 0.5rem; }}
        .p-3 {{ padding: 1rem; }}
        .p-4 {{ padding: 1.5rem; }}
        .p-5 {{ padding: 2rem; }}
        """
        
        return css
    
    def get_plotly_theme(self, theme_name: Optional[str] = None) -> Dict[str, Any]:
        """Get Plotly theme configuration"""
        theme_name = theme_name or self.current_theme
        colors = self.get_theme_colors(theme_name)
        
        if theme_name == 'dark':
            return {
                'layout': {
                    'paper_bgcolor': colors['background'],
                    'plot_bgcolor': colors['surface'],
                    'font': {'color': colors['text_primary']},
                    'colorway': self.get_chart_colors(theme_name),
                    'xaxis': {
                        'gridcolor': colors['border'],
                        'linecolor': colors['border'],
                        'tickcolor': colors['text_secondary']
                    },
                    'yaxis': {
                        'gridcolor': colors['border'],
                        'linecolor': colors['border'],
                        'tickcolor': colors['text_secondary']
                    }
                }
            }
        else:
            return {
                'layout': {
                    'paper_bgcolor': colors['background'],
                    'plot_bgcolor': colors['surface'],
                    'font': {'color': colors['text_primary']},
                    'colorway': self.get_chart_colors(theme_name),
                    'xaxis': {
                        'gridcolor': colors['border'],
                        'linecolor': colors['border']
                    },
                    'yaxis': {
                        'gridcolor': colors['border'],
                        'linecolor': colors['border']
                    }
                }
            }
    
    def create_status_indicator(self, status: str, label: str = "") -> str:
        """Create a status indicator HTML"""
        status_class = f"status-{status.lower()}"
        return f'<span class="status-indicator {status_class}"></span>{label}'
    
    def create_progress_bar(self, value: float, max_value: float = 100) -> str:
        """Create a progress bar HTML"""
        percentage = min((value / max_value) * 100, 100)
        return f'''
        <div class="progress-bar">
            <div class="progress-fill" style="width: {percentage}%"></div>
        </div>
        '''
    
    def get_available_theme_names(self) -> list:
        """Get list of available theme names"""
        return list(self.themes.keys())
    
    def get_current_theme(self) -> str:
        """Get the current theme name"""
        return self.current_theme
    
    def get_available_themes(self) -> list:
        """Get list of available theme names (alias for compatibility)"""
        return self.get_available_theme_names()
    
    def set_theme(self, theme_name: str) -> None:
        """Set the current theme"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            st.session_state.current_theme = theme_name
            # Apply the theme immediately
            self.apply_theme(theme_name)
    
    def get_theme_info(self, theme_name: str) -> Dict[str, Any]:
        """Get theme information"""
        return self.themes.get(theme_name, {})

def create_theme_manager() -> ThemeManager:
    """Factory function to create theme manager"""
    return ThemeManager()