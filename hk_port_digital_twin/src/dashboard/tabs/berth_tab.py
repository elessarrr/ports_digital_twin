import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

def render():
    """Renders the Berth Planning tab."""
    st.subheader("🏗️ Berth Utilization Analysis")

    # Sample data for demonstration
    st.info("📊 Using sample data - Start simulation for real-time berth data")

    # Generate scenario-aware sample berth data
    berth_utilization = 75  # Example utilization
    throughput_base = 50000 # Example throughput

    berth_statuses = ['occupied', 'available', 'maintenance']
    status_probs = [0.6, 0.35, 0.05]

    sample_berths = []
    for i in range(1, 21):  # 20 berths
        status = np.random.choice(berth_statuses, p=status_probs)

        utilization = np.random.normal(berth_utilization, berth_utilization * 0.15)
        utilization = max(0, min(utilization, 100))

        berth_throughput = int(np.random.normal(throughput_base / 20, throughput_base / 40))
        berth_throughput = max(0, berth_throughput)

        sample_berths.append({
            'berth_id': f'B{i:02d}',
            'status': status,
            'current_ship': f'SHIP-{np.random.randint(100, 999)}' if status == 'occupied' else None,
            'utilization': utilization,
            'throughput': berth_throughput,
            'last_updated': datetime.now().strftime('%H:%M:%S')
        })

    # Sample metrics
    berth_col1, berth_col2, berth_col3, berth_col4 = st.columns(4)
    with berth_col1:
        occupied_berths = sum(1 for berth in sample_berths if berth['status'] == 'occupied')
        st.metric("Occupied Berths", f"{occupied_berths}/{len(sample_berths)}")
    with berth_col2:
        avg_utilization = sum(berth['utilization'] for berth in sample_berths) / len(sample_berths)
        st.metric("Avg Utilization", f"{avg_utilization:.1f}%")
    with berth_col3:
        maintenance_berths = sum(1 for berth in sample_berths if berth['status'] == 'maintenance')
        st.metric("Under Maintenance", maintenance_berths)
    with berth_col4:
        total_throughput = sum(berth['throughput'] for berth in sample_berths)
        st.metric("Total Throughput", f"{total_throughput:,.0f} TEU")

    # Sample visualization
    berth_df = pd.DataFrame(sample_berths)

    fig_berth = px.bar(
        berth_df,
        x='berth_id',
        y='utilization',
        color='status',
        title='Berth Utilization by Status (Sample Data)',
        labels={'utilization': 'Utilization (%)', 'berth_id': 'Berth ID'}
    )
    st.plotly_chart(fig_berth, use_container_width=True)

    # Sample berth table
    st.subheader("📋 Berth Status Details")
    st.dataframe(berth_df, use_container_width=True)