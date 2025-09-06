import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from components.layout import LayoutManager
from styles.theme_manager import ThemeManager

class DashboardPage:
    """Main dashboard page with overview and key metrics"""
    
    def __init__(self, layout_manager: LayoutManager):
        self.layout = layout_manager
    
    def render(self, data: Dict[str, Any]) -> None:
        """Render the main dashboard page"""
        # Apply custom CSS
        self.layout.apply_custom_css()
        
        # Page header
        self.layout.create_section_header(
            "Dashboard Overview",
            "Real-time insights and key performance indicators",
            "🏠"
        )
        
        # Render main sections
        self._render_kpi_summary(data)
        self.layout.add_spacing('lg')
        
        self._render_operational_status(data)
        self.layout.add_spacing('lg')
        
        self._render_performance_charts(data)
        self.layout.add_spacing('lg')
        
        self._render_recent_activities(data)
    
    def _render_kpi_summary(self, data: Dict[str, Any]) -> None:
        """Render KPI summary section"""
        st.markdown("### 📊 Key Performance Indicators")
        
        # Get KPI data or use fallback
        kpi_data = data.get('kpi_data', self._get_fallback_kpi_data())
        
        # Create metrics grid
        metrics = [
            {
                'label': 'Total Vessels',
                'value': kpi_data.get('total_vessels', 'N/A'),
                'delta': kpi_data.get('vessels_delta', None),
                'help': 'Total number of vessels currently in port'
            },
            {
                'label': 'Active Berths',
                'value': f"{kpi_data.get('active_berths', 0)}/{kpi_data.get('total_berths', 0)}",
                'delta': kpi_data.get('berths_delta', None),
                'help': 'Number of berths currently occupied'
            },
            {
                'label': 'Cargo Throughput',
                'value': f"{kpi_data.get('cargo_throughput', 0):,.0f} TEU",
                'delta': kpi_data.get('cargo_delta', None),
                'help': 'Total cargo throughput today'
            },
            {
                'label': 'Port Efficiency',
                'value': f"{kpi_data.get('efficiency', 0):.1f}%",
                'delta': kpi_data.get('efficiency_delta', None),
                'help': 'Overall port operational efficiency'
            }
        ]
        
        self.layout.create_metric_grid(metrics, columns=4)
    
    def _render_operational_status(self, data: Dict[str, Any]) -> None:
        """Render operational status section"""
        st.markdown("### 🚢 Operational Status")
        
        # Create columns for different status indicators
        cols = self.layout.create_columns('third')
        
        with cols[0]:
            self._render_vessel_status(data)
        
        with cols[1]:
            self._render_berth_status(data)
        
        with cols[2]:
            self._render_weather_status(data)
    
    def _render_vessel_status(self, data: Dict[str, Any]) -> None:
        """Render vessel status widget"""
        st.markdown("#### 🚢 Vessel Status")
        
        vessel_data = data.get('vessel_data', {})
        
        # Vessel status metrics
        status_metrics = [
            {'label': 'Arriving Today', 'value': vessel_data.get('arriving', 0)},
            {'label': 'In Port', 'value': vessel_data.get('in_port', 0)},
            {'label': 'Departing Today', 'value': vessel_data.get('departing', 0)}
        ]
        
        for metric in status_metrics:
            st.metric(metric['label'], metric['value'])
    
    def _render_berth_status(self, data: Dict[str, Any]) -> None:
        """Render berth status widget"""
        st.markdown("#### 🏗️ Berth Status")
        
        berth_data = data.get('berth_data', {})
        
        # Berth utilization chart
        if berth_data:
            occupied = berth_data.get('occupied', 0)
            total = berth_data.get('total', 1)
            utilization = (occupied / total) * 100 if total > 0 else 0
            
            # Create simple donut chart
            fig = go.Figure(data=[
                go.Pie(
                    labels=['Occupied', 'Available'],
                    values=[occupied, total - occupied],
                    hole=0.6,
                    marker_colors=['#ff6b6b', '#51cf66']
                )
            ])
            
            fig.update_layout(
                title=f"Utilization: {utilization:.1f}%",
                height=200,
                showlegend=False,
                margin=dict(t=40, b=0, l=0, r=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Berth data not available")
    
    def _render_weather_status(self, data: Dict[str, Any]) -> None:
        """Render weather status widget"""
        st.markdown("#### 🌤️ Weather Status")
        
        weather_data = data.get('weather_data', {})
        
        if weather_data:
            st.metric("Temperature", f"{weather_data.get('temperature', 'N/A')}°C")
            st.metric("Wind Speed", f"{weather_data.get('wind_speed', 'N/A')} km/h")
            st.metric("Visibility", f"{weather_data.get('visibility', 'N/A')} km")
        else:
            # Fallback weather data
            st.metric("Temperature", "24°C")
            st.metric("Wind Speed", "15 km/h")
            st.metric("Visibility", "10 km")
            
            self.layout.create_info_box(
                "Weather data simulated for demo",
                'info',
                '🌤️'
            )
    
    def _render_performance_charts(self, data: Dict[str, Any]) -> None:
        """Render performance charts section"""
        st.markdown("### 📈 Performance Trends")
        
        # Create columns for charts
        cols = self.layout.create_columns('half')
        
        with cols[0]:
            self._render_throughput_chart(data)
        
        with cols[1]:
            self._render_efficiency_chart(data)
    
    def _render_throughput_chart(self, data: Dict[str, Any]) -> None:
        """Render cargo throughput chart"""
        st.markdown("#### 📦 Cargo Throughput (Last 7 Days)")
        
        # Generate sample data if not available
        throughput_data = data.get('throughput_data')
        
        if throughput_data is None:
            # Generate sample throughput data
            dates = [datetime.now() - timedelta(days=i) for i in range(6, -1, -1)]
            throughput_values = [12500, 13200, 11800, 14100, 13500, 12900, 13800]
            
            df = pd.DataFrame({
                'Date': dates,
                'Throughput': throughput_values
            })
        else:
            df = pd.DataFrame(throughput_data)
        
        # Create line chart
        fig = px.line(
            df, 
            x='Date', 
            y='Throughput',
            title="Daily Cargo Throughput (TEU)",
            markers=True
        )
        
        fig.update_layout(
            height=300,
            margin=dict(t=40, b=40, l=40, r=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_efficiency_chart(self, data: Dict[str, Any]) -> None:
        """Render efficiency trend chart"""
        st.markdown("#### ⚡ Operational Efficiency")
        
        # Generate sample data if not available
        efficiency_data = data.get('efficiency_data')
        
        if efficiency_data is None:
            # Generate sample efficiency data
            categories = ['Vessel Turnaround', 'Cargo Handling', 'Berth Utilization', 'Equipment Uptime']
            current_values = [85, 92, 78, 95]
            target_values = [90, 95, 85, 98]
            
            df = pd.DataFrame({
                'Category': categories,
                'Current': current_values,
                'Target': target_values
            })
        else:
            df = pd.DataFrame(efficiency_data)
        
        # Create grouped bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Current',
            x=df['Category'],
            y=df['Current'],
            marker_color='#ff6b6b'
        ))
        
        fig.add_trace(go.Bar(
            name='Target',
            x=df['Category'],
            y=df['Target'],
            marker_color='#51cf66'
        ))
        
        fig.update_layout(
            title="Efficiency Metrics (%)",
            barmode='group',
            height=300,
            margin=dict(t=40, b=40, l=40, r=40),
            yaxis=dict(range=[0, 100])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_recent_activities(self, data: Dict[str, Any]) -> None:
        """Render recent activities section"""
        st.markdown("### 📋 Recent Activities")
        
        # Get recent activities or use fallback
        activities = data.get('recent_activities', self._get_fallback_activities())
        
        # Create columns for activities
        cols = self.layout.create_columns('half')
        
        with cols[0]:
            st.markdown("#### 🚢 Vessel Movements")
            for activity in activities.get('vessel_movements', []):
                timestamp = activity.get('timestamp', 'Unknown time')
                vessel = activity.get('vessel', 'Unknown vessel')
                action = activity.get('action', 'Unknown action')
                
                st.markdown(f"**{timestamp}** - {vessel}: {action}")
        
        with cols[1]:
            st.markdown("#### 📦 Cargo Operations")
            for activity in activities.get('cargo_operations', []):
                timestamp = activity.get('timestamp', 'Unknown time')
                operation = activity.get('operation', 'Unknown operation')
                quantity = activity.get('quantity', 'Unknown quantity')
                
                st.markdown(f"**{timestamp}** - {operation}: {quantity}")
    
    def _get_fallback_kpi_data(self) -> Dict[str, Any]:
        """Get fallback KPI data for demo purposes"""
        return {
            'total_vessels': 45,
            'vessels_delta': 3,
            'active_berths': 28,
            'total_berths': 35,
            'berths_delta': 2,
            'cargo_throughput': 13800,
            'cargo_delta': 1200,
            'efficiency': 87.5,
            'efficiency_delta': 2.3
        }
    
    def _get_fallback_activities(self) -> Dict[str, Any]:
        """Get fallback activities data for demo purposes"""
        return {
            'vessel_movements': [
                {'timestamp': '14:30', 'vessel': 'MSC Bellissima', 'action': 'Arrived at Berth 12'},
                {'timestamp': '13:45', 'vessel': 'COSCO Shanghai', 'action': 'Departed from Berth 8'},
                {'timestamp': '12:20', 'vessel': 'Evergreen Ever Given', 'action': 'Berthed at Terminal 3'}
            ],
            'cargo_operations': [
                {'timestamp': '14:15', 'operation': 'Container Loading', 'quantity': '450 TEU'},
                {'timestamp': '13:30', 'operation': 'Bulk Cargo Discharge', 'quantity': '2,300 tons'},
                {'timestamp': '12:45', 'operation': 'Container Unloading', 'quantity': '680 TEU'}
            ]
        }

def create_dashboard_page(layout_manager: LayoutManager) -> DashboardPage:
    """Factory function to create dashboard page"""
    return DashboardPage(layout_manager)