import os
import sys
import pandas as pd
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from hk_port_digital_twin.src.utils.data_loader import load_combined_vessel_data, get_comprehensive_vessel_analysis
from hk_port_digital_twin.src.dashboard.executive_dashboard import ExecutiveDashboard

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_historical_integration():
    logger.info("Starting verification of historical data integration...")
    
    # 1. Test Data Loading
    logger.info("1. Testing load_combined_vessel_data()...")
    df = load_combined_vessel_data()
    
    if df.empty:
        logger.error("❌ load_combined_vessel_data returned empty DataFrame")
        return
    
    logger.info(f"✅ Loaded {len(df)} vessels")
    
    # Check for historical data source
    if 'data_source' in df.columns:
        sources = df['data_source'].unique()
        logger.info(f"Data sources found: {sources}")
        if 'historical_archive' in sources:
            logger.info("✅ Historical data source present")
            hist_count = len(df[df['data_source'] == 'historical_archive'])
            logger.info(f"   - {hist_count} historical records")
        else:
            logger.warning("⚠️ 'historical_archive' source NOT found (might be expected if CSV is empty or not created yet)")
    
    # 2. Check Deduplication
    logger.info("2. Checking for duplicates (Call Sign + Vessel Name)...")
    duplicates = df[df.duplicated(subset=['call_sign', 'vessel_name'], keep=False)]
    if not duplicates.empty:
        logger.warning(f"⚠️ Found {len(duplicates)} potential duplicates (might be valid if different arrival times)")
        # Check strict duplicates (same arrival time)
        strict_dupes = df[df.duplicated(subset=['call_sign', 'vessel_name', 'arrival_time'], keep=False)]
        if not strict_dupes.empty:
            logger.error(f"❌ Found {len(strict_dupes)} STRICT duplicates (same vessel, same arrival time)")
            print(strict_dupes[['call_sign', 'vessel_name', 'arrival_time', 'data_source']].head())
        else:
            logger.info("✅ No strict duplicates found")
    else:
        logger.info("✅ No duplicates found")

    # 3. Test Comprehensive Analysis
    logger.info("3. Testing get_comprehensive_vessel_analysis()...")
    analysis = get_comprehensive_vessel_analysis(include_historical_data=True)
    
    if not analysis:
        logger.error("❌ get_comprehensive_vessel_analysis returned empty dict")
    else:
        logger.info("✅ Comprehensive analysis returned data")
        if 'activity_trend' in analysis:
            logger.info(f"✅ Activity trend has {len(analysis['activity_trend'])} data points")
        else:
            logger.warning("⚠️ No activity_trend in analysis")

    # 4. Test Executive Dashboard Metrics
    logger.info("4. Testing ExecutiveDashboard metrics calculation...")
    dashboard = ExecutiveDashboard()
    metrics = dashboard.calculate_metrics_from_vessel_data(df)
    
    logger.info("Calculated Metrics:")
    logger.info(f" - Revenue/Hour: ${metrics.revenue_per_hour:,.2f}")
    logger.info(f" - Efficiency Improvement: {metrics.efficiency_improvement:.2f}%")
    logger.info(f" - Capacity Utilization: {metrics.capacity_utilization:.2f}%")
    
    if metrics.revenue_per_hour > 0:
        logger.info("✅ Metrics calculated successfully")
    else:
        logger.warning("⚠️ Metrics seem low/zero")

if __name__ == "__main__":
    verify_historical_integration()
