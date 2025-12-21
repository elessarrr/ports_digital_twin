
import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hk_port_digital_twin.src.utils.data_loader import load_combined_vessel_data

# Mocking streamlit_app functions since we can't easily import from the script without side effects
def filter_vessel_data_by_time_range(vessel_data: pd.DataFrame, time_range: str) -> pd.DataFrame:
    if vessel_data.empty:
        return vessel_data
    
    # Determine the time column to use for filtering
    time_column = None
    if 'arrival_time' in vessel_data.columns:
        time_column = 'arrival_time'
    elif 'timestamp' in vessel_data.columns:
        time_column = 'timestamp'
    elif 'departure_time' in vessel_data.columns:
        time_column = 'departure_time'
    
    if time_column is None:
        return vessel_data
    
    # Ensure the time column is in datetime format
    vessel_data[time_column] = pd.to_datetime(vessel_data[time_column], errors='coerce')
    
    # Determine anchor date (handle historical data)
    now = datetime.now()
    max_date = vessel_data[time_column].max()
    
    # Anchor date logic
    if pd.notna(max_date) and max_date < now - timedelta(days=2):
        anchor_date = max_date
        print(f"Using historical anchor date: {anchor_date}")
    else:
        anchor_date = now
    
    if time_range == 'Last 7 days':
        cutoff_date = anchor_date - timedelta(days=7)
    elif time_range == 'Last 30 days':
        cutoff_date = anchor_date - timedelta(days=30)
    elif time_range == 'Last 1 year':
        cutoff_date = anchor_date - timedelta(days=365)
    elif time_range == 'All historical data':
        return vessel_data
    else:
        return vessel_data
    
    # Filter the data
    filtered_data = vessel_data[
        (vessel_data[time_column].notna()) & 
        (vessel_data[time_column] >= cutoff_date)
    ].copy()
    
    return filtered_data

def get_recent_vessel_counts(vessel_data):
    if vessel_data is None or vessel_data.empty:
        return {'arriving': 0, 'departing': 0, 'in_port': 0}
    
    # Get the most recent date in the data
    time_col = None
    if 'timestamp' in vessel_data.columns:
        time_col = 'timestamp'
    elif 'arrival_time' in vessel_data.columns:
        time_col = 'arrival_time'
        
    if time_col:
        vessel_data[time_col] = pd.to_datetime(vessel_data[time_col], errors='coerce')
        most_recent_date = vessel_data[time_col].max()
        
        if pd.notna(most_recent_date):
            # Filter to last 24 hours from the most recent date
            cutoff_time = most_recent_date - timedelta(hours=24)
            recent_data = vessel_data[vessel_data[time_col] >= cutoff_time]
        else:
            recent_data = vessel_data
    else:
        recent_data = vessel_data
    
    # Count vessels by status
    if 'status' in recent_data.columns:
        status_counts = recent_data['status'].value_counts()
        return {
            'arriving': int(status_counts.get('arriving', 0)),
            'departing': int(status_counts.get('departing', 0) + status_counts.get('departed', 0)),
            'in_port': int(status_counts.get('in_port', 0))
        }
    return {'arriving': 0, 'departing': 0, 'in_port': 0}

def main():
    print("Loading combined vessel data...")
    data = load_combined_vessel_data()
    
    if data is None or data.empty:
        print("ERROR: No data loaded.")
        return
    
    print(f"Total records loaded: {len(data)}")
    
    # Check date range
    if 'timestamp' in data.columns:
        min_date = pd.to_datetime(data['timestamp']).min()
        max_date = pd.to_datetime(data['timestamp']).max()
        print(f"Data range: {min_date} to {max_date}")
    
    # Test 1: Recent Counts (Overview Tab logic)
    print("\nTest 1: Recent Vessel Counts (Overview Tab)")
    counts = get_recent_vessel_counts(data)
    print(f"Recent counts: {counts}")
    if counts['arriving'] + counts['in_port'] + counts['departing'] == 0:
        print("WARNING: Zero counts for recent activity.")
    else:
        print("SUCCESS: Retrieved recent counts.")

    # Test 2: Filter Last 30 Days (Vessel Insights Tab logic)
    print("\nTest 2: Filter Last 30 Days")
    filtered_30 = filter_vessel_data_by_time_range(data.copy(), 'Last 30 days')
    print(f"Records in last 30 days: {len(filtered_30)}")
    
    # Test 3: Filter Last 1 Year
    print("\nTest 3: Filter Last 1 Year")
    filtered_year = filter_vessel_data_by_time_range(data.copy(), 'Last 1 year')
    print(f"Records in last 1 year: {len(filtered_year)}")
    
    # Test 4: All Historical Data
    print("\nTest 4: All Historical Data")
    all_hist = filter_vessel_data_by_time_range(data.copy(), 'All historical data')
    print(f"Records in all history: {len(all_hist)}")
    
    if len(all_hist) >= len(filtered_year) >= len(filtered_30):
        print("SUCCESS: Filtering logic works as expected (All >= Year >= 30 Days).")
    else:
        print("ERROR: Filtering logic mismatch.")

if __name__ == "__main__":
    main()
