#!/usr/bin/env python3
"""
Comments for context:
This module provides Streamlit dashboard components for data quality monitoring
and reporting. It integrates with the DataQualityMonitor to display real-time
quality metrics, trends, alerts, and recommendations in an intuitive interface.

The dashboard includes:
1. Quality score overview with visual indicators
2. Deduplication metrics and efficiency tracking
3. Historical trends and quality progression
4. Active alerts and recommendations
5. Detailed quality analysis reports

This component is designed to be integrated into the main Streamlit dashboard
to provide comprehensive visibility into data quality across the vessel data pipeline.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

# Import our quality monitoring module
try:
    from src.utils.data_quality_monitor import DataQualityMonitor, QualityLevel
except ImportError:
    # Fallback for development/testing
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from src.utils.data_quality_monitor import DataQualityMonitor, QualityLevel

logger = logging.getLogger(__name__)

class QualityDashboard:
    """
    Streamlit dashboard component for data quality monitoring and visualization.
    
    This class provides methods to render quality metrics, trends, and alerts
    in an interactive Streamlit interface.
    """
    
    def __init__(self):
        """Initialize the quality dashboard"""
        self.monitor = DataQualityMonitor()
        
    def render_quality_overview(self, vessel_data: pd.DataFrame) -> None:
        """
        Render the main quality overview section.
        
        Args:
            vessel_data: DataFrame containing vessel data with quality metrics
        """
        st.header("🔍 Data Quality Overview")
        
        try:
            # Generate quality analysis
            with st.spinner("Analyzing data quality..."):
                analysis = self.monitor.analyze_vessel_data_quality(vessel_data)
            
            if analysis.get('status') == 'error':
                st.error(f"Quality analysis failed: {analysis.get('error', 'Unknown error')}")
                return
            
            # Display quality scores in columns
            col1, col2, col3, col4 = st.columns(4)
            
            quality_scores = analysis.get('quality_scores', {})
            basic_metrics = analysis.get('basic_metrics', {})
            
            with col1:
                overall_score = quality_scores.get('overall_score', 0)
                grade = quality_scores.get('grade', 'unknown')
                
                # Color coding based on grade
                color = self._get_grade_color(grade)
                
                st.metric(
                    label="Overall Quality Score",
                    value=f"{overall_score:.1f}%",
                    delta=None
                )
                st.markdown(f"<div style='text-align: center; color: {color}; font-weight: bold; font-size: 1.2em;'>{grade.upper()}</div>", 
                           unsafe_allow_html=True)
            
            with col2:
                completeness = quality_scores.get('data_completeness_score', 0)
                st.metric(
                    label="Data Completeness",
                    value=f"{completeness:.1f}%"
                )
            
            with col3:
                dedup_score = quality_scores.get('deduplication_score', 0)
                st.metric(
                    label="Deduplication Efficiency",
                    value=f"{dedup_score:.1f}%"
                )
            
            with col4:
                records_count = basic_metrics.get('records_count', 0)
                st.metric(
                    label="Total Records",
                    value=f"{records_count:,}"
                )
            
            # Display alerts if any
            alerts = analysis.get('alerts', [])
            if alerts:
                st.warning(f"⚠️ {len(alerts)} quality alert(s) detected")
                with st.expander("View Alerts", expanded=False):
                    for alert in alerts:
                        severity_icon = "🔴" if alert.severity in ['critical', 'poor'] else "🟡"
                        st.write(f"{severity_icon} **{alert.metric_name}**: {alert.message}")
            
            # Display recommendations
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                with st.expander("💡 Quality Recommendations", expanded=False):
                    for i, rec in enumerate(recommendations, 1):
                        st.write(f"{i}. {rec}")
            
        except Exception as e:
            logger.error(f"Error rendering quality overview: {e}")
            st.error(f"Failed to render quality overview: {str(e)}")
    
    def render_deduplication_metrics(self, vessel_data: pd.DataFrame) -> None:
        """
        Render detailed deduplication metrics and analysis.
        
        Args:
            vessel_data: DataFrame containing vessel data with deduplication metrics
        """
        st.header("🔄 Deduplication Analysis")
        
        try:
            # Get deduplication analysis
            analysis = self.monitor.analyze_vessel_data_quality(vessel_data)
            dedup_analysis = analysis.get('deduplication_analysis', {})
            
            # Deduplication summary
            col1, col2, col3 = st.columns(3)
            
            with col1:
                strategy = dedup_analysis.get('strategy_used', 'unknown')
                st.metric(
                    label="Strategy Used",
                    value=strategy.replace('_', ' ').title()
                )
            
            with col2:
                duplicates_removed = dedup_analysis.get('duplicates_removed', 0)
                st.metric(
                    label="Duplicates Removed",
                    value=f"{duplicates_removed:,}"
                )
            
            with col3:
                duplicate_rate = dedup_analysis.get('duplicate_rate', 0)
                st.metric(
                    label="Duplicate Rate",
                    value=f"{duplicate_rate:.2f}%"
                )
            
            # Deduplication efficiency chart
            if dedup_analysis.get('original_count', 0) > 0:
                self._render_deduplication_chart(dedup_analysis)
            
            # Potential remaining duplicates analysis
            potential_dupes = dedup_analysis.get('potential_remaining_duplicates', {})
            if potential_dupes and any(potential_dupes.values()):
                st.subheader("🔍 Potential Remaining Duplicates")
                
                col1, col2 = st.columns(2)
                with col1:
                    call_sign_dupes = potential_dupes.get('call_sign_duplicates', 0)
                    st.metric("Call Sign Duplicates", call_sign_dupes)
                
                with col2:
                    vessel_name_dupes = potential_dupes.get('vessel_name_duplicates', 0)
                    st.metric("Vessel Name Duplicates", vessel_name_dupes)
                
                # Show suspicious patterns
                suspicious_patterns = potential_dupes.get('suspicious_patterns', [])
                if suspicious_patterns:
                    st.write("**Suspicious Patterns:**")
                    for pattern in suspicious_patterns[:5]:  # Show top 5
                        st.write(f"- {pattern['call_sign']}: {pattern['count']} occurrences")
            
            # Temporal clustering analysis
            temporal_analysis = dedup_analysis.get('temporal_clustering', {})
            if temporal_analysis and not temporal_analysis.get('error'):
                st.subheader("⏰ Temporal Clustering Analysis")
                self._render_temporal_analysis(temporal_analysis)
            
        except Exception as e:
            logger.error(f"Error rendering deduplication metrics: {e}")
            st.error(f"Failed to render deduplication metrics: {str(e)}")
    
    def render_quality_trends(self) -> None:
        """Render quality trends over time"""
        st.header("📈 Quality Trends")
        
        try:
            # Time period selector
            col1, col2 = st.columns([1, 3])
            with col1:
                hours = st.selectbox(
                    "Time Period",
                    options=[6, 12, 24, 48, 72],
                    index=2,  # Default to 24 hours
                    format_func=lambda x: f"Last {x} hours"
                )
            
            # Get trends data
            trends = self.monitor.get_quality_trends(hours=hours)
            
            if trends.get('status') == 'no_data':
                st.info(f"No quality trend data available for the last {hours} hours")
                return
            elif trends.get('status') == 'error':
                st.error(f"Error loading trends: {trends.get('error')}")
                return
            
            # Display trend metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                overall_trend = trends.get('overall_score_trend', {})
                current_score = overall_trend.get('current', 0)
                trend_direction = overall_trend.get('trend_direction', 'stable')
                
                delta_color = self._get_trend_color(trend_direction)
                st.metric(
                    label="Overall Score",
                    value=f"{current_score:.1f}%",
                    delta=f"{trend_direction.replace('_', ' ').title()}"
                )
            
            with col2:
                completeness_trend = trends.get('completeness_trend', {})
                current_completeness = completeness_trend.get('current', 0)
                completeness_direction = completeness_trend.get('trend_direction', 'stable')
                
                st.metric(
                    label="Data Completeness",
                    value=f"{current_completeness:.1f}%",
                    delta=f"{completeness_direction.replace('_', ' ').title()}"
                )
            
            with col3:
                duplicate_trend = trends.get('duplicate_rate_trend', {})
                current_duplicate_rate = duplicate_trend.get('current', 0)
                duplicate_direction = duplicate_trend.get('trend_direction', 'stable')
                
                st.metric(
                    label="Duplicate Rate",
                    value=f"{current_duplicate_rate:.2f}%",
                    delta=f"{duplicate_direction.replace('_', ' ').title()}"
                )
            
            # Render trend charts if we have historical data
            if self.monitor.quality_history:
                self._render_trend_charts()
            
        except Exception as e:
            logger.error(f"Error rendering quality trends: {e}")
            st.error(f"Failed to render quality trends: {str(e)}")
    
    def render_detailed_report(self, vessel_data: pd.DataFrame) -> None:
        """Render detailed quality report"""
        st.header("📊 Detailed Quality Report")
        
        try:
            # Generate comprehensive report
            with st.spinner("Generating detailed quality report..."):
                report = self.monitor.generate_quality_report(vessel_data)
            
            if report.get('status') == 'error':
                st.error(f"Report generation failed: {report.get('error')}")
                return
            
            # Report summary
            summary = report.get('summary', {})
            st.subheader("Executive Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Overall Grade", summary.get('overall_grade', 'unknown').upper())
            with col2:
                st.metric("Quality Score", f"{summary.get('overall_score', 0):.1f}%")
            with col3:
                st.metric("Total Records", f"{summary.get('total_records', 0):,}")
            with col4:
                st.metric("Active Alerts", summary.get('active_alerts', 0))
            
            # Detailed analysis sections
            detailed_analysis = report.get('detailed_analysis', {})
            
            # Basic metrics
            if detailed_analysis.get('basic_metrics'):
                with st.expander("📋 Basic Data Metrics", expanded=False):
                    basic_metrics = detailed_analysis['basic_metrics']
                    
                    # Key column completeness
                    key_completeness = basic_metrics.get('key_column_completeness', {})
                    if key_completeness:
                        st.write("**Key Column Completeness:**")
                        for col, completeness in key_completeness.items():
                            st.progress(completeness / 100, text=f"{col}: {completeness:.1f}%")
                    
                    # Status distribution
                    status_dist = basic_metrics.get('status_distribution', {})
                    if status_dist:
                        st.write("**Vessel Status Distribution:**")
                        status_df = pd.DataFrame(list(status_dist.items()), columns=['Status', 'Count'])
                        fig = px.pie(status_df, values='Count', names='Status', title="Vessel Status Distribution")
                        st.plotly_chart(fig, use_container_width=True)
            
            # Deduplication analysis
            if detailed_analysis.get('deduplication_analysis'):
                with st.expander("🔄 Deduplication Analysis", expanded=False):
                    dedup_analysis = detailed_analysis['deduplication_analysis']
                    
                    # Display key metrics in a structured format
                    st.json({
                        'Strategy Used': dedup_analysis.get('strategy_used', 'unknown'),
                        'Original Count': dedup_analysis.get('original_count', 0),
                        'Final Count': dedup_analysis.get('final_count', 0),
                        'Duplicates Removed': dedup_analysis.get('duplicates_removed', 0),
                        'Duplicate Rate': f"{dedup_analysis.get('duplicate_rate', 0):.2f}%",
                        'Efficiency': f"{dedup_analysis.get('deduplication_efficiency', 0):.2f}%"
                    })
            
            # Quality scores breakdown
            if detailed_analysis.get('quality_scores'):
                with st.expander("🎯 Quality Scores Breakdown", expanded=False):
                    quality_scores = detailed_analysis['quality_scores']
                    
                    # Create a radar chart for quality dimensions
                    self._render_quality_radar_chart(quality_scores)
            
            # Export report option
            st.subheader("📥 Export Report")
            if st.button("Download Quality Report as JSON"):
                report_json = pd.Series(report).to_json(indent=2)
                st.download_button(
                    label="Download Report",
                    data=report_json,
                    file_name=f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
        except Exception as e:
            logger.error(f"Error rendering detailed report: {e}")
            st.error(f"Failed to render detailed report: {str(e)}")
    
    def _get_grade_color(self, grade: str) -> str:
        """Get color for quality grade"""
        color_map = {
            'excellent': '#28a745',  # Green
            'good': '#17a2b8',       # Blue
            'fair': '#ffc107',       # Yellow
            'poor': '#fd7e14',       # Orange
            'critical': '#dc3545'    # Red
        }
        return color_map.get(grade.lower(), '#6c757d')  # Default gray
    
    def _get_trend_color(self, trend: str) -> str:
        """Get color for trend direction"""
        if trend == 'improving':
            return 'normal'
        elif trend == 'declining':
            return 'inverse'
        else:
            return 'off'
    
    def _render_deduplication_chart(self, dedup_analysis: Dict[str, Any]) -> None:
        """Render deduplication efficiency chart"""
        original_count = dedup_analysis.get('original_count', 0)
        duplicates_removed = dedup_analysis.get('duplicates_removed', 0)
        final_count = dedup_analysis.get('final_count', 0)
        
        # Create a simple bar chart showing before/after
        fig = go.Figure(data=[
            go.Bar(name='Original Records', x=['Before Deduplication'], y=[original_count], marker_color='lightblue'),
            go.Bar(name='Duplicates Removed', x=['Duplicates'], y=[duplicates_removed], marker_color='red'),
            go.Bar(name='Final Records', x=['After Deduplication'], y=[final_count], marker_color='green')
        ])
        
        fig.update_layout(
            title="Deduplication Results",
            yaxis_title="Number of Records",
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_temporal_analysis(self, temporal_analysis: Dict[str, Any]) -> None:
        """Render temporal clustering analysis"""
        col1, col2 = st.columns(2)
        
        with col1:
            time_gaps = temporal_analysis.get('time_gaps_analysis', {})
            if time_gaps:
                st.write("**Time Gap Analysis:**")
                st.write(f"- Mean gap: {time_gaps.get('mean_gap_hours', 0):.1f} hours")
                st.write(f"- Median gap: {time_gaps.get('median_gap_hours', 0):.1f} hours")
                st.write(f"- Min gap: {time_gaps.get('min_gap_minutes', 0):.1f} minutes")
        
        with col2:
            clustering = temporal_analysis.get('clustering_patterns', {})
            if clustering:
                st.write("**Clustering Patterns:**")
                st.write(f"- Arrivals within 1 hour: {clustering.get('arrivals_within_1hour', 0)}")
                st.write(f"- Clustering rate: {clustering.get('clustering_rate', 0):.1f}%")
        
        # Hourly distribution chart
        distribution = temporal_analysis.get('data_distribution', {})
        if distribution and distribution.get('hourly_distribution'):
            hourly_data = distribution['hourly_distribution']
            hours = list(hourly_data.keys())
            counts = list(hourly_data.values())
            
            fig = go.Figure(data=go.Bar(x=hours, y=counts))
            fig.update_layout(
                title="Vessel Arrivals by Hour of Day",
                xaxis_title="Hour",
                yaxis_title="Number of Arrivals",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_trend_charts(self) -> None:
        """Render historical trend charts"""
        if not self.monitor.quality_history:
            return
        
        # Convert history to DataFrame
        history_df = pd.DataFrame(self.monitor.quality_history)
        history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
        
        # Create trend charts
        fig = go.Figure()
        
        # Overall score trend
        fig.add_trace(go.Scatter(
            x=history_df['timestamp'],
            y=history_df['overall_score'],
            mode='lines+markers',
            name='Overall Score',
            line=dict(color='blue')
        ))
        
        # Data completeness trend
        fig.add_trace(go.Scatter(
            x=history_df['timestamp'],
            y=history_df['data_completeness'],
            mode='lines+markers',
            name='Data Completeness',
            line=dict(color='green')
        ))
        
        # Duplicate rate trend (inverted for better visualization)
        fig.add_trace(go.Scatter(
            x=history_df['timestamp'],
            y=100 - history_df['duplicate_rate'],  # Invert so higher is better
            mode='lines+markers',
            name='Deduplication Efficiency',
            line=dict(color='orange')
        ))
        
        fig.update_layout(
            title="Quality Trends Over Time",
            xaxis_title="Time",
            yaxis_title="Score (%)",
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_quality_radar_chart(self, quality_scores: Dict[str, Any]) -> None:
        """Render radar chart for quality dimensions"""
        categories = ['Data Completeness', 'Deduplication', 'Consistency']
        values = [
            quality_scores.get('data_completeness_score', 0),
            quality_scores.get('deduplication_score', 0),
            quality_scores.get('consistency_score', 0)
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Quality Scores'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="Quality Dimensions Breakdown",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Global instance for easy access
quality_dashboard = QualityDashboard()