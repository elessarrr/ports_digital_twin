import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import numpy as np

from components.layout import LayoutManager
from styles.theme_manager import ThemeManager

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
        tab_names = ["Cargo Statistics", "Performance Metrics", "Trend Analysis", "Forecasting"]
        tab_icons = ["📦", "⚡", "📈", "🔮"]
        
        tabs = self.layout.create_tabs_container(tab_names, tab_icons)
        
        with tabs[0]:
            self._render_cargo_statistics(data)
        
        with tabs[1]:
            self._render_performance_metrics(data)
        
        with tabs[2]:
            self._render_trend_analysis(data)
        
        with tabs[3]:
            self._render_forecasting(data)
    
    def _render_cargo_statistics(self, data: Dict[str, Any]) -> None:
        """Render cargo statistics section"""
        self.layout.add_spacing('md')
        
        # Cargo overview metrics
        self._render_cargo_overview(data)
        self.layout.add_spacing('lg')
        
        # Cargo breakdown charts
        cols = self.layout.create_columns('half')
        
        with cols[0]:
            self._render_cargo_types_chart(data)
        
        with cols[1]:
            self._render_transport_modes_chart(data)
        
        self.layout.add_spacing('lg')
        
        # Detailed cargo statistics
        self._render_cargo_details_table(data)
    
    def _render_cargo_overview(self, data: Dict[str, Any]) -> None:
        """Render cargo overview metrics"""
        st.markdown("### 📦 Cargo Overview")
        
        cargo_data = data.get('cargo_statistics', {})
        
        metrics = [
            {
                'label': 'Total Throughput',
                'value': f"{cargo_data.get('total_throughput', 125000):,} TEU",
                'delta': f"+{cargo_data.get('throughput_delta', 5200):,}",
                'help': 'Total cargo throughput this month'
            },
            {
                'label': 'Container Volume',
                'value': f"{cargo_data.get('container_volume', 98000):,} TEU",
                'delta': f"+{cargo_data.get('container_delta', 4100):,}",
                'help': 'Container cargo volume this month'
            },
            {
                'label': 'Bulk Cargo',
                'value': f"{cargo_data.get('bulk_cargo', 27000):,} tons",
                'delta': f"+{cargo_data.get('bulk_delta', 1100):,}",
                'help': 'Bulk cargo volume this month'
            },
            {
                'label': 'Average Dwell Time',
                'value': f"{cargo_data.get('avg_dwell_time', 3.2):.1f} days",
                'delta': f"-{cargo_data.get('dwell_delta', 0.3):.1f}",
                'help': 'Average cargo dwell time in port'
            }
        ]
        
        self.layout.create_metric_grid(metrics, columns=4)
    
    def _render_cargo_types_chart(self, data: Dict[str, Any]) -> None:
        """Render cargo types distribution chart"""
        st.markdown("#### 📊 Cargo Types Distribution")
        
        cargo_types_data = data.get('cargo_types', self._get_fallback_cargo_types())
        
        # Create donut chart
        fig = go.Figure(data=[
            go.Pie(
                labels=list(cargo_types_data.keys()),
                values=list(cargo_types_data.values()),
                hole=0.4,
                textinfo='label+percent',
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title="Cargo Distribution by Type",
            height=400,
            margin=dict(t=40, b=40, l=40, r=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_transport_modes_chart(self, data: Dict[str, Any]) -> None:
        """Render transport modes chart"""
        st.markdown("#### 🚛 Transport Modes")
        
        transport_data = data.get('transport_modes', self._get_fallback_transport_modes())
        
        if transport_data:
            df = pd.DataFrame(list(transport_data.items()), columns=['Mode', 'Volume'])
            
            # Create bar chart
            fig = px.bar(
                df,
                x='Mode',
                y='Volume',
                title="Cargo Volume by Transport Mode",
                color='Volume',
                color_continuous_scale='viridis'
            )
            
            fig.update_layout(
                height=400,
                margin=dict(t=40, b=40, l=40, r=40),
                xaxis_title="Transport Mode",
                yaxis_title="Volume (TEU)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No transport mode data available")
    
    def _render_cargo_details_table(self, data: Dict[str, Any]) -> None:
        """Render detailed cargo statistics table"""
        st.markdown("### 📋 Detailed Cargo Statistics")
        
        cargo_details = data.get('cargo_details', self._get_fallback_cargo_details())
        
        if cargo_details:
            df = pd.DataFrame(cargo_details)
            
            # Add filters
            cols = st.columns(3)
            
            with cols[0]:
                period_filter = st.selectbox(
                    "Time Period",
                    options=['Last 7 Days', 'Last 30 Days', 'Last 90 Days', 'Year to Date'],
                    key="cargo_period_filter"
                )
            
            with cols[1]:
                cargo_type_filter = st.selectbox(
                    "Cargo Type",
                    options=['All'] + list(df['cargo_type'].unique()) if 'cargo_type' in df.columns else ['All'],
                    key="cargo_type_filter"
                )
            
            with cols[2]:
                terminal_filter = st.selectbox(
                    "Terminal",
                    options=['All'] + list(df['terminal'].unique()) if 'terminal' in df.columns else ['All'],
                    key="terminal_filter"
                )
            
            # Apply filters
            filtered_df = df.copy()
            
            if cargo_type_filter != 'All' and 'cargo_type' in df.columns:
                filtered_df = filtered_df[filtered_df['cargo_type'] == cargo_type_filter]
            
            if terminal_filter != 'All' and 'terminal' in df.columns:
                filtered_df = filtered_df[filtered_df['terminal'] == terminal_filter]
            
            # Display table
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.info("No cargo details available")
    
    def _render_performance_metrics(self, data: Dict[str, Any]) -> None:
        """Render performance metrics section"""
        self.layout.add_spacing('md')
        
        # Performance overview
        self._render_performance_overview(data)
        self.layout.add_spacing('lg')
        
        # Performance charts
        cols = self.layout.create_columns('half')
        
        with cols[0]:
            self._render_efficiency_metrics_chart(data)
        
        with cols[1]:
            self._render_productivity_chart(data)
        
        self.layout.add_spacing('lg')
        
        # KPI dashboard
        self._render_kpi_dashboard(data)
    
    def _render_performance_overview(self, data: Dict[str, Any]) -> None:
        """Render performance overview metrics"""
        st.markdown("### ⚡ Performance Overview")
        
        performance_data = data.get('performance_metrics', {})
        
        metrics = [
            {
                'label': 'Overall Efficiency',
                'value': f"{performance_data.get('overall_efficiency', 87.5):.1f}%",
                'delta': f"+{performance_data.get('efficiency_delta', 2.3):.1f}%",
                'help': 'Overall port operational efficiency'
            },
            {
                'label': 'Vessel Turnaround',
                'value': f"{performance_data.get('vessel_turnaround', 18.5):.1f}h",
                'delta': f"-{performance_data.get('turnaround_delta', 1.2):.1f}h",
                'help': 'Average vessel turnaround time'
            },
            {
                'label': 'Crane Productivity',
                'value': f"{performance_data.get('crane_productivity', 32):.0f} moves/h",
                'delta': f"+{performance_data.get('crane_delta', 3):.0f}",
                'help': 'Average crane moves per hour'
            },
            {
                'label': 'Berth Utilization',
                'value': f"{performance_data.get('berth_utilization', 78.2):.1f}%",
                'delta': f"+{performance_data.get('berth_delta', 4.1):.1f}%",
                'help': 'Average berth utilization rate'
            }
        ]
        
        self.layout.create_metric_grid(metrics, columns=4)
    
    def _render_efficiency_metrics_chart(self, data: Dict[str, Any]) -> None:
        """Render efficiency metrics radar chart"""
        st.markdown("#### 📊 Efficiency Metrics")
        
        efficiency_data = data.get('efficiency_metrics', self._get_fallback_efficiency_metrics())
        
        if efficiency_data:
            categories = list(efficiency_data.keys())
            values = list(efficiency_data.values())
            
            # Create radar chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Current Performance',
                line_color='#ff6b6b'
            ))
            
            # Add target line
            target_values = [90] * len(categories)  # 90% target for all metrics
            fig.add_trace(go.Scatterpolar(
                r=target_values,
                theta=categories,
                fill='toself',
                name='Target',
                line_color='#51cf66',
                opacity=0.3
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                title="Performance vs Target",
                height=400,
                margin=dict(t=40, b=40, l=40, r=40)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No efficiency metrics available")
    
    def _render_productivity_chart(self, data: Dict[str, Any]) -> None:
        """Render productivity trend chart"""
        st.markdown("#### 📈 Productivity Trends")
        
        productivity_data = data.get('productivity_trends', self._get_fallback_productivity_trends())
        
        if productivity_data:
            df = pd.DataFrame(productivity_data)
            
            # Create multi-line chart
            fig = go.Figure()
            
            for column in df.columns[1:]:  # Skip date column
                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=df[column],
                    mode='lines+markers',
                    name=column,
                    line=dict(width=3)
                ))
            
            fig.update_layout(
                title="Productivity Trends (Last 30 Days)",
                height=400,
                margin=dict(t=40, b=40, l=40, r=40),
                xaxis_title="Date",
                yaxis_title="Productivity Index"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No productivity trend data available")
    
    def _render_kpi_dashboard(self, data: Dict[str, Any]) -> None:
        """Render KPI dashboard"""
        st.markdown("### 🎯 Key Performance Indicators")
        
        kpi_data = data.get('kpi_data', self._get_fallback_kpi_data())
        
        # Create KPI cards
        cols = self.layout.create_columns('third')
        
        for i, (kpi_name, kpi_info) in enumerate(kpi_data.items()):
            with cols[i % 3]:
                current_value = kpi_info.get('current', 0)
                target_value = kpi_info.get('target', 100)
                unit = kpi_info.get('unit', '%')
                
                # Calculate progress
                progress = (current_value / target_value) * 100 if target_value > 0 else 0
                
                st.markdown(f"#### {kpi_name}")
                st.metric(
                    label=f"Current ({unit})",
                    value=f"{current_value:.1f}",
                    delta=f"Target: {target_value:.1f}"
                )
                
                # Progress bar
                st.progress(min(progress / 100, 1.0))
                st.markdown(f"Progress: {progress:.1f}%")
    
    def _render_trend_analysis(self, data: Dict[str, Any]) -> None:
        """Render trend analysis section"""
        self.layout.add_spacing('md')
        
        st.markdown("### 📈 Trend Analysis")
        
        # Time series analysis
        cols = self.layout.create_columns('half')
        
        with cols[0]:
            self._render_throughput_trends(data)
        
        with cols[1]:
            self._render_seasonal_analysis(data)
        
        self.layout.add_spacing('lg')
        
        # Comparative analysis
        self._render_comparative_analysis(data)
    
    def _render_throughput_trends(self, data: Dict[str, Any]) -> None:
        """Render throughput trends chart"""
        st.markdown("#### 📦 Throughput Trends")
        
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
        st.markdown("#### 🗓️ Seasonal Analysis")
        
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
        st.markdown("#### 🔍 Comparative Analysis")
        
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
        
        st.markdown("### 🔮 Forecasting")
        
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