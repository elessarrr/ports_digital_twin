import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from components.layout import LayoutManager
from styles.theme_manager import ThemeManager

class OperationsPage:
    """Operations page with vessel analytics, berth management, and live data"""
    
    def __init__(self, layout_manager: LayoutManager):
        self.layout = layout_manager
    
    def render(self, data: Dict[str, Any]) -> None:
        """Render the operations page"""
        # Apply custom CSS
        self.layout.apply_custom_css()
        
        # Page header
        self.layout.create_section_header(
            "Operations Center",
            "Real-time vessel tracking, berth management, and operational analytics",
            "🚢"
        )
        
        # Create tabs for different operational views
        tab_names = ["Vessel Analytics", "Berth Management", "Live Operations", "Port Layout"]
        tab_icons = ["🚢", "🏗️", "📡", "🗺️"]
        
        tabs = self.layout.create_tabs_container(tab_names, tab_icons)
        
        with tabs[0]:
            self._render_vessel_analytics(data)
        
        with tabs[1]:
            self._render_berth_management(data)
        
        with tabs[2]:
            self._render_live_operations(data)
        
        with tabs[3]:
            self._render_port_layout(data)
    
    def _render_vessel_analytics(self, data: Dict[str, Any]) -> None:
        """Render vessel analytics section"""
        self.layout.add_spacing('md')
        
        # Vessel summary metrics
        self._render_vessel_summary(data)
        self.layout.add_spacing('lg')
        
        # Vessel analytics charts
        cols = self.layout.create_columns('half')
        
        with cols[0]:
            self._render_vessel_types_chart(data)
        
        with cols[1]:
            self._render_vessel_timeline_chart(data)
        
        self.layout.add_spacing('lg')
        
        # Vessel details table
        self._render_vessel_details_table(data)
    
    def _render_vessel_summary(self, data: Dict[str, Any]) -> None:
        """Render vessel summary metrics"""
        st.markdown("### 🚢 Vessel Summary")
        
        vessel_data = data.get('vessel_analytics', {})
        
        metrics = [
            {
                'label': 'Total Vessels',
                'value': vessel_data.get('total_vessels', 45),
                'help': 'Total vessels currently in port area'
            },
            {
                'label': 'Arriving Today',
                'value': vessel_data.get('arriving_today', 8),
                'help': 'Vessels scheduled to arrive today'
            },
            {
                'label': 'Departing Today',
                'value': vessel_data.get('departing_today', 6),
                'help': 'Vessels scheduled to depart today'
            },
            {
                'label': 'Average Stay',
                'value': f"{vessel_data.get('avg_stay_hours', 18.5):.1f}h",
                'help': 'Average vessel stay duration'
            }
        ]
        
        self.layout.create_metric_grid(metrics, columns=4)
    
    def _render_vessel_types_chart(self, data: Dict[str, Any]) -> None:
        """Render vessel types distribution chart"""
        st.markdown("#### 📊 Vessel Types Distribution")
        
        vessel_types_data = data.get('vessel_types', self._get_fallback_vessel_types())
        
        # Create pie chart
        fig = px.pie(
            values=list(vessel_types_data.values()),
            names=list(vessel_types_data.keys()),
            title="Current Vessels by Type"
        )
        
        fig.update_layout(
            height=400,
            margin=dict(t=40, b=40, l=40, r=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_vessel_timeline_chart(self, data: Dict[str, Any]) -> None:
        """Render vessel arrival/departure timeline"""
        st.markdown("#### ⏰ Vessel Timeline (Next 24h)")
        
        timeline_data = data.get('vessel_timeline', self._get_fallback_timeline())
        
        if timeline_data:
            df = pd.DataFrame(timeline_data)
            
            # Create timeline chart
            fig = px.scatter(
                df,
                x='time',
                y='vessel_name',
                color='event_type',
                size='vessel_size',
                hover_data=['berth', 'cargo_type'],
                title="Vessel Schedule Timeline"
            )
            
            fig.update_layout(
                height=400,
                margin=dict(t=40, b=40, l=40, r=40),
                xaxis_title="Time",
                yaxis_title="Vessel"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No timeline data available")
    
    def _render_vessel_details_table(self, data: Dict[str, Any]) -> None:
        """Render detailed vessel information table"""
        st.markdown("### 📋 Vessel Details")
        
        vessel_details = data.get('vessel_details', self._get_fallback_vessel_details())
        
        if vessel_details:
            df = pd.DataFrame(vessel_details)
            
            # Add filters
            cols = st.columns(3)
            
            with cols[0]:
                status_filter = st.selectbox(
                    "Filter by Status",
                    options=['All'] + list(df['status'].unique()) if 'status' in df.columns else ['All'],
                    key="vessel_status_filter"
                )
            
            with cols[1]:
                type_filter = st.selectbox(
                    "Filter by Type",
                    options=['All'] + list(df['type'].unique()) if 'type' in df.columns else ['All'],
                    key="vessel_type_filter"
                )
            
            with cols[2]:
                berth_filter = st.selectbox(
                    "Filter by Berth",
                    options=['All'] + list(df['berth'].unique()) if 'berth' in df.columns else ['All'],
                    key="vessel_berth_filter"
                )
            
            # Apply filters
            filtered_df = df.copy()
            
            if status_filter != 'All' and 'status' in df.columns:
                filtered_df = filtered_df[filtered_df['status'] == status_filter]
            
            if type_filter != 'All' and 'type' in df.columns:
                filtered_df = filtered_df[filtered_df['type'] == type_filter]
            
            if berth_filter != 'All' and 'berth' in df.columns:
                filtered_df = filtered_df[filtered_df['berth'] == berth_filter]
            
            # Display table
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.info("No vessel details available")
    
    def _render_berth_management(self, data: Dict[str, Any]) -> None:
        """Render berth management section"""
        self.layout.add_spacing('md')
        
        # Berth utilization overview
        self._render_berth_utilization(data)
        self.layout.add_spacing('lg')
        
        # Berth details
        cols = self.layout.create_columns('half')
        
        with cols[0]:
            self._render_berth_status_chart(data)
        
        with cols[1]:
            self._render_berth_schedule(data)
    
    def _render_berth_utilization(self, data: Dict[str, Any]) -> None:
        """Render berth utilization metrics"""
        st.markdown("### 🏗️ Berth Utilization")
        
        berth_data = data.get('berth_data', {})
        
        total_berths = berth_data.get('total_berths', 35)
        occupied_berths = berth_data.get('occupied_berths', 28)
        utilization_rate = (occupied_berths / total_berths * 100) if total_berths > 0 else 0
        
        metrics = [
            {
                'label': 'Total Berths',
                'value': total_berths,
                'help': 'Total number of berths in the port'
            },
            {
                'label': 'Occupied Berths',
                'value': occupied_berths,
                'help': 'Number of berths currently occupied'
            },
            {
                'label': 'Available Berths',
                'value': total_berths - occupied_berths,
                'help': 'Number of berths currently available'
            },
            {
                'label': 'Utilization Rate',
                'value': f"{utilization_rate:.1f}%",
                'help': 'Percentage of berths currently in use'
            }
        ]
        
        self.layout.create_metric_grid(metrics, columns=4)
    
    def _render_berth_status_chart(self, data: Dict[str, Any]) -> None:
        """Render berth status visualization"""
        st.markdown("#### 📊 Berth Status Overview")
        
        berth_status_data = data.get('berth_status', self._get_fallback_berth_status())
        
        if berth_status_data:
            df = pd.DataFrame(berth_status_data)
            
            # Create status chart
            fig = px.bar(
                df,
                x='berth_id',
                y='utilization',
                color='status',
                title="Berth Utilization by Status",
                color_discrete_map={
                    'Occupied': '#ff6b6b',
                    'Available': '#51cf66',
                    'Maintenance': '#ffd43b'
                }
            )
            
            fig.update_layout(
                height=400,
                margin=dict(t=40, b=40, l=40, r=40),
                xaxis_title="Berth ID",
                yaxis_title="Utilization (%)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No berth status data available")
    
    def _render_berth_schedule(self, data: Dict[str, Any]) -> None:
        """Render berth schedule"""
        st.markdown("#### 📅 Berth Schedule")
        
        schedule_data = data.get('berth_schedule', self._get_fallback_berth_schedule())
        
        if schedule_data:
            df = pd.DataFrame(schedule_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No schedule data available")
    
    def _render_live_operations(self, data: Dict[str, Any]) -> None:
        """Render live operations section"""
        self.layout.add_spacing('md')
        
        # Real-time status indicators
        self._render_live_status(data)
        self.layout.add_spacing('lg')
        
        # Live data feeds
        cols = self.layout.create_columns('half')
        
        with cols[0]:
            self._render_live_vessel_movements(data)
        
        with cols[1]:
            self._render_live_cargo_operations(data)
    
    def _render_live_status(self, data: Dict[str, Any]) -> None:
        """Render live status indicators"""
        st.markdown("### 📡 Live Operations Status")
        
        # Status indicators
        cols = self.layout.create_columns('quarter')
        
        with cols[0]:
            st.markdown("#### 🚢 Vessel Traffic")
            st.markdown("🟢 **Normal** - 3 movements/hour")
        
        with cols[1]:
            st.markdown("#### 🏗️ Cargo Operations")
            st.markdown("🟡 **Busy** - 85% capacity")
        
        with cols[2]:
            st.markdown("#### 🌊 Weather Conditions")
            st.markdown("🟢 **Good** - Clear skies")
        
        with cols[3]:
            st.markdown("#### ⚡ System Status")
            st.markdown("🟢 **Online** - All systems operational")
    
    def _render_live_vessel_movements(self, data: Dict[str, Any]) -> None:
        """Render live vessel movements feed"""
        st.markdown("#### 🚢 Live Vessel Movements")
        
        movements = data.get('live_movements', self._get_fallback_live_movements())
        
        for movement in movements:
            timestamp = movement.get('timestamp', 'Unknown')
            vessel = movement.get('vessel', 'Unknown vessel')
            action = movement.get('action', 'Unknown action')
            location = movement.get('location', 'Unknown location')
            
            st.markdown(f"**{timestamp}** - {vessel}")
            st.markdown(f"   {action} at {location}")
            st.markdown("---")
    
    def _render_live_cargo_operations(self, data: Dict[str, Any]) -> None:
        """Render live cargo operations feed"""
        st.markdown("#### 📦 Live Cargo Operations")
        
        operations = data.get('live_operations', self._get_fallback_live_operations())
        
        for operation in operations:
            timestamp = operation.get('timestamp', 'Unknown')
            operation_type = operation.get('type', 'Unknown operation')
            quantity = operation.get('quantity', 'Unknown quantity')
            location = operation.get('location', 'Unknown location')
            
            st.markdown(f"**{timestamp}** - {operation_type}")
            st.markdown(f"   {quantity} at {location}")
            st.markdown("---")
    
    def _render_port_layout(self, data: Dict[str, Any]) -> None:
        """Render port layout visualization"""
        self.layout.add_spacing('md')
        
        st.markdown("### 🗺️ Port Layout")
        
        # Port layout visualization placeholder
        self.layout.create_info_box(
            "Interactive port layout visualization will be implemented here. This will show real-time berth status, vessel positions, and cargo areas.",
            'info',
            '🗺️'
        )
        
        # Placeholder for port layout
        st.markdown("#### 🏗️ Terminal Layout")
        st.markdown("*Interactive port map coming soon...*")
    
    # Fallback data methods
    def _get_fallback_vessel_types(self) -> Dict[str, int]:
        return {
            'Container Ship': 18,
            'Bulk Carrier': 12,
            'Tanker': 8,
            'General Cargo': 5,
            'RoRo': 2
        }
    
    def _get_fallback_timeline(self) -> List[Dict[str, Any]]:
        base_time = datetime.now()
        return [
            {
                'time': base_time + timedelta(hours=1),
                'vessel_name': 'MSC Bellissima',
                'event_type': 'Arrival',
                'vessel_size': 20,
                'berth': 'B12',
                'cargo_type': 'Container'
            },
            {
                'time': base_time + timedelta(hours=3),
                'vessel_name': 'COSCO Shanghai',
                'event_type': 'Departure',
                'vessel_size': 15,
                'berth': 'B8',
                'cargo_type': 'Container'
            }
        ]
    
    def _get_fallback_vessel_details(self) -> List[Dict[str, Any]]:
        return [
            {
                'vessel_name': 'MSC Bellissima',
                'type': 'Container Ship',
                'status': 'Berthed',
                'berth': 'B12',
                'arrival': '2024-01-15 08:30',
                'departure': '2024-01-16 14:00',
                'cargo': '2,400 TEU'
            },
            {
                'vessel_name': 'COSCO Shanghai',
                'type': 'Container Ship',
                'status': 'Loading',
                'berth': 'B8',
                'arrival': '2024-01-14 16:45',
                'departure': '2024-01-15 22:30',
                'cargo': '1,800 TEU'
            }
        ]
    
    def _get_fallback_berth_status(self) -> List[Dict[str, Any]]:
        return [
            {'berth_id': 'B1', 'status': 'Occupied', 'utilization': 100},
            {'berth_id': 'B2', 'status': 'Available', 'utilization': 0},
            {'berth_id': 'B3', 'status': 'Occupied', 'utilization': 85},
            {'berth_id': 'B4', 'status': 'Maintenance', 'utilization': 0}
        ]
    
    def _get_fallback_berth_schedule(self) -> List[Dict[str, Any]]:
        return [
            {
                'berth': 'B12',
                'vessel': 'MSC Bellissima',
                'arrival': '08:30',
                'departure': '14:00',
                'status': 'Confirmed'
            },
            {
                'berth': 'B8',
                'vessel': 'COSCO Shanghai',
                'arrival': '16:45',
                'departure': '22:30',
                'status': 'In Progress'
            }
        ]
    
    def _get_fallback_live_movements(self) -> List[Dict[str, Any]]:
        return [
            {
                'timestamp': '14:35',
                'vessel': 'Ever Given',
                'action': 'Approaching',
                'location': 'Pilot Station'
            },
            {
                'timestamp': '14:20',
                'vessel': 'MSC Bellissima',
                'action': 'Berthed',
                'location': 'Terminal 3, Berth 12'
            }
        ]
    
    def _get_fallback_live_operations(self) -> List[Dict[str, Any]]:
        return [
            {
                'timestamp': '14:40',
                'type': 'Container Loading',
                'quantity': '120 TEU',
                'location': 'Terminal 2'
            },
            {
                'timestamp': '14:25',
                'type': 'Bulk Discharge',
                'quantity': '500 tons',
                'location': 'Terminal 1'
            }
        ]

def create_operations_page(layout_manager: LayoutManager) -> OperationsPage:
    """Factory function to create operations page"""
    return OperationsPage(layout_manager)