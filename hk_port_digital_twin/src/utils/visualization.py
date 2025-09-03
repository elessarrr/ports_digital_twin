"""Visualization Utilities for Hong Kong Port Digital Twin

This module provides reusable functions for creating charts and graphs
to visualize port operations and simulation results.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Optional
import numpy as np


def create_port_layout_chart(berths_data: pd.DataFrame) -> go.Figure:
    """Create visual representation of port layout
    
    Args:
        berths_data: DataFrame with berth information including berth_id, name, 
                    max_capacity_teu, crane_count, berth_type, is_occupied
    
    Returns:
        Plotly figure showing port layout
    """
    # Create a scatter plot representing berths
    fig = go.Figure()
    
    # Define colors for different berth types
    color_map = {
        'container': 'blue',
        'bulk': 'green', 
        'mixed': 'orange'
    }
    
    # Create positions for berths (arrange in a line along the port)
    x_positions = list(range(len(berths_data)))
    y_positions = [0] * len(berths_data)
    
    for idx, berth in berths_data.iterrows():
        color = color_map.get(berth['berth_type'], 'gray')
        symbol = 'square' if berth.get('is_occupied', False) else 'circle'
        
        fig.add_trace(go.Scatter(
            x=[x_positions[idx]],
            y=[y_positions[idx]],
            mode='markers+text',
            marker=dict(
                size=20 + berth['crane_count'] * 5,  # Size based on crane count
                color=color,
                symbol=symbol,
                line=dict(width=2, color='black')
            ),
            text=[berth['name']],
            textposition='top center',
            name=f"Berth {berth['berth_id']}",
            hovertemplate=(
                f"<b>{berth['name']}</b><br>"
                f"Type: {berth['berth_type']}<br>"
                f"Capacity: {berth['max_capacity_teu']:,} TEU<br>"
                f"Cranes: {berth['crane_count']}<br>"
                f"Status: {'Occupied' if berth.get('is_occupied', False) else 'Available'}"
                "<extra></extra>"
            )
        ))
    
    fig.update_layout(
        title="Hong Kong Port - Berth Layout",
        xaxis_title="Berth Position",
        yaxis_title="",
        showlegend=False,
        height=300,
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        xaxis=dict(showgrid=True, zeroline=False)
    )
    
    return fig


def create_ship_queue_chart(queue_data: List[Dict]) -> go.Figure:
    """Visualize ship waiting queue
    
    Args:
        queue_data: List of dictionaries with ship information including
                   ship_id, name, ship_type, size_teu, waiting_time
    
    Returns:
        Plotly figure showing ship queue
    """
    if not queue_data:
        # Return empty chart if no ships in queue
        fig = go.Figure()
        fig.add_annotation(
            text="No ships currently in queue",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        fig.update_layout(
            title="Ship Waiting Queue",
            height=300,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(queue_data)
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    # Color mapping for ship types
    type_colors = {
        'container': 'lightblue',
        'bulk': 'lightgreen',
        'mixed': 'lightyellow'
    }
    
    # Add a trace for each ship type to create a legend
    for ship_type, color in type_colors.items():
        type_df = df[df['ship_type'] == ship_type]
        if not type_df.empty:
            fig.add_trace(go.Bar(
                y=type_df['name'],
                x=type_df['waiting_time'],
                orientation='h',
                marker_color=color,
                text=[f"{size:,} TEU" for size in type_df['size_teu']],
                textposition='inside',
                name=ship_type.capitalize(),
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Type: %{customdata[0]}<br>"
                    "Size: %{customdata[1]:,} TEU<br>"
                    "Waiting: %{x:.1f} hours"
                    "<extra></extra>"
                ),
                customdata=list(zip(type_df['ship_type'], type_df['size_teu']))
            ))

    # Handle other ship types
    other_df = df[~df['ship_type'].isin(type_colors.keys())]
    if not other_df.empty:
        fig.add_trace(go.Bar(
            y=other_df['name'],
            x=other_df['waiting_time'],
            orientation='h',
            marker_color='lightgray',
            text=[f"{size:,} TEU" for size in other_df['size_teu']],
            textposition='inside',
            name='Other',
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Type: %{customdata[0]}<br>"
                "Size: %{customdata[1]:,} TEU<br>"
                "Waiting: %{x:.1f} hours"
                "<extra></extra>"
            ),
            customdata=list(zip(other_df['ship_type'], other_df['size_teu']))
        ))

    fig.update_layout(
        title="Ship Waiting Queue",
        xaxis_title="Waiting Time (hours)",
        yaxis_title="Ships",
        height=max(300, len(queue_data) * 30),
        yaxis=dict(autorange="reversed"),  # Show first in queue at top
        legend_title="Ship Type",
        showlegend=True
    )
    
    return fig


def create_berth_utilization_chart(utilization_data: Dict[int, float]) -> go.Figure:
    """Create berth utilization chart
    
    Args:
        utilization_data: Dictionary mapping berth_id to utilization percentage
    
    Returns:
        Plotly figure showing berth utilization
    """
    berth_ids = list(utilization_data.keys())
    utilizations = list(utilization_data.values())
    
    df = pd.DataFrame({
        'berth_id': berth_ids,
        'utilization': utilizations
    })

    def assign_category(u):
        if u > 80:
            return 'High (> 80%)'
        elif u > 60:
            return 'Medium (60-80%)'
        else:
            return 'Low (< 60%)'

    df['category'] = df['utilization'].apply(assign_category)

    category_colors = {
        'High (> 80%)': 'red',
        'Medium (60-80%)': 'orange',
        'Low (< 60%)': 'green'
    }

    fig = go.Figure()

    for category, color in category_colors.items():
        category_df = df[df['category'] == category]
        if not category_df.empty:
            fig.add_trace(go.Bar(
                x=[f"Berth {bid}" for bid in category_df['berth_id']],
                y=category_df['utilization'],
                marker_color=color,
                text=[f"{u:.1f}%" for u in category_df['utilization']],
                textposition='outside',
                name=category
            ))

    fig.update_layout(
        title="Berth Utilization",
        xaxis_title="Berths",
        yaxis_title="Utilization (%)",
        yaxis=dict(range=[0, 100]),
        height=400,
        legend_title="Utilization Level",
        showlegend=True
    )
    
    return fig


def create_throughput_timeline(throughput_data: pd.DataFrame) -> go.Figure:
    """Create timeline chart showing container throughput over time with seaborne/river breakdown
    
    Args:
        throughput_data: DataFrame with columns 'time', 'seaborne_teus', 'river_teus', 'total_teus'
                        OR legacy format with 'time' and 'containers_processed'
    
    Returns:
        Plotly figure showing throughput timeline with breakdown
    """
    fig = go.Figure()
    
    # Check if we have the new format with seaborne/river breakdown
    if 'seaborne_teus' in throughput_data.columns and 'river_teus' in throughput_data.columns:
        # Add seaborne throughput line
        fig.add_trace(go.Scatter(
            x=throughput_data['time'],
            y=throughput_data['seaborne_teus'],
            mode='lines+markers',
            name='Seaborne TEUs',
            line=dict(color='blue', width=2),
            marker=dict(size=6)
        ))
        
        # Add river throughput line
        fig.add_trace(go.Scatter(
            x=throughput_data['time'],
            y=throughput_data['river_teus'],
            mode='lines+markers',
            name='River TEUs',
            line=dict(color='green', width=2),
            marker=dict(size=6)
        ))
        
        # Add total throughput line if available
        if 'total_teus' in throughput_data.columns:
            fig.add_trace(go.Scatter(
                x=throughput_data['time'],
                y=throughput_data['total_teus'],
                mode='lines+markers',
                name='Total TEUs',
                line=dict(color='red', width=3, dash='dash'),
                marker=dict(size=8)
            ))
        
        title = "Container Throughput Over Time (Real Data - Seaborne vs River)"
        yaxis_title = "TEUs (Twenty-foot Equivalent Units)"
    else:
        # Fallback to legacy format
        fig.add_trace(go.Scatter(
            x=throughput_data['time'],
            y=throughput_data['containers_processed'],
            mode='lines+markers',
            name='Container Throughput',
            line=dict(color='blue', width=2),
            marker=dict(size=6)
        ))
        
        title = "Container Throughput Over Time"
        yaxis_title = "Containers Processed"
    
    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title=yaxis_title,
        height=400,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def create_waiting_time_distribution(waiting_times: List[float]) -> go.Figure:
    """Create histogram showing distribution of ship waiting times
    
    Args:
        waiting_times: List of waiting times in hours
    
    Returns:
        Plotly figure showing waiting time distribution
    """
    if not waiting_times:
        fig = go.Figure()
        fig.add_annotation(
            text="No waiting time data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        fig.update_layout(
            title="Ship Waiting Time Distribution",
            height=300,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    fig = go.Figure(data=[
        go.Histogram(
            x=waiting_times,
            nbinsx=20,
            marker_color='lightblue',
            opacity=0.7
        )
    ])
    
    # Add statistics annotations
    avg_wait = np.mean(waiting_times)
    max_wait = np.max(waiting_times)
    
    fig.add_vline(
        x=avg_wait, 
        line_dash="dash", 
        line_color="red",
        annotation_text=f"Avg: {avg_wait:.1f}h"
    )
    
    fig.update_layout(
        title="Ship Waiting Time Distribution",
        xaxis_title="Waiting Time (hours)",
        yaxis_title="Number of Ships",
        height=400
    )
    
    return fig


def create_kpi_summary_chart(kpi_data: Dict) -> go.Figure:
    """Create summary chart showing key performance indicators
    
    Args:
        kpi_data: Dictionary containing KPI values
    
    Returns:
        Plotly figure showing KPI summary
    """
    # Extract KPIs for display
    kpis = {
        'Avg Waiting Time (h)': kpi_data.get('average_waiting_time', 0),
        'Avg Berth Utilization (%)': kpi_data.get('average_berth_utilization', 0) * 100,
        'Ships Processed': kpi_data.get('total_ships_processed', 0),
        'Containers Processed': kpi_data.get('total_containers_processed', 0),
        'Avg Queue Length': kpi_data.get('average_queue_length', 0)
    }
    
    # Create subplots for different KPI types
    fig = go.Figure()
    
    # Create gauge charts for percentage-based KPIs
    if 'Avg Berth Utilization (%)' in kpis:
        utilization = kpis['Avg Berth Utilization (%)']
        color = 'red' if utilization > 80 else 'orange' if utilization > 60 else 'green'
        
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=utilization,
            domain={'x': [0, 0.5], 'y': [0.5, 1]},
            title={'text': "Berth Utilization (%)"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 60], 'color': "lightgray"},
                    {'range': [60, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
    
    # Add text annotations for other KPIs
    y_pos = 0.4
    for i, (kpi_name, value) in enumerate(kpis.items()):
        if kpi_name != 'Avg Berth Utilization (%)':
            # Ensure value is numeric for formatting
            try:
                numeric_value = float(value)
                formatted_value = f"{numeric_value:.1f}"
            except (ValueError, TypeError):
                formatted_value = str(value)
            
            fig.add_annotation(
                text=f"<b>{kpi_name}</b><br>{formatted_value}",
                xref="paper", yref="paper",
                x=0.75, y=y_pos - i * 0.08,
                xanchor='center', yanchor='middle',
                showarrow=False,
                font=dict(size=14),
                bgcolor="lightblue",
                bordercolor="blue",
                borderwidth=1
            )
    
    fig.update_layout(
        title="Key Performance Indicators",
        height=500,
        showlegend=False
    )
    
    return fig