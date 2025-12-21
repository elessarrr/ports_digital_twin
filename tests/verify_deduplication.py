import pandas as pd
import logging
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import data loader
try:
    from hk_port_digital_twin.src.utils.data_loader import load_combined_vessel_data, HISTORICAL_DATA_FILE
except ImportError:
    # Try alternate path
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../hk_port_digital_twin')))
    from src.utils.data_loader import load_combined_vessel_data, HISTORICAL_DATA_FILE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_deduplication():
    print("\n=== Verifying Deduplication and Historical Data Integration ===\n")
    
    # 1. Check Historical CSV
    print(f"Checking historical file: {HISTORICAL_DATA_FILE}")
    if not HISTORICAL_DATA_FILE.exists():
        print("ERROR: Historical data file not found!")
        return
    
    hist_df = pd.read_csv(HISTORICAL_DATA_FILE)
    raw_count = len(hist_df)
    print(f"Raw rows in historical CSV: {raw_count}")
    
    # Check for 'nan' timestamps in CSV
    if 'ARRIVAL_TIME' in hist_df.columns:
        nan_arrivals = hist_df['ARRIVAL_TIME'].isna().sum()
        print(f"Rows with NaN ARRIVAL_TIME in CSV: {nan_arrivals}")
        
        # Estimate unique visits in CSV
        # Using VESSEL_NAME + ARRIVAL_TIME as key
        unique_visits = hist_df.drop_duplicates(subset=['VESSEL_NAME', 'ARRIVAL_TIME']).shape[0]
        print(f"Estimated unique visits (VESSEL_NAME + ARRIVAL_TIME) in CSV: {unique_visits}")
        
        est_reduction = raw_count - unique_visits
        print(f"Expected reduction from deduplication: {est_reduction} rows ({est_reduction/raw_count*100:.1f}%)")
    
    # 2. Load Combined Data
    print("\nLoading combined vessel data...")
    combined_df = load_combined_vessel_data()
    
    loaded_count = len(combined_df)
    print(f"Total rows in combined dataframe: {loaded_count}")
    
    # 3. Analyze Sources
    if 'data_source' in combined_df.columns:
        print("\nBreakdown by Data Source:")
        print(combined_df['data_source'].value_counts())
    else:
        print("\nWARNING: 'data_source' column missing in combined dataframe")
        
    # 4. Analyze Status
    if 'status' in combined_df.columns:
        print("\nBreakdown by Status:")
        print(combined_df['status'].value_counts())

    # 5. Check Date Range
    if 'arrival_time' in combined_df.columns and not combined_df.empty:
        min_date = combined_df['arrival_time'].min()
        max_date = combined_df['arrival_time'].max()
        print(f"\nDate Range: {min_date} to {max_date}")
        
        # Check distribution by year
        combined_df['year'] = combined_df['arrival_time'].apply(lambda x: x.year if pd.notna(x) else 'Unknown')
        print("\nDistribution by Year:")
        print(combined_df['year'].value_counts().sort_index())
    
    # 6. Verify specific historical vessels
    # Check if we have data from 2011, 2014, etc.
    historical_years = [2011, 2014, 2016, 2018]
    print("\nVerifying historical years presence:")
    for year in historical_years:
        count = len(combined_df[combined_df['year'] == year]) if 'year' in combined_df.columns else 0
        status = "FOUND" if count > 0 else "MISSING"
        print(f"Year {year}: {status} ({count} vessels)")

    # 7. Check for potential duplicates remaining
    # If we have same vessel arriving at same time multiple times
    dupes = combined_df.duplicated(subset=['vessel_name', 'arrival_time'], keep=False)
    dupe_count = dupes.sum()
    print(f"\nRemaining duplicates (vessel_name + arrival_time): {dupe_count}")
    if dupe_count > 0:
        print("WARNING: Duplicates still exist!")
        print(combined_df[dupes][['vessel_name', 'arrival_time', 'data_source', 'status']].head())
    else:
        print("SUCCESS: No duplicates found based on vessel_name + arrival_time")

if __name__ == "__main__":
    verify_deduplication()
