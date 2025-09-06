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
    """Render comprehensive cargo statistics using real data from CSV files."""
    # Import the new cargo analysis functions
    from ...utils.data_loader import load_port_cargo_statistics, get_cargo_breakdown_analysis
    
    try:
        # Load real cargo statistics data
        cargo_analysis = get_cargo_breakdown_analysis()
        
        if 'error' in cargo_analysis:
            st.error(f"Error loading cargo statistics: {cargo_analysis['error']}")
            st.info("Please ensure the Port Cargo Statistics CSV files are available in the data/cargo_statistics directory.")
            return
        
        # Display key metrics overview
        st.subheader("📊 Key Metrics (2023)")
        
        key_metrics = cargo_analysis.get('key_metrics', {})
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_throughput = key_metrics.get('total_throughput_2023', 0)
            st.metric(
                "Total Throughput", 
                f"{total_throughput:,.0f}" if total_throughput > 1000 else f"{total_throughput:.1f}",
                help="Total port cargo throughput in 2023"
            )
        
        with col2:
            growth_rate = key_metrics.get('annual_growth_rate', 0)
            st.metric(
                "Annual Growth Rate", 
                f"{growth_rate:+.1f}%",
                delta=f"{growth_rate:.1f}%",
                help="Average annual growth rate (2014-2023)"
            )
        
        with col3:
            transhipment_ratio = key_metrics.get('transhipment_ratio', 0)
            st.metric(
                "Transhipment Ratio", 
                f"{transhipment_ratio:.1%}",
                help="Percentage of cargo that is transhipment"
            )
        
        with col4:
            seaborne_ratio = key_metrics.get('seaborne_ratio', 0)
            st.metric(
                "Seaborne Cargo", 
                f"{seaborne_ratio:.1%}",
                help="Percentage of cargo transported by sea"
            )
        
        # Create tabs for detailed analysis
        tab1, tab2 = st.tabs(["📦 Shipment Types", "🚛 Transport Modes"])
        
        with tab1:
            st.subheader("Shipment Type Analysis")
            shipment_analysis = cargo_analysis.get('shipment_type_analysis', {})
            
            if shipment_analysis:
                # Display shipment breakdown
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Direct Shipment vs Transhipment (2023)**")
                    
                    direct = shipment_analysis.get('direct_shipment_2023', {})
                    tranship = shipment_analysis.get('transhipment_2023', {})
                    
                    shipment_data = {
                        'Type': ['Direct Shipment', 'Transhipment'],
                        'Volume': [direct.get('volume', 0), tranship.get('volume', 0)],
                        'Percentage': [direct.get('percentage', 0), tranship.get('percentage', 0)]
                    }
                    
                    shipment_df = pd.DataFrame(shipment_data)
                    st.dataframe(shipment_df, use_container_width=True)
                
                with col2:
                    # Create pie chart for shipment types
                    if shipment_data['Volume'][0] > 0 or shipment_data['Volume'][1] > 0:
                        fig = go.Figure(data=[
                            go.Pie(
                                labels=shipment_data['Type'],
                                values=shipment_data['Volume'],
                                hole=0.4,
                                textinfo='label+percent',
                                textposition='outside'
                            )
                        ])
                        
                        fig.update_layout(
                            title="Shipment Type Distribution",
                            height=400,
                            margin=dict(t=40, b=40, l=40, r=40)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No shipment type data available")
        
        with tab2:
            st.subheader("Transport Mode Analysis")
            transport_analysis = cargo_analysis.get('transport_mode_analysis', {})
            
            if transport_analysis:
                # Display transport mode breakdown
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Transport Mode Distribution (2023)**")
                    
                    waterborne = transport_analysis.get('waterborne_2023', {})
                    seaborne = transport_analysis.get('seaborne_2023', {})
                    river = transport_analysis.get('river_2023', {})
                    
                    transport_data = {
                        'Mode': ['Waterborne', 'Seaborne', 'River'],
                        'Volume': [waterborne.get('volume', 0), seaborne.get('volume', 0), river.get('volume', 0)],
                        'Percentage': [waterborne.get('percentage', 0), seaborne.get('percentage', 0), river.get('percentage', 0)]
                    }
                    
                    transport_df = pd.DataFrame(transport_data)
                    st.dataframe(transport_df, use_container_width=True)
                
                with col2:
                    # Create bar chart for transport modes
                    if any(vol > 0 for vol in transport_data['Volume']):
                        fig = px.bar(
                            transport_df,
                            x='Mode',
                            y='Volume',
                            color='Volume',
                            color_continuous_scale='viridis',
                            title="Volume by Transport Mode"
                        )
                        
                        fig.update_layout(
                            height=400,
                            margin=dict(t=40, b=40, l=40, r=40),
                            xaxis_title="Transport Mode",
                            yaxis_title="Volume"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No transport mode data available")
        
    except Exception as e:
        st.error(f"Error rendering cargo statistics: {str(e)}")
        st.info("Please ensure the data loader module is properly configured and CSV files are available.")

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