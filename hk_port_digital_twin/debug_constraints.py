#!/usr/bin/env python3
"""
Constraint Debug Script
This script focuses on identifying specific constraint violations
that prevent ship-berth assignments.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ai.optimization import BerthAllocationOptimizer, ScenarioWeights, OptimizationConstraints, Ship, Berth
from src.utils.data_loader import load_berth_configurations, load_vessel_arrivals
from datetime import datetime
import logging
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_constraints():
    """Debug constraint violations in detail"""
    try:
        logger.info("=== CONSTRAINT DEBUG SESSION ===")
        
        # Load data
        berth_data = load_berth_configurations()
        vessel_data = load_vessel_arrivals()
        
        # Create a simple test case with relaxed constraints
        constraints = OptimizationConstraints(
            max_berths=50,    # Increased from 20
            max_cranes=200,   # Increased from 40
            budget=10000.0    # Increased from 1000.0
        )
        
        scenario_weights = ScenarioWeights()
        optimizer = BerthAllocationOptimizer(scenario_weights, constraints)
        
        # Create one test ship
        test_ship = Ship(
            id="TEST_SHIP",
            arrival_time=datetime.now(),
            ship_type="container",
            size=15000.0,  # 15k TEU
            priority=1,
            estimated_service_time=8.0,
            containers_to_load=100,
            containers_to_unload=150
        )
        
        # Create one test berth
        test_berth = Berth(
            id="TEST_BERTH",
            capacity=20000.0,  # 20k TEU capacity
            crane_count=8,
            suitable_ship_types=[],  # Accept all types
            is_available=True
        )
        
        logger.info(f"Test ship: {test_ship}")
        logger.info(f"Test berth: {test_berth}")
        logger.info(f"Constraints: {constraints}")
        
        # Test basic compatibility
        is_suitable = optimizer.is_berth_suitable(test_ship, test_berth)
        logger.info(f"Is berth suitable for ship? {is_suitable}")
        
        # Test service time estimation
        service_time = optimizer.estimate_service_time(test_ship, test_berth)
        logger.info(f"Estimated service time: {service_time} hours")
        
        # Calculate costs manually
        berth_cost = 50.0 * service_time  # 50k HKD per hour
        crane_cost = 20.0 * test_berth.crane_count * service_time  # 20k HKD per crane per hour
        total_cost = berth_cost + crane_cost
        logger.info(f"Berth cost: {berth_cost} HKD")
        logger.info(f"Crane cost: {crane_cost} HKD")
        logger.info(f"Total assignment cost: {total_cost} HKD")
        logger.info(f"Budget available: {constraints.budget} HKD")
        logger.info(f"Cost within budget? {total_cost <= constraints.budget}")
        
        # Add to optimizer and test
        optimizer.add_ship(test_ship)
        optimizer.add_berth(test_berth)
        
        logger.info("Running optimization with single ship and berth...")
        result = optimizer.optimize_berth_allocation()
        
        logger.info(f"Assignments: {result.ship_berth_assignments}")
        logger.info(f"Success: {len(result.ship_berth_assignments) > 0}")
        
        if len(result.ship_berth_assignments) == 0:
            logger.error("FAILED: Even simple test case failed!")
        else:
            logger.info("SUCCESS: Simple test case worked!")
            
            # Now test with real data but relaxed constraints
            logger.info("Testing with real data and relaxed constraints...")
            optimizer.clear()
            
            # Add real berths
            for i, berth_config in enumerate(berth_data[:5]):  # First 5 berths
                berth_id = str(berth_config.get('berth_id', f'berth_{i+1}'))
                capacity = float(berth_config.get('max_capacity_teu', 50000))
                crane_count = int(berth_config.get('crane_count', 2))
                
                berth = Berth(
                    id=berth_id,
                    capacity=capacity,
                    crane_count=crane_count,
                    suitable_ship_types=[],  # Accept all types
                    is_available=True
                )
                optimizer.add_berth(berth)
                logger.info(f"Added berth {berth_id}: capacity={capacity}, cranes={crane_count}")
            
            # Add real ships
            for i, (_, vessel_row) in enumerate(vessel_data.head(3).iterrows()):  # First 3 ships
                ship_id = str(vessel_row.get('call_sign', f'ship_{i+1}'))
                arrival_time = vessel_row.get('arrival_time', datetime.now())
                if pd.isna(arrival_time) or arrival_time is None:
                    arrival_time = datetime.now()
                
                ship_type = str(vessel_row.get('ship_type', 'container')).lower().strip()
                size = 15000.0  # Fixed reasonable size
                
                ship = Ship(
                    id=ship_id,
                    arrival_time=arrival_time,
                    ship_type=ship_type,
                    size=size,
                    priority=1,
                    estimated_service_time=8.0,
                    containers_to_load=100,
                    containers_to_unload=150
                )
                optimizer.add_ship(ship)
                logger.info(f"Added ship {ship_id}: type={ship_type}, size={size}")
            
            result = optimizer.optimize_berth_allocation()
            logger.info(f"Real data assignments: {result.ship_berth_assignments}")
            logger.info(f"Real data success: {len(result.ship_berth_assignments) > 0}")
        
    except Exception as e:
        logger.error(f"Error during constraint debug: {e}", exc_info=True)

if __name__ == "__main__":
    debug_constraints()