import streamlit as st
from typing import Dict, List, Optional

class NavigationFramework:
    """Navigation framework for the Hong Kong Port Digital Twin Dashboard"""
    
    def __init__(self):
        self.sections = {
            "monitoring": {
                "icon": "🏠",
                "title": "Main App",
                "description": "Overview + Key Metrics"
            },
            "analytics": {
                "icon": "📊",
                "title": "Analytics",
                "description": "Performance metrics and data analysis"
            },
            "operations": {
                "icon": "🚢",
                "title": "Operations",
                "description": "Ships, berths, and operational monitoring"
            },
            "scenarios": {
                "icon": "🔬",
                "title": "Scenarios",
                "description": "Simulation and scenario planning"
            },
            "settings": {
                "icon": "⚙️",
                "title": "Settings",
                "description": "Configuration and preferences"
            }
        }
    
    def render_sidebar_navigation(self) -> str:
        """Render navigation in sidebar and return selected section"""

        
        # Initialize session state for current section
        if 'current_section' not in st.session_state:
            st.session_state.current_section = list(self.sections.keys())[0]
        
        # Create navigation buttons
        with st.sidebar:
            st.markdown("### 📍 Navigation")
            
            for section_key, section_config in self.sections.items():
                icon = section_config.get('icon', '📄')
                title = section_config.get('title', section_key.title())
                
                if st.button(
                    f"{icon} {title}",
                    key=f"nav_{section_key}",
                    use_container_width=True
                ):
                    st.session_state.current_section = section_key
                    st.rerun()
            
            # Show current section indicator
            current_config = self.sections[st.session_state.current_section]
            current_icon = current_config.get('icon', '📄')
            current_title = current_config.get('title', st.session_state.current_section.title())
            st.markdown(f"**Current:** {current_icon} {current_title}")
            
            # Show description if available
            description = current_config.get('description')
            if description:
                st.markdown(f"*{description}*")
        

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