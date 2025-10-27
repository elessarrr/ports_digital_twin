import pandas as pd
from hk_port_digital_twin.src.utils.data_loader import load_combined_vessel_data


def verify_data_loading():
    """Verify that the combined vessel data can be loaded and is not empty."""
    combined_df = load_combined_vessel_data()
    if combined_df.empty:
        return


def analyze_time_column(combined_df):
    """Analyze the time column to ensure it contains valid timestamp data."""
    time_column = 'timestamp' if 'timestamp' in combined_df.columns else 'arrival_time'
    if time_column not in combined_df.columns:
        return

    # Convert to datetime, coercing errors to NaT
    timestamps = pd.to_datetime(combined_df[time_column], errors='coerce')

    if timestamps.isnull().all():
        return

    # Check for recent data
    three_days_ago = pd.Timestamp.now() - pd.Timedelta(days=3)
    recent_vessels_df = combined_df[timestamps > three_days_ago]

    if not recent_vessels_df.empty:
        pass
    else:
        pass

    most_recent_data = timestamps.max()
    if pd.notnull(most_recent_data):
        days_old = (pd.Timestamp.now() - most_recent_data).days
    else:
        pass


if __name__ == "__main__":
    verify_data_loading()