import streamlit as st
from typing import List, Optional, Union

class LayoutManager:
    """Layout manager for consistent spacing and grid system"""
    
    # Standard spacing increments (in pixels)
    SPACING = {
        'xs': 8,
        'sm': 16,
        'md': 24,
        'lg': 32,
        'xl': 48
    }
    
    # Standard column ratios for 12-column grid
    GRID_RATIOS = {
        'full': [1],
        'half': [1, 1],
        'third': [1, 1, 1],
        'quarter': [1, 1, 1, 1],
        'sidebar_main': [0.3, 0.7],
        'main_sidebar': [0.7, 0.3],
        'centered': [0.1, 0.8, 0.1],
        'wide_centered': [0.05, 0.9, 0.05]
    }
    
    @staticmethod
    def add_spacing(size: str = 'md') -> None:
        """Add vertical spacing"""
        spacing_px = LayoutManager.SPACING.get(size, 24)
        st.markdown(f'<div style="margin-top: {spacing_px}px;"></div>', unsafe_allow_html=True)
    
    @staticmethod
    def create_columns(layout: Union[str, List[float]], gap: str = 'md') -> List:
        """Create columns with standardized spacing"""
        if isinstance(layout, str):
            ratios = LayoutManager.GRID_RATIOS.get(layout, [1])
        else:
            ratios = layout
        
        gap_size = LayoutManager.SPACING.get(gap, 24)
        
        # Create columns with gap
        columns = st.columns(ratios, gap=gap_size)
        return columns
    
    @staticmethod
    def create_card(title: Optional[str] = None, 
                   subtitle: Optional[str] = None,
                   border: bool = True,
                   padding: str = 'md') -> None:
        """Create a card container with consistent styling"""
        padding_px = LayoutManager.SPACING.get(padding, 24)
        
        # Card styling
        border_style = "border: 1px solid #e0e0e0; border-radius: 8px;" if border else ""
        
        card_style = f"""
        <div style="
            {border_style}
            padding: {padding_px}px;
            margin: 8px 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
        """
        
        st.markdown(card_style, unsafe_allow_html=True)
        
        if title:
            st.markdown(f"### {title}")
        
        if subtitle:
            st.markdown(f"*{subtitle}*")
    
    @staticmethod
    def close_card() -> None:
        """Close card container"""
        st.markdown("</div>", unsafe_allow_html=True)
    
    @staticmethod
    def create_metric_grid(metrics: List[dict], columns: int = 4) -> None:
        """Create a grid of metrics with consistent styling"""
        # Calculate number of rows needed
        rows = (len(metrics) + columns - 1) // columns
        
        for row in range(rows):
            cols = st.columns(columns)
            
            for col_idx in range(columns):
                metric_idx = row * columns + col_idx
                
                if metric_idx < len(metrics):
                    metric = metrics[metric_idx]
                    
                    with cols[col_idx]:
                        st.metric(
                            label=metric.get('label', ''),
                            value=metric.get('value', ''),
                            delta=metric.get('delta', None),
                            help=metric.get('help', None)
                        )
    
    @staticmethod
    def create_section_header(title: str, 
                            subtitle: Optional[str] = None,
                            icon: Optional[str] = None) -> None:
        """Create a standardized section header"""
        header_title = f"{icon} {title}" if icon else title
        
        st.markdown(f"## {header_title}")
        
        if subtitle:
            st.markdown(f"*{subtitle}*")
        
        # Add separator line
        st.markdown("---")
    
    @staticmethod
    def create_info_box(message: str, 
                       box_type: str = 'info',
                       icon: Optional[str] = None) -> None:
        """Create an information box with consistent styling"""
        
        type_configs = {
            'info': {'color': '#e3f2fd', 'border': '#2196f3', 'text': '#1976d2'},
            'warning': {'color': '#fff3e0', 'border': '#ff9800', 'text': '#f57c00'},
            'error': {'color': '#ffebee', 'border': '#f44336', 'text': '#d32f2f'},
            'success': {'color': '#e8f5e8', 'border': '#4caf50', 'text': '#388e3c'}
        }
        
        config = type_configs.get(box_type, type_configs['info'])
        
        display_message = f"{icon} {message}" if icon else message
        
        st.markdown(f"""
        <div style="
            background-color: {config['color']};
            border-left: 4px solid {config['border']};
            padding: 16px;
            margin: 8px 0;
            border-radius: 4px;
            color: {config['text']};
        ">
            {display_message}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def create_tabs_container(tab_names: List[str], 
                            tab_icons: Optional[List[str]] = None) -> List:
        """Create tabs with consistent styling"""
        if tab_icons and len(tab_icons) == len(tab_names):
            tab_labels = [f"{icon} {name}" for icon, name in zip(tab_icons, tab_names)]
        else:
            tab_labels = tab_names
        
        return st.tabs(tab_labels)
    
    @staticmethod
    def apply_custom_css() -> None:
        """Apply custom CSS for consistent styling"""
        st.markdown("""
        <style>
        /* Main container styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Metric styling */
        [data-testid="metric-container"] {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 6px;
            border: 1px solid #e0e0e0;
            transition: all 0.2s;
        }
        
        .stButton > button:hover {
            border-color: #2196f3;
            box-shadow: 0 2px 8px rgba(33, 150, 243, 0.2);
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 6px 6px 0 0;
            padding: 12px 24px;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            padding-top: 2rem;
        }
        
        /* Chart container styling */
        .js-plotly-plot {
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)

def create_layout_manager() -> LayoutManager:
    """Factory function to create layout manager"""
    return LayoutManager()