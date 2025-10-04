import pandas as pd
import os
import sys
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from hk_port_digital_twin.src.utils.data_loader import load_combined_vessel_data

def verify_dashboard_fix():
    print("Loading combined vessel data...")
    combined_df = load_combined_vessel_data()

    if combined_df.empty:
        print("No vessel data loaded. The DataFrame is empty.")
        return

    print(f"Successfully loaded {len(combined_df)} vessels.")

    # Check for the presence of 'timestamp' or 'arrival_time' column
    time_column = None
    if 'arrival_time' in combined_df.columns:
        time_column = 'arrival_time'
    elif 'timestamp' in combined_df.columns:
        time_column = 'timestamp'

    if time_column:
        print(f"Identified time column: {time_column}")
        # Ensure the time column is in datetime format
        combined_df[time_column] = pd.to_datetime(combined_df[time_column], errors='coerce')
        combined_df.dropna(subset=[time_column], inplace=True)

        if combined_df.empty:
            print(f"No valid timestamps found in the '{time_column}' column after conversion.")
            return

        # Filter for vessels within the last 3 days
        three_days_ago = datetime.now() - timedelta(days=3)
        recent_vessels_df = combined_df[combined_df[time_column] >= three_days_ago]

        if not recent_vessels_df.empty:
            print(f"Found {len(recent_vessels_df)} vessels in the last 3 days.")
            print("Recent vessels data:")
            print(recent_vessels_df[['vessel_name', time_column]].head())
        else:
            print("No vessels found in the last 3 days.")
            most_recent_data = combined_df[time_column].max()
            if pd.notna(most_recent_data):
                days_old = (datetime.now() - most_recent_data).days
                print(f"Most recent vessel data is {days_old} days old ({most_recent_data.strftime('%Y-%m-%d %H:%M')}).")
            else:
                print("Could not determine the age of the most recent data.")
    else:
        print("Neither 'timestamp' nor 'arrival_time' column found in the data.")

if __name__ == "__main__":
    verify_dashboard_fix()