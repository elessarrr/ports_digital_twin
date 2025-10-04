#!/usr/bin/env python3
"""
Debug script to test the exact data loading that Streamlit uses.
This helps identify if there's a difference between the data loading in isolation vs in Streamlit.
"""

import sys
import os
sys.path.append('/Users/Bhavesh/Documents/GitHub/ports_digital_twin')

from hk_port_digital_twin.src.utils.data_loader import load_combined_vessel_data

def debug_streamlit_data_loading():
    """Debug the exact data loading process used by Streamlit"""
    print("=== Debug: Streamlit Data Loading ===")
    
    # Load data exactly as Streamlit does
    print("\n1. Loading combined vessel data (as Streamlit does)...")
    vessel_data = load_combined_vessel_data()
    
    if vessel_data.empty:
        print("❌ No vessel data loaded - DataFrame is empty")
        return
    
    print(f"✅ Loaded {len(vessel_data)} vessels")
    
    # Check status column
    if 'status' not in vessel_data.columns:
        print("❌ No 'status' column found in vessel data")
        print(f"Available columns: {list(vessel_data.columns)}")
        return
    
    # Status breakdown
    print(f"\n2. Status breakdown:")
    status_counts = vessel_data['status'].value_counts()
    for status, count in status_counts.items():
        print(f"   {status}: {count}")
    
    # Check for arriving vessels specifically
    arriving_vessels = vessel_data[vessel_data['status'] == 'arriving']
    print(f"\n3. Arriving vessels check:")
    print(f"   Found {len(arriving_vessels)} arriving vessels")
    
    if len(arriving_vessels) > 0:
        print(f"   Sample arriving vessels:")
        for i, (idx, vessel) in enumerate(arriving_vessels.head(3).iterrows()):
            print(f"     - {vessel.get('vessel_name', 'Unknown')}: {vessel.get('status', 'No status')}")
    
    # Check unique statuses
    print(f"\n4. All unique statuses in data:")
    unique_statuses = sorted(vessel_data['status'].unique())
    print(f"   {unique_statuses}")
    
    # Check if there are any data type issues
    print(f"\n5. Status column data type: {vessel_data['status'].dtype}")
    
    # Check for any null/NaN values in status
    null_status_count = vessel_data['status'].isnull().sum()
    print(f"   Null status values: {null_status_count}")
    
    return vessel_data

if __name__ == "__main__":
    debug_streamlit_data_loading()