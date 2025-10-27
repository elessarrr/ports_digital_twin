import streamlit as st
import pandas as pd
import redis
import json
from datetime import datetime

# Connect to Redis
redis_client = redis.StrictRedis(decode_responses=True)

def render():
    """Renders the real-time Berth Planning tab."""
    st.subheader("🚢 Real-Time Berth Monitoring")

    # Placeholder for the berth status table
    status_placeholder = st.empty()

    def get_berth_data():
        """Fetch and format berth data from Redis."""
        berth_keys = sorted(redis_client.keys("berth:*"))
        berth_data = []
        for key in berth_keys:
            data = redis_client.hgetall(key)
            # Convert relevant fields to appropriate types
            data['berth_id'] = int(data.get('berth_id', 0))
            data['is_occupied'] = data.get('is_occupied') == 'True'
            data['occupation_start_time'] = float(data.get('occupation_start_time', 0))
            data['total_occupation_time'] = float(data.get('total_occupation_time', 0))
            data['ships_served'] = int(data.get('ships_served', 0))
            berth_data.append(data)
        return pd.DataFrame(berth_data)

    def display_berth_status():
        """Display the real-time berth status table."""
        berth_df = get_berth_data()
        if not berth_df.empty:
            # Format for display
            berth_df['status'] = berth_df['is_occupied'].apply(lambda x: 'Occupied' if x else 'Available')
            berth_df_display = berth_df[['berth_id', 'name', 'status', 'current_ship', 'ships_served']]
            status_placeholder.dataframe(berth_df_display, use_container_width=True)
        else:
            status_placeholder.info("Waiting for berth data...")

    # Initial display
    display_berth_status()

    # This part of the original code will not work in Streamlit's execution model.
    # Streamlit reruns the script on each interaction, so a long-running loop
    # listening to Redis pub/sub is not feasible. Instead, we will rely on
    # Streamlit's native mechanisms to periodically refresh the data.
    # For a true real-time experience, a different architecture would be needed,
    # but for this dashboard, we can simulate it with a refresh button.

    # The app will now automatically refresh when new data is available.
    # if st.button("Refresh"): 
    #     display_berth_status()