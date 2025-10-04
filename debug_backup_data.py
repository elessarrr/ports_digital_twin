#!/usr/bin/env python3
"""
Debug script to test the load_all_vessel_data_with_backups function that Streamlit uses by default.
This helps identify why 'arriving' vessels aren't showing up in the default view.
"""

import sys
import os
sys.path.append('/Users/Bhavesh/Documents/GitHub/ports_digital_twin')

from hk_port_digital_twin.src.utils.data_loader import load_all_vessel_data_with_backups
import pandas as pd

def debug_backup_data_loading():
    """Debug the backup data loading process used by Streamlit by default"""
    print("=== Debug: Backup Data Loading (Streamlit Default) ===")
    
    # Load data exactly as Streamlit does for "Last 7 days" (default selection)
    print("\n1. Loading all vessel data with backups (as Streamlit does by default)...")
    all_vessel_data = load_all_vessel_data_with_backups(include_backups=True, max_backup_files=None)
    
    if not all_vessel_data:
        print("❌ No vessel data loaded - Dictionary is empty")
        return
    
    print(f"✅ Loaded data from {len(all_vessel_data)} sources")
    print(f"   Data sources: {list(all_vessel_data.keys())}")
    
    # Combine all data sources into a single DataFrame (as Streamlit does)
    print(f"\n2. Combining data sources...")
    vessel_dataframes = []
    for source_name, df in all_vessel_data.items():
        if not df.empty:
            print(f"   - {source_name}: {len(df)} vessels")
            df['data_source'] = source_name
            vessel_dataframes.append(df)
        else:
            print(f"   - {source_name}: EMPTY")
    
    if not vessel_dataframes:
        print("❌ No non-empty dataframes found")
        return
    
    # Concatenate as Streamlit does
    vessel_data = pd.concat(vessel_dataframes, ignore_index=True)
    print(f"\n3. Combined data: {len(vessel_data)} total vessels")
    
    # Check status column
    if 'status' not in vessel_data.columns:
        print("❌ No 'status' column found in combined vessel data")
        print(f"Available columns: {list(vessel_data.columns)}")
        return
    
    # Status breakdown
    print(f"\n4. Status breakdown in combined data:")
    status_counts = vessel_data['status'].value_counts()
    for status, count in status_counts.items():
        print(f"   {status}: {count}")
    
    # Check for arriving vessels specifically
    arriving_vessels = vessel_data[vessel_data['status'] == 'arriving']
    print(f"\n5. Arriving vessels check:")
    print(f"   Found {len(arriving_vessels)} arriving vessels")
    
    if len(arriving_vessels) > 0:
        print(f"   Sample arriving vessels:")
        for i, (idx, vessel) in enumerate(arriving_vessels.head(3).iterrows()):
            print(f"     - {vessel.get('vessel_name', 'Unknown')}: {vessel.get('status', 'No status')} (source: {vessel.get('data_source', 'Unknown')})")
    
    # Check unique statuses
    print(f"\n6. All unique statuses in combined data:")
    unique_statuses = sorted(vessel_data['status'].unique())
    print(f"   {unique_statuses}")
    
    return vessel_data

if __name__ == "__main__":
    debug_backup_data_loading()