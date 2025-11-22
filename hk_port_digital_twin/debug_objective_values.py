#!/usr/bin/env python3
"""
Objective Value Debug Script
This script analyzes the objective value calculation to understand
why values are only 1-0.8 instead of up to 100.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ai.optimization import BerthAllocationOptimizer, ScenarioWeights, OptimizationConstraints
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_objective_calculation():
    """Debug the objective value calculation step by step"""
    
    logger.info("=== OBJECTIVE VALUE CALCULATION DEBUG ===")
    
    # Create optimizer
    scenario_weights = ScenarioWeights()
    constraints = OptimizationConstraints()
    optimizer = BerthAllocationOptimizer(scenario_weights, constraints)
    
    # Test different metric scenarios
    test_scenarios = [
        {
            'name': 'Worst Case',
            'metrics': {
                'waiting_time': 24.0,  # 24 hours waiting
                'utilization': 0.0,    # 0% utilization
                'throughput': 0.0,     # 0 throughput
                'efficiency': 0.0      # 0% efficiency
            }
        },
        {
            'name': 'Best Case',
            'metrics': {
                'waiting_time': 0.0,   # No waiting
                'utilization': 1.0,    # 100% utilization
                'throughput': 100.0,   # High throughput
                'efficiency': 1.0      # 100% efficiency
            }
        },
        {
            'name': 'Typical Good',
            'metrics': {
                'waiting_time': 2.0,   # 2 hours waiting
                'utilization': 0.8,    # 80% utilization
                'throughput': 50.0,    # Moderate throughput
                'efficiency': 0.9      # 90% efficiency
            }
        },
        {
            'name': 'Typical Poor',
            'metrics': {
                'waiting_time': 12.0,  # 12 hours waiting
                'utilization': 0.3,    # 30% utilization
                'throughput': 10.0,    # Low throughput
                'efficiency': 0.4      # 40% efficiency
            }
        },
        {
            'name': 'Current Debug Values',
            'metrics': {
                'waiting_time': 0.0,   # No waiting (no ships assigned)
                'utilization': 0.0,    # 0% utilization (no ships assigned)
                'throughput': 0.0,     # 0 throughput (no ships assigned)
                'efficiency': 0.0      # 0% efficiency (no ships assigned)
            }
        }
    ]
    
    logger.info(f"Scenario weights: Normal={scenario_weights.normal}, Peak={scenario_weights.peak_season}, Maintenance={scenario_weights.maintenance}, Typhoon={scenario_weights.typhoon_season}")
    
    for scenario in test_scenarios:
        logger.info(f"\n--- {scenario['name']} ---")
        metrics = scenario['metrics']
        logger.info(f"Input metrics: {metrics}")
        
        # Calculate raw objective value
        raw_objective = optimizer.calculate_weighted_objective_value(metrics)
        logger.info(f"Raw objective value: {raw_objective:.2f}")
        
        # Calculate normalized objective value
        normalized_objective = optimizer.normalize_objective_value(raw_objective)
        logger.info(f"Normalized objective value: {normalized_objective:.2f}")
        
        # Manual calculation breakdown
        logger.info("Manual calculation breakdown:")
        
        # Calculate for each scenario weight
        total_manual = 0.0
        for scenario_name, weight in [
            ('normal', scenario_weights.normal),
            ('peak_season', scenario_weights.peak_season),
            ('maintenance', scenario_weights.maintenance),
            ('typhoon_season', scenario_weights.typhoon_season)
        ]:
            # Get multipliers (from the code)
            multipliers = {
                'normal': {'waiting_time_factor': 1.0, 'utilization_factor': 1.0, 'throughput_factor': 1.0, 'efficiency_factor': 1.0},
                'peak_season': {'waiting_time_factor': 1.5, 'utilization_factor': 1.2, 'throughput_factor': 1.3, 'efficiency_factor': 1.1},
                'maintenance': {'waiting_time_factor': 0.8, 'utilization_factor': 0.7, 'throughput_factor': 0.6, 'efficiency_factor': 0.8},
                'typhoon_season': {'waiting_time_factor': 2.0, 'utilization_factor': 0.5, 'throughput_factor': 0.4, 'efficiency_factor': 0.6}
            }[scenario_name]
            
            # Calculate components (updated scaling factors)
            waiting_component = -metrics['waiting_time'] * multipliers['waiting_time_factor'] * 2
            utilization_component = metrics['utilization'] * multipliers['utilization_factor'] * 25
            throughput_component = metrics['throughput'] * multipliers['throughput_factor'] * 1
            efficiency_component = metrics['efficiency'] * multipliers['efficiency_factor'] * 25
            
            scenario_total = waiting_component + utilization_component + throughput_component + efficiency_component
            weighted_total = scenario_total * weight
            total_manual += weighted_total
            
            logger.info(f"  {scenario_name} (weight {weight:.1f}): waiting={waiting_component:.2f}, util={utilization_component:.2f}, throughput={throughput_component:.2f}, efficiency={efficiency_component:.2f} -> {scenario_total:.2f} * {weight:.1f} = {weighted_total:.2f}")
        
        logger.info(f"Manual total: {total_manual:.2f}")
        logger.info(f"Difference from method: {abs(raw_objective - total_manual):.6f}")

def analyze_scaling_factors():
    """Analyze the scaling factors used in the calculation"""
    logger.info("\n=== SCALING FACTOR ANALYSIS ===")
    
    logger.info("Current scaling factors in the code:")
    logger.info("- Utilization: * 25 (so 100% utilization = 25 points)")
    logger.info("- Throughput: * 1 (so 25 containers/hour = 25 points)")
    logger.info("- Efficiency: * 25 (so 100% efficiency = 25 points)")
    logger.info("- Waiting time: * -2 (so 24 hours waiting = -48 points)")
    
    logger.info("\nBalanced design:")
    logger.info("1. Each metric can contribute ~25 points maximum")
    logger.info("2. Utilization: 0-1 range, scaled by 25 -> 0-25 points")
    logger.info("3. Throughput: 0-25 range, scaled by 1 -> 0-25 points")
    logger.info("4. Efficiency: 0-1 range, scaled by 25 -> 0-25 points")
    logger.info("5. Waiting time: 0-24 hours, penalty scaled by -2 -> 0 to -48 points")

if __name__ == "__main__":
    debug_objective_calculation()
    analyze_scaling_factors()