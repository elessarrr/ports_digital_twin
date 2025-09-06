import streamlit as st
from typing import Dict, List, Optional

class NavigationFramework:
    """Navigation framework for the Hong Kong Port Digital Twin Dashboard"""
    
    def __init__(self):
        self.sections = {
            "dashboard": {
                "icon": "🏠",
                "title": "Dashboard",
                "description": "Overview + Key Metrics"
            },
            "operations": {
                "icon": "🚢",
                "title": "Operations",
                "description": "Vessels + Berths + Live Data"
            },
            "analytics": {
                "icon": "📊",
                "title": "Analytics",
                "description": "Cargo Statistics + Performance"
            },
            "scenarios": {
                "icon": "🎯",
                "title": "Scenarios",
                "description": "Simulation Controls"
            },
            "settings": {
                "icon": "⚙️",
                "title": "Settings",
                "description": "Configuration + Preferences"
            }
        }
    
    def render_sidebar_navigation(self) -> str:
        """Render the sidebar navigation and return selected section"""
        st.sidebar.markdown("## 🏗️ Navigation")
        
        # Initialize session state for navigation
        if 'current_section' not in st.session_state:
            st.session_state.current_section = 'dashboard'
        
        selected_section = None
        
        # Create navigation buttons
        for section_key, section_info in self.sections.items():
            # Create button with icon and title
            button_label = f"{section_info['icon']} {section_info['title']}"
            
            # Check if this is the current section
            is_current = st.session_state.current_section == section_key
            
            # Create button with different styling for current section
            if st.sidebar.button(
                button_label,
                key=f"nav_{section_key}",
                help=section_info['description'],
                use_container_width=True
            ):
                st.session_state.current_section = section_key
                selected_section = section_key
                st.rerun()
        
        # Show current section indicator
        current_info = self.sections[st.session_state.current_section]
        st.sidebar.markdown(f"**Current:** {current_info['icon']} {current_info['title']}")
        st.sidebar.markdown(f"*{current_info['description']}*")
        
        return st.session_state.current_section
    
    def render_breadcrumb(self, current_section: str, subsection: Optional[str] = None) -> None:
        """Render breadcrumb navigation"""
        section_info = self.sections.get(current_section, {})
        
        breadcrumb_parts = ["🏗️ HK Port Digital Twin"]
        
        if section_info:
            breadcrumb_parts.append(f"{section_info['icon']} {section_info['title']}")
        
        if subsection:
            breadcrumb_parts.append(subsection)
        
        breadcrumb = " > ".join(breadcrumb_parts)
        st.markdown(f"**{breadcrumb}**")
    
    def get_section_config(self, section: str) -> Dict:
        """Get configuration for a specific section"""
        return self.sections.get(section, {})
    
    def render_quick_actions(self) -> None:
        """Render quick action buttons in sidebar"""
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ⚡ Quick Actions")
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("🔄 Refresh", key="quick_refresh", use_container_width=True):
                # Clear cache and refresh data
                st.cache_data.clear()
                st.rerun()
        
        with col2:
            if st.button("📊 Status", key="quick_status", use_container_width=True):
                st.session_state.current_section = 'dashboard'
                st.rerun()
    
    def render_system_status(self) -> None:
        """Render system status indicators in sidebar"""
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔍 System Status")
        
        # Data connection status
        st.sidebar.markdown("📡 **Data Connection:** 🟢 Online")
        
        # Last update time
        from datetime import datetime
        last_update = datetime.now().strftime("%H:%M:%S")
        st.sidebar.markdown(f"🕒 **Last Update:** {last_update}")
        
        # Active scenarios
        if hasattr(st.session_state, 'scenario_manager'):
            current_scenario = st.session_state.scenario_manager.get_current_scenario()
            st.sidebar.markdown(f"🎯 **Scenario:** {current_scenario}")

def create_navigation() -> NavigationFramework:
    """Factory function to create navigation framework"""
    return NavigationFramework()