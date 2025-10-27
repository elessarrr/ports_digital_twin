import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def render():
    st.subheader("Vessel Analytics")

    # Mock data for demonstration
    vessel_data = {
        'vessel_name': [f'Vessel {i}' for i in range(1, 21)],
        'arrival_time': [datetime.now() - timedelta(hours=i*2) for i in range(20)],
        'departure_time': [datetime.now() - timedelta(hours=i*2) + timedelta(hours=10) for i in range(20)],
        'status': ['Departed'] * 10 + ['At Berth'] * 5 + ['Anchored'] * 5,
        'cargo_volume': [i * 100 for i in range(1, 21)],
        'vessel_type': ['Container Ship'] * 10 + ['Bulk Carrier'] * 5 + ['Tanker'] * 5
    }
    df = pd.DataFrame(vessel_data)

    # Vessel tracking and status
    st.subheader("Live Vessel Tracking")
    st.map(pd.DataFrame({
        'lat': [22.30, 22.32, 22.28],
        'lon': [114.17, 114.15, 114.19],
    }))

    # Vessel details table
    st.subheader("Vessel Details")
    st.dataframe(df)

    # Analytics and charts
    st.subheader("Vessel Performance Analytics")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Average Turnaround Time", "12 hours")
        st.bar_chart(df.groupby('vessel_type')['cargo_volume'].sum())

    with col2:
        st.metric("Vessels in Port", "10")
        st.line_chart(df.set_index('arrival_time')['cargo_volume'])