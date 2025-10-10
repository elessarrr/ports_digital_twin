"""Sample Data Generator for Hong Kong Port Digital Twin

This module generates realistic sample data for development and testing.
Use this when real APIs are unavailable or for offline development.
"""

import os
import pandas as pd
from datetime import datetime, timedelta


def generate_sample_vessel_data(num_records: int = 100) -> pd.DataFrame:
    """Generate a DataFrame of sample vessel data."""
    data = {
        'vessel_name': [f'Vessel_{i}' for i in range(num_records)],
        'arrival_time': [datetime.now() - timedelta(hours=i) for i in range(num_records)],
        'berth_time': [datetime.now() - timedelta(hours=i, minutes=30) for i in range(num_records)],
        'departure_time': [datetime.now() - timedelta(hours=i-1) for i in range(num_records)],
        'vessel_type': ['Container Ship' if i % 2 == 0 else 'Bulk Carrier' for i in range(num_records)],
        'port_of_origin': ['Shanghai' if i % 2 == 0 else 'Singapore' for i in range(num_records)],
        'destination_port': ['Rotterdam' if i % 2 == 0 else 'Los Angeles' for i in range(num_records)],
    }
    return pd.DataFrame(data)


def save_sample_data(df: pd.DataFrame, file_path: str):
    """Save the sample data to a CSV file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_csv(file_path, index=False)


if __name__ == "__main__":
    # Define the output directory and file path
    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')
    file_path = os.path.join(output_dir, 'sample_vessel_data.csv')

    # Generate and save the sample data
    sample_df = generate_sample_vessel_data()
    save_sample_data(sample_df, file_path)