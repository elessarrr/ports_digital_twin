#!/usr/bin/env python3
"""
Enhanced Debug Script for Optimization Metrics
This script provides detailed debugging of the ship-berth assignment process
to identify why no ships are being assigned to berths.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ai.optimization import BerthAllocationOptimizer, ScenarioWeights, OptimizationConstraints, Ship, Berth
from src.utils.data_loader import load_berth_configurations, load_vessel_arrivals
from datetime import datetime
import logging
import pandas as pd

# Configure logging for detailed debugging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_detailed_optimization.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def debug_detailed_optimization():
    """Enhanced debugging of optimization process"""
    try:
        logger.info("=== ENHANCED OPTIMIZATION DEBUG SESSION ===")
        
        # Load data
        logger.info("Loading berth configurations...")
        berth_data = load_berth_configurations()
        logger.info(f"Loaded {len(berth_data)} berth configurations")
        
        logger.info("Loading vessel arrivals...")
        vessel_data = load_vessel_arrivals()
        logger.info(f"Loaded {len(vessel_data)} vessel records")
        
        # Initialize constraints and weights
        constraints = OptimizationConstraints(
            max_berths=20,
            max_cranes=40,
            budget=1000.0
        )
        
        scenario_weights = ScenarioWeights(
            normal=0.4,
            peak_season=0.3,
            maintenance=0.2,
            typhoon_season=0.1
        )
        
        # Initialize optimizer
        optimizer = BerthAllocationOptimizer(scenario_weights, constraints)
        
        logger.info("Converting data to optimization objects...")
        
        # Create berths list with detailed logging
        berths = []
        logger.info("=== BERTH DATA ANALYSIS ===")
        for i, berth_config in enumerate(berth_data):
            logger.info(f"Berth {i+1}: {berth_config}")
            
            # Extract berth data with correct field names
            berth_id = str(berth_config.get('berth_id', f'berth_{i+1}'))
            capacity = float(berth_config.get('max_capacity_teu', 50000))  # Use correct field name
            crane_count = int(berth_config.get('crane_count', 2))
            
            # Handle suitable_ship_types - use berth_type as ship type compatibility
            berth_type = berth_config.get('berth_type', 'container')
            # For now, let's make berths accept all ship types (empty list means accepts all)
            suitable_types = []  # Accept all ship types for debugging
            
            logger.info(f"  Berth {berth_id}: capacity={capacity}, cranes={crane_count}, types={suitable_types}")
            
            berth = Berth(
                id=berth_id,
                capacity=capacity,
                crane_count=crane_count,
                suitable_ship_types=suitable_types,
                is_available=True
            )
            berths.append(berth)
        
        # Create ships list with detailed logging
        ships = []
        logger.info("=== SHIP DATA ANALYSIS ===")
        ship_count = 0
        for i, (_, vessel_row) in enumerate(vessel_data.head(5).iterrows()):  # Test with first 5 vessels
            logger.info(f"Vessel {i+1}: {dict(vessel_row)}")
            
            try:
                # Extract ship data with correct field names from vessel data
                ship_id = str(vessel_row.get('call_sign', f'ship_{i+1}'))
                arrival_time = vessel_row.get('arrival_time', datetime.now())
                if pd.isna(arrival_time) or arrival_time is None:
                    arrival_time = datetime.now()  # Use current time for testing
                
                ship_type = str(vessel_row.get('ship_type', 'container')).lower().strip()
                
                # For ship size, we need to estimate since it's not in the XML data
                # Let's use a reasonable default based on ship type
                size = 20000.0  # Default size in TEU
                if 'container' in ship_type.lower():
                    size = 15000.0
                elif 'bulk' in ship_type.lower():
                    size = 30000.0
                elif 'tanker' in ship_type.lower():
                    size = 25000.0
                
                logger.info(f"  Ship {ship_id}: type='{ship_type}', size={size}")
                
                ship = Ship(
                    id=ship_id,
                    arrival_time=arrival_time,
                    ship_type=ship_type,
                    size=size,
                    priority=1,
                    estimated_service_time=8.0,  # Default 8 hours
                    containers_to_load=100,      # Default values
                    containers_to_unload=150
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
        
        # Manual compatibility check before optimization
        logger.info("=== MANUAL COMPATIBILITY CHECK ===")
        for ship in ships:
            logger.info(f"Checking ship {ship.id} (type: '{ship.ship_type}', size: {ship.size})")
            compatible_berths = []
            
            for berth in berths:
                # Check size compatibility
                size_ok = ship.size <= berth.capacity
                
                # Check type compatibility
                type_ok = (not berth.suitable_ship_types or 
                          ship.ship_type in berth.suitable_ship_types or
                          len(berth.suitable_ship_types) == 0)
                
                is_suitable = optimizer.is_berth_suitable(ship, berth)
                
                logger.info(f"  Berth {berth.id}: size_ok={size_ok} ({ship.size} <= {berth.capacity}), "
                           f"type_ok={type_ok} ('{ship.ship_type}' in {berth.suitable_ship_types}), "
                           f"is_suitable={is_suitable}")
                
                if is_suitable:
                    compatible_berths.append(berth.id)
            
            logger.info(f"  Ship {ship.id} compatible berths: {compatible_berths}")
        
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
        logger.info(f"Assignments: {result.ship_berth_assignments}")
        
        # Log berth utilization details
        logger.info("=== BERTH UTILIZATION ===")
        for berth_id, utilization in result.berth_utilization.items():
            logger.info(f"  {berth_id}: {utilization:.2%}")
        
        logger.info("=== ENHANCED DEBUG SESSION COMPLETE ===")
        
    except Exception as e:
        logger.error(f"Error during enhanced debug session: {e}", exc_info=True)

if __name__ == "__main__":
    debug_detailed_optimization()