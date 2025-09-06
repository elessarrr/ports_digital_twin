import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import numpy as np

from ..components.layout import LayoutManager
from ..styles.theme_manager import ThemeManager
from ..components.weather_impact_analysis import render_weather_impact_analysis
from ..components.analytics_view import render_analytics_view

class AnalyticsPage:
    """Analytics page with cargo statistics, performance metrics, and data visualization"""
    
    def __init__(self, layout_manager: LayoutManager):
        self.layout = layout_manager
    
    def render(self, data: Dict[str, Any]) -> None:
        """Render the analytics page"""
        # Apply custom CSS
        self.layout.apply_custom_css()
        
        # Page header
        self.layout.create_section_header(
            "Analytics & Performance",
            "Comprehensive cargo statistics, performance metrics, and trend analysis",
            "📊"
        )
        
        # Create tabs for different analytics views
        tab_names = ["Cargo Statistics", "Performance Metrics", "Trend Analysis", "Forecasting", "Weather Impact"]
        tab_icons = ["📦", "⚡", "📈", "🔮", "🌦️"]
        
        tabs = self.layout.create_tabs_container(tab_names, tab_icons)
        
        with tabs[0]:
            self.render_cargo_statistics_tab(data)
        
        with tabs[1]:
            self.render_performance_metrics_tab(data)
        
        with tabs[2]:
            self.render_trend_analysis_tab(data)
        
        with tabs[3]:
            self._render_forecasting(data)

        with tabs[4]:
            render_weather_impact_analysis()
    
    def render_cargo_statistics_tab(self, data: dict) -> None:
        """Render the cargo statistics tab"""
        render_analytics_view(data, ['cargo_statistics'])

    def render_performance_metrics_tab(self, data: dict) -> None:
        """Render the performance metrics tab"""
        render_analytics_view(data, ['performance_metrics'])

    def render_trend_analysis_tab(self, data: dict) -> None:
        """Render the trend analysis tab"""
        self.layout.add_spacing('md')
        
        with self.layout.create_card("📈 Trend Analysis"):
            # Time series analysis
            cols = self.layout.create_columns('half')
            
            with cols[0]:
                self._render_throughput_trends(data)
            
            with cols[1]:
                self._render_seasonal_analysis(data)
            
            self.layout.add_spacing('lg')
            
            # Comparative analysis
            self._render_comparative_analysis(data)

    def render_forecasting_tab(self, data: dict) -> None:
        """Render the forecasting tab"""
        self._render_forecasting(data)

    def render_weather_impact_tab(self, data: dict) -> None:
        """Render the weather impact analysis tab"""
        render_weather_impact_analysis(data)

    def _render_throughput_trends(self, data: Dict[str, Any]) -> None:
        """Render throughput trends chart"""
        throughput_trends = data.get('throughput_trends', self._get_fallback_throughput_trends())
        
        if throughput_trends:
            df = pd.DataFrame(throughput_trends)
            
            # Create area chart
            fig = px.area(
                df,
                x='date',
                y='throughput',
                title="Monthly Throughput Trends",
                color_discrete_sequence=['#ff6b6b']
            )
            
            fig.update_layout(
                height=400,
                margin=dict(t=40, b=40, l=40, r=40),
                xaxis_title="Date",
                yaxis_title="Throughput (TEU)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No throughput trend data available")
    
    def _render_seasonal_analysis(self, data: Dict[str, Any]) -> None:
        """Render seasonal analysis chart"""
        seasonal_data = data.get('seasonal_analysis', self._get_fallback_seasonal_data())
        
        if seasonal_data:
            df = pd.DataFrame(seasonal_data)
            
            # Create heatmap
            fig = px.imshow(
                df.set_index('month'),
                title="Seasonal Cargo Volume Patterns",
                color_continuous_scale='viridis',
                aspect='auto'
            )
            
            fig.update_layout(
                height=400,
                margin=dict(t=40, b=40, l=40, r=40)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No seasonal analysis data available")
    
    def _render_comparative_analysis(self, data: Dict[str, Any]) -> None:
        """Render comparative analysis"""
        comparative_data = data.get('comparative_analysis', self._get_fallback_comparative_data())
        
        if comparative_data:
            df = pd.DataFrame(comparative_data)
            
            # Create grouped bar chart
            fig = px.bar(
                df,
                x='metric',
                y='value',
                color='period',
                barmode='group',
                title="Current vs Previous Period Comparison"
            )
            
            fig.update_layout(
                height=400,
                margin=dict(t=40, b=40, l=40, r=40),
                xaxis_title="Metrics",
                yaxis_title="Value"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No comparative analysis data available")

    def _render_forecasting(self, data: Dict[str, Any]) -> None:
        """Render forecasting section"""
        self.layout.add_spacing('md')
        
        with self.layout.create_card("🔮 Forecasting"):
            # Forecasting controls
            cols = st.columns(3)
            
            with cols[0]:
                forecast_period = st.selectbox(
                    "Forecast Period",
                    options=['Next 7 Days', 'Next 30 Days', 'Next 90 Days'],
                    key="forecast_period"
                )
            
            with cols[1]:
                forecast_metric = st.selectbox(
                    "Metric",
                    options=['Throughput', 'Vessel Arrivals', 'Berth Utilization'],
                    key="forecast_metric"
                )
            
            with cols[2]:
                confidence_level = st.selectbox(
                    "Confidence Level",
                    options=['80%', '90%', '95%'],
                    key="confidence_level"
                )
        
        self.layout.add_spacing('md')
        
        # Forecast visualization
        self._render_forecast_chart(data, forecast_period, forecast_metric, confidence_level)
        
        self.layout.add_spacing('lg')
        
        # Forecast insights
        self._render_forecast_insights(data)
    
    def _render_forecast_chart(self, data: Dict[str, Any], period: str, metric: str, confidence: str) -> None:
        """Render forecast chart"""
        st.markdown(f"#### 📊 {metric} Forecast - {period}")
        
        forecast_data = data.get('forecast_data', self._get_fallback_forecast_data())
        
        if forecast_data:
            df = pd.DataFrame(forecast_data)
            
            # Create forecast chart with confidence intervals
            fig = go.Figure()
            
            # Historical data
            fig.add_trace(go.Scatter(
                x=df['date'][:20],  # First 20 points as historical
                y=df['actual'][:20],
                mode='lines+markers',
                name='Historical',
                line=dict(color='#2196f3', width=3)
            ))
            
            # Forecast
            fig.add_trace(go.Scatter(
                x=df['date'][19:],  # Overlap one point
                y=df['forecast'][19:],
                mode='lines+markers',
                name='Forecast',
                line=dict(color='#ff6b6b', width=3, dash='dash')
            ))
            
            # Confidence interval
            fig.add_trace(go.Scatter(
                x=df['date'][19:],
                y=df['upper_bound'][19:],
                mode='lines',
                name='Upper Bound',
                line=dict(color='rgba(255, 107, 107, 0.3)'),
                showlegend=False
            ))
            
            fig.add_trace(go.Scatter(
                x=df['date'][19:],
                y=df['lower_bound'][19:],
                mode='lines',
                name='Lower Bound',
                line=dict(color='rgba(255, 107, 107, 0.3)'),
                fill='tonexty',
                fillcolor='rgba(255, 107, 107, 0.2)',
                showlegend=False
            ))
            
            fig.update_layout(
                title=f"{metric} Forecast with {confidence} Confidence Interval",
                height=400,
                margin=dict(t=40, b=40, l=40, r=40),
                xaxis_title="Date",
                yaxis_title=metric
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No forecast data available")
    
    def _render_forecast_insights(self, data: Dict[str, Any]) -> None:
        """Render forecast insights"""
        st.markdown("#### 💡 Forecast Insights")
        
        insights = data.get('forecast_insights', self._get_fallback_forecast_insights())
        
        for insight in insights:
            self.layout.create_info_box(
                insight['message'],
                insight.get('type', 'info'),
                insight.get('icon', '💡')
            )
    
    # Fallback data methods
    def _get_fallback_cargo_types(self) -> Dict[str, int]:
        return {
            'Containers': 98000,
            'Bulk Cargo': 27000,
            'General Cargo': 15000,
            'Liquid Bulk': 8500,
            'RoRo': 3200
        }
    
    def _get_fallback_transport_modes(self) -> Dict[str, int]:
        return {
            'Truck': 85000,
            'Rail': 45000,
            'Barge': 18000,
            'Pipeline': 3500
        }
    
    def _get_fallback_cargo_details(self) -> List[Dict[str, Any]]:
        return [
            {
                'date': '2024-01-15',
                'cargo_type': 'Container',
                'terminal': 'Terminal 1',
                'volume': 2400,
                'origin': 'Shanghai',
                'destination': 'Los Angeles'
            },
            {
                'date': '2024-01-15',
                'cargo_type': 'Bulk',
                'terminal': 'Terminal 2',
                'volume': 1800,
                'origin': 'Australia',
                'destination': 'Hong Kong'
            }
        ]
    
    def _get_fallback_efficiency_metrics(self) -> Dict[str, float]:
        return {
            'Vessel Turnaround': 85,
            'Cargo Handling': 92,
            'Berth Utilization': 78,
            'Equipment Uptime': 95,
            'Labor Productivity': 88,
            'Energy Efficiency': 82
        }
    
    def _get_fallback_productivity_trends(self) -> List[Dict[str, Any]]:
        dates = [datetime.now() - timedelta(days=i) for i in range(29, -1, -1)]
        return [
            {
                'date': date,
                'Crane Productivity': 30 + np.random.normal(0, 3),
                'Truck Turnaround': 25 + np.random.normal(0, 2),
                'Vessel Efficiency': 85 + np.random.normal(0, 5)
            }
            for date in dates
        ]
    
    def _get_fallback_kpi_data(self) -> Dict[str, Dict[str, float]]:
        return {
            'Throughput Efficiency': {'current': 87.5, 'target': 90.0, 'unit': '%'},
            'Cost per TEU': {'current': 125.0, 'target': 120.0, 'unit': '$'},
            'Customer Satisfaction': {'current': 92.3, 'target': 95.0, 'unit': '%'}
        }
    
    def _get_fallback_throughput_trends(self) -> List[Dict[str, Any]]:
        dates = [datetime.now() - timedelta(days=30*i) for i in range(11, -1, -1)]
        return [
            {
                'date': date,
                'throughput': 100000 + np.random.normal(0, 10000)
            }
            for date in dates
        ]
    
    def _get_fallback_seasonal_data(self) -> List[Dict[str, Any]]:
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        cargo_types = ['Container', 'Bulk', 'General']
        
        data = []
        for month in months:
            row = {'month': month}
            for cargo_type in cargo_types:
                row[cargo_type] = np.random.randint(80, 120)
            data.append(row)
        
        return data
    
    def _get_fallback_comparative_data(self) -> List[Dict[str, Any]]:
        metrics = ['Throughput', 'Efficiency', 'Turnaround Time', 'Cost per TEU']
        data = []
        
        for metric in metrics:
            data.extend([
                {'metric': metric, 'period': 'Current', 'value': np.random.randint(80, 120)},
                {'metric': metric, 'period': 'Previous', 'value': np.random.randint(70, 110)}
            ])
        
        return data
    
    def _get_fallback_forecast_data(self) -> List[Dict[str, Any]]:
        dates = [datetime.now() + timedelta(days=i) for i in range(-20, 11)]
        data = []
        
        for i, date in enumerate(dates):
            base_value = 100 + i * 2 + np.random.normal(0, 5)
            data.append({
                'date': date,
                'actual': base_value if i < 20 else None,
                'forecast': base_value if i >= 19 else None,
                'upper_bound': base_value * 1.1 if i >= 19 else None,
                'lower_bound': base_value * 0.9 if i >= 19 else None
            })
        
        return data
    
    def _get_fallback_forecast_insights(self) -> List[Dict[str, str]]:
        return [
            {
                'message': 'Throughput is expected to increase by 15% over the next 30 days',
                'type': 'success',
                'icon': '📈'
            },
            {
                'message': 'Peak season approaching - consider additional berth capacity',
                'type': 'warning',
                'icon': '⚠️'
            },
            {
                'message': 'Weather conditions may impact operations in week 3',
                'type': 'info',
                'icon': '🌤️'
            }
        ]

def create_analytics_page(layout_manager: LayoutManager) -> AnalyticsPage:
    """Factory function to create analytics page"""
    return AnalyticsPage(layout_manager)

    def _render_cargo_statistics(self, data: dict) -> None:
        """Render cargo statistics and visualizations."""
        st.header("📦 Cargo Analytics")
        
        cargo_data = data.get('cargo_volume', pd.DataFrame())
        
        if cargo_data.empty:
            st.warning("No cargo data available.")
            return

        with self.layout.create_card("📦 Cargo Overview"):
            total_cargo = cargo_data['Actual Tonnage'].sum()
            avg_tonnage = cargo_data['Actual Tonnage'].mean()
            
            col1, col2 = self.layout.create_columns('half')
            
            with col1:
                st.metric("Total Cargo Handled", f"{total_cargo:,.0f} tons")
            
            with col2:
                st.metric("Average Tonnage per Vessel", f"{avg_tonnage:,.2f} tons")

            self.layout.add_spacing()

            fig = px.bar(
                cargo_data,
                x='Date',
                y='Actual Tonnage',
                title='Daily Cargo Volume',
                labels={'Actual Tonnage': 'Tonnage (tons)'}
            )
            st.plotly_chart(fig, use_container_width=True)

    def _render_vessel_analytics(self, data: dict) -> None:
        """Render vessel-related analytics."""
        vessel_data = data.get('vessel_movements', pd.DataFrame())
        
        if vessel_data.empty:
            st.warning("No vessel movement data available.")
            return

        with self.layout.create_card("⚓ Vessel Analytics"):
            total_movements = len(vessel_data)
            avg_turnaround = vessel_data['Turnaround Time (hours)'].mean()
            
            col1, col2 = self.layout.create_columns('half')
            
            with col1:
                st.metric("Total Vessel Movements", f"{total_movements}")
            
            with col2:
                st.metric("Average Turnaround Time", f"{avg_turnaround:.2f} hours")

            self.layout.add_spacing()

            turnaround_fig = px.histogram(
                vessel_data,
                x='Turnaround Time (hours)',
                title='Distribution of Vessel Turnaround Time',
                nbins=20
            )
            st.plotly_chart(turnaround_fig, use_container_width=True)

    def _render_berth_occupancy(self, data: dict) -> None:
        """Render berth occupancy analytics."""
        berth_data = data.get('berth_occupancy', pd.DataFrame())
        
        if berth_data.empty:
            st.warning("No berth occupancy data available.")
            return

        with self.layout.create_card("📊 Berth Occupancy"):
            avg_occupancy = berth_data['Occupancy Rate'].mean() * 100
            
            st.metric("Average Berth Occupancy", f"{avg_occupancy:.2f}%")

            self.layout.add_spacing()

            occupancy_fig = px.line(
                berth_data,
                x='Date',
                y='Occupancy Rate',
                title='Berth Occupancy Over Time',
                labels={'Occupancy Rate': 'Occupancy (%)'}
            )
            st.plotly_chart(occupancy_fig, use_container_width=True)

    def _render_environmental_impact(self, data: dict) -> None:
        """Render environmental impact section"""
        self.layout.add_spacing('md')
        
        with self.layout.create_card("🌍 Environmental Impact"):
            # Environmental controls
            cols = st.columns(2)
            
            with cols[0]:
                emission_type = st.selectbox(
                    "Emission Type",
                    options=['CO2', 'SOx', 'NOx'],
                    key="emission_type"
                )
            
            with cols[1]:
                env_time_period = st.selectbox(
                    "Time Period",
                    options=['Last 30 Days', 'Last 90 Days', 'Last Year'],
                    key="env_time_period"
                )
        
        self.layout.add_spacing('md')
        
        # Environmental visualization
        self._render_environmental_chart(data, emission_type, env_time_period)
        
        self.layout.add_spacing('lg')
        
        # Environmental insights
        self._render_environmental_insights(data)