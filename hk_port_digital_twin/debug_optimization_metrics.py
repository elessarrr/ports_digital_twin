#!/usr/bin/env python3
"""
Debug script to investigate optimization metrics
This script manually triggers the optimization process and logs detailed metrics
to understand why the objective value is showing as 1.00 (theoretical minimum).
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ai.optimization import BerthAllocationOptimizer, ScenarioWeights, OptimizationConstraints, Ship, Berth
from src.utils.data_loader import load_berth_configurations, load_vessel_arrivals
from datetime import datetime
import logging

# Configure logging to file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_optimization_metrics.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def debug_optimization_metrics():
    """Debug the optimization metrics calculation"""
    try:
        logger.info("=== OPTIMIZATION METRICS DEBUG SESSION ===")
        
        # Load data
        logger.info("Loading berth and vessel data...")
        berth_data = load_berth_configurations()
        vessel_data = load_vessel_arrivals()
        
        # Define test scenario weights (same as default)
        scenario_weights = ScenarioWeights(
            normal=0.4,
            peak_season=0.3,
            maintenance=0.2,
            typhoon_season=0.1
        )
        
        constraints = OptimizationConstraints(
            max_berths=20,
            max_cranes=40,
            budget=10000.0  # Updated to match the new default
        )
        
        # Initialize optimization engine
        logger.info("Initializing optimization engine...")
        optimizer = BerthAllocationOptimizer(
            scenario_weights=scenario_weights,
            constraints=constraints
        )
        
        logger.info(f"Loaded {len(berth_data)} berth records")
        logger.info(f"Loaded {len(vessel_data)} vessel records")
        
        # Convert data to Ship and Berth objects
        logger.info("Converting data to optimization objects...")
        
        # Create berths list
        berths = []
        for berth_config in berth_data:
            berth = Berth(
                id=str(berth_config.get('berth_id', 'unknown')),
                capacity=float(berth_config.get('max_capacity_teu', 50000)),
                crane_count=int(berth_config.get('crane_count', 4)),
                suitable_ship_types=['container', 'bulk', 'general'],
                is_available=True
            )
            berths.append(berth)
        
        # Create ships list (use a subset for testing)
        ships = []
        ship_count = 0
        for _, vessel_row in vessel_data.head(10).iterrows():  # Test with first 10 vessels
            try:
                arrival_time = vessel_row.get('arrival_time', datetime.now())
                if isinstance(arrival_time, str):
                    arrival_time = datetime.fromisoformat(arrival_time.replace('Z', '+00:00'))
                
                ship = Ship(
                    id=str(vessel_row.get('call_sign', f'ship_{ship_count}')),
                    arrival_time=arrival_time,
                    ship_type=str(vessel_row.get('ship_category', 'container')).lower(),
                    size=20000.0,  # Fixed reasonable size since not in data
                    priority=1,
                    estimated_service_time=8.0,  # Fixed reasonable time since not in data
                    containers_to_load=100,  # Fixed reasonable number since not in data
                    containers_to_unload=150  # Fixed reasonable number since not in data
                )
                ships.append(ship)
                ship_count += 1
            except Exception as e:
                logger.warning(f"Skipping vessel due to data issue: {e}")
        
        # Add ships and berths to optimizer
        logger.info(f"Adding {len(ships)} ships to optimizer...")
        for ship in ships:
            optimizer.add_ship(ship)
        
        logger.info(f"Adding {len(berths)} berths to optimizer...")
        for berth in berths:
            optimizer.add_berth(berth)
        
        logger.info(f"Using scenario weights: {scenario_weights}")
        logger.info(f"Using constraints: {constraints}")
        
        # Run optimization
        logger.info("Running optimization...")
        result = optimizer.optimize_berth_allocation()
        
        logger.info("=== OPTIMIZATION RESULTS ===")
        logger.info(f"Optimization Score: {result.optimization_score}")
        logger.info(f"Total Waiting Time: {result.total_waiting_time}")
        logger.info(f"Average Waiting Time: {result.average_waiting_time}")
        logger.info(f"Ship-Berth Assignments: {len(result.ship_berth_assignments)}")
        
        # Log berth utilization details
        logger.info("=== BERTH UTILIZATION ===")
        for berth_id, utilization in result.berth_utilization.items():
            logger.info(f"  {berth_id}: {utilization:.2%}")
        
        # Log scenario performance details if available
        if result.scenario_performance:
            logger.info("=== SCENARIO PERFORMANCE DETAILS ===")
            for scenario, performance in result.scenario_performance.items():
                logger.info(f"{scenario.upper()}:")
                if isinstance(performance, dict):
                    for metric, value in performance.items():
                        logger.info(f"  {metric}: {value}")
                else:
                    logger.info(f"  Performance: {performance}")
        
        logger.info("=== DEBUG SESSION COMPLETE ===")
        
    except Exception as e:
        logger.error(f"Error during optimization debug: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    debug_optimization_metrics()