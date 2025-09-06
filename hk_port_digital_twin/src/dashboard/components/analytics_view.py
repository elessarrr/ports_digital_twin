import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render_analytics_view(data, view_types=None):
    """
    Renders the analytics view, combining cargo statistics and performance metrics.

    Args:
        data (dict): A dictionary containing the data for the view.
        view_types (list, optional): List of view types to render. Defaults to None (renders all).
    """
    # If no view types specified, render all sections
    if view_types is None:
        view_types = ['cargo_statistics', 'performance_metrics']
    
    # Render sections based on view_types
    if 'cargo_statistics' in view_types:
        st.subheader("Cargo Statistics")
        _render_cargo_statistics(data)

    if 'performance_metrics' in view_types:
        st.subheader("Performance Metrics")
        _render_performance_metrics(data)

def _render_cargo_statistics(data):
    st.warning("Cargo statistics not implemented yet.")

def _render_performance_metrics(data):
    _render_performance_overview(data)
    # This is a placeholder for a layout manager
    cols = st.columns(2)
    with cols[0]:
        _render_efficiency_metrics_chart(data)
    with cols[1]:
        _render_productivity_chart(data)
    _render_kpi_dashboard(data)

def _render_performance_overview(data: dict) -> None:
    """Render performance overview metrics"""
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
            'value': f"{performance_data.get('avg_turnaround_time', 22.4):.1f} hours",
            'delta': f"-{performance_data.get('turnaround_delta', 1.2):.1f}h",
            'help': 'Average vessel turnaround time'
        },
        {
            'label': 'Berth Occupancy',
            'value': f"{performance_data.get('berth_occupancy', 78.9):.1f}%",
            'delta': f"+{performance_data.get('occupancy_delta', 4.5):.1f}%",
            'help': 'Current berth occupancy rate'
        },
        {
            'label': 'Crane Productivity',
            'value': f"{performance_data.get('crane_productivity', 32.5):.1f} moves/hr",
            'delta': f"+{performance_data.get('crane_delta', 1.8):.1f}",
            'help': 'Average crane moves per hour'
        }
    ]
    
    # This is a placeholder for a layout manager
    cols = st.columns(4)
    for i, metric in enumerate(metrics):
        with cols[i]:
            st.metric(label=metric['label'], value=metric['value'], delta=metric['delta'], help=metric['help'])

def _render_efficiency_metrics_chart(data: dict) -> None:
    """Render efficiency metrics chart"""
    efficiency_data = data.get('efficiency_data', pd.DataFrame({
        'date': pd.to_datetime(['2023-10-01', '2023-10-02', '2023-10-03']),
        'efficiency': [85, 88, 86]
    }))
    
    if not efficiency_data.empty:
        fig = px.line(efficiency_data, x='date', y='efficiency', title='Efficiency Over Time')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No efficiency data available.")

def _render_productivity_chart(data: dict) -> None:
    """Render productivity chart"""
    productivity_data = data.get('productivity_data', pd.DataFrame({
        'date': pd.to_datetime(['2023-10-01', '2023-10-02', '2023-10-03']),
        'productivity': [30, 32, 31]
    }))

    if not productivity_data.empty:
        fig = px.bar(productivity_data, x='date', y='productivity', title='Productivity Over Time')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No productivity data available.")

def _render_kpi_dashboard(data: dict) -> None:
    """Render KPI dashboard"""
    kpi_data = data.get('kpi_data', {
        'Vessel Turnaround Time': {'value': 22.4, 'target': 24},
        'Berth Occupancy': {'value': 78.9, 'target': 85},
        'Crane Productivity': {'value': 32.5, 'target': 30}
    })

    for kpi, values in kpi_data.items():
        # Ensure progress value stays within valid range [0.0, 1.0]
        progress_value = min(1.0, max(0.0, values['value'] / values['target']))
        st.progress(progress_value, text=f"{kpi}: {values['value']}")

def _render_cargo_overview(data: dict) -> None:
    """Render cargo overview metrics"""
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
            'value': f"{data.get('avg_dwell_time', 3.2):.1f} days",
            'delta': f"-{data.get('dwell_delta', 0.3):.1f}",
            'help': 'Average cargo dwell time in port'
        }
    ]
    
    # This is a placeholder for a layout manager
    cols = st.columns(4)
    for i, metric in enumerate(metrics):
        with cols[i]:
            st.metric(label=metric['label'], value=metric['value'], delta=metric['delta'], help=metric['help'])

def _render_cargo_types_chart(data: dict) -> None:
    """Render cargo types distribution chart"""
    cargo_types_data = data.get('cargo_types', {
        'Refrigerated': 45000,
        'Dry Cargo': 35000,
        'Hazardous': 12000,
        'Out of Gauge': 6000
    })
    
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
        height=400,
        margin=dict(t=40, b=40, l=40, r=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def _render_transport_modes_chart(data: dict) -> None:
    """Render transport modes chart"""
    transport_data = data.get('transport_modes', {
        'Truck': 65000,
        'Rail': 25000,
        'Barge': 10000
    })
    
    if transport_data:
        df = pd.DataFrame(list(transport_data.items()), columns=['Mode', 'Volume'])
        
        fig = px.bar(
            df,
            x='Mode',
            y='Volume',
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

def _render_cargo_details_table(data: dict) -> None:
    """Render detailed cargo statistics table"""
    cargo_details = data.get('cargo_details', pd.DataFrame({
        'date': pd.to_datetime(['2023-10-01', '2023-10-02', '2023-10-03']),
        'cargo_type': ['Refrigerated', 'Dry Cargo', 'Refrigerated'],
        'terminal': ['CT1', 'CT2', 'CT1'],
        'volume': [100, 200, 150]
    }))
    
    if not cargo_details.empty:
        st.dataframe(cargo_details, use_container_width=True)
    else:
        st.info("No cargo details available")