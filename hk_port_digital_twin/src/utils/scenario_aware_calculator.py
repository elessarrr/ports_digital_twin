"""Scenario-Aware Value Calculator Utility

Comments for context:
This module provides a centralized utility for generating scenario-aware values that maintain
logical ordering across Peak, Normal, and Low seasons. It addresses the identified logical
inconsistencies in the scenarios tab where values like ship containers, TEU sizes, and
processing rates were generated with fixed ranges regardless of the scenario.

The problem we're solving:
- Ship queue metrics (containers, TEU sizes) were using fixed ranges regardless of season
- Processing rates didn't vary meaningfully between scenarios
- Wait times and other metrics lacked proper scenario-aware generation
- Values didn't maintain Peak > Normal > Low logical ordering

Our approach:
- Create a unified calculator that generates values based on scenario parameters
- Extend existing scenario parameter definitions with ship and processing characteristics
- Maintain backward compatibility with existing code
- Provide comprehensive validation to ensure logical ordering
- Use conservative enhancements that build on existing validation framework

This utility integrates with the existing scenario_tab_consolidation.py parameter system
and extends it with additional ship characteristics and processing rate parameters.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple
from enum import Enum
import logging

# Set up logging
logger = logging.getLogger(__name__)

class ScenarioType(Enum):
    """Enumeration for scenario types to ensure consistency."""
    PEAK = "Peak Season"
    NORMAL = "Normal Operations" 
    LOW = "Low Season"

class ValueType(Enum):
    """Enumeration for value types that can be generated."""
    # Existing types from scenario_tab_consolidation.py
    THROUGHPUT = "throughput"
    UTILIZATION = "utilization"
    REVENUE = "revenue"
    HANDLING_TIME = "handling_time"
    QUEUE_LENGTH = "queue_length"
    WAITING_TIME = "waiting_time"
    EFFICIENCY = "efficiency"
    CARGO_VOLUME = "cargo_volume"
    TRADE_BALANCE = "trade_balance"
    MONTHLY_VOLUME = "monthly_volume"
    KPI = "kpi"
    BERTH_THROUGHPUT = "berth_throughput"
    TREND_DATA = "trend_data"
    
    # New enhanced types for ship characteristics
    SHIP_CONTAINERS = "ship_containers"
    SHIP_TEU_SIZE = "ship_teu_size"
    SHIP_CARGO_VOLUME = "ship_cargo_volume"
    SHIP_PROCESSING_TIME = "ship_processing_time"
    SHIP_LENGTH = "ship_length"
    SHIP_DRAFT = "ship_draft"
    
    # New enhanced types for processing rates
    CONTAINERS_PROCESSED = "containers_processed"
    SHIPS_PROCESSED = "ships_processed"
    PROCESSING_RATE = "processing_rate"
    CRANE_MOVES = "crane_moves"
    
    # New enhanced types for berth characteristics
    BERTH_OCCUPANCY = "berth_occupancy"
    BERTH_EFFICIENCY = "berth_efficiency"

class ScenarioAwareCalculator:
    """
    Centralized calculator for generating scenario-aware values with logical ordering.
    
    This class extends the existing scenario parameter system from scenario_tab_consolidation.py
    with additional ship characteristics and processing rate parameters while maintaining
    backward compatibility.
    """
    
    def __init__(self):
        """Initialize the scenario-aware calculator."""
        self.scenario_parameters = self._get_enhanced_scenario_parameters()
        self.validation_cache = {}
        
    def _get_enhanced_scenario_parameters(self) -> Dict[str, Dict[str, Any]]:
        """
        Get enhanced scenario parameters that include ship characteristics and processing rates.
        
        This extends the existing parameter system from scenario_tab_consolidation.py with
        additional parameters for ship characteristics and processing rates while maintaining
        the same logical ordering principles.
        
        Returns:
            Dictionary containing enhanced parameters for all scenarios
        """
        return {
            ScenarioType.PEAK.value: {
                # Existing parameters (from scenario_tab_consolidation.py)
                "throughput_range": (130, 180),
                "utilization_range": (88, 98),
                "revenue_range": (150_000_000, 220_000_000),
                "handling_time_range": (1.0, 2.0),
                "queue_length_range": (18, 30),
                "waiting_time_exponential_scale": 1.8,
                # Enhanced wait time parameters (Peak = efficient, predictable)
                "waiting_time_distribution": "enhanced_gamma",
                "max_waiting_time": 9.0,  # Cap at 9 hours for peak efficiency
                "include_time_variation": True,
                "include_seasonal_variation": True,
                "seasonal_multiplier": 0.9,  # 10% reduction during peak efficiency
                "scenario_type": "Peak Season",
                "efficiency_range": (92, 99),
                "cargo_volume_range": (450_000, 650_000),
                "trade_balance_range": (100_000, 180_000),
                
                # Enhanced ship characteristics (Peak = larger ships, more containers)
                "ship_containers_range": (800, 1500),  # Large container ships
                "ship_teu_size_range": (8000, 15000),  # Large TEU capacity
                "ship_cargo_volume_range": (12000, 25000),  # High cargo volume per ship
                "ship_processing_time_range": (4, 8),  # Faster processing due to efficiency
                "ship_length_range": (300, 400),  # Large ships (300-400 meters)
                "ship_draft_range": (12, 16),  # Deep draft for large ships (12-16 meters)
                
                # Enhanced processing rates (Peak = higher processing capacity)
                "containers_processed_range": (150, 250),  # High container processing
                "ships_processed_range": (8, 15),  # More ships processed
                "processing_rate_range": (45, 65),  # High processing rate per hour
                "crane_moves_range": (40, 50),  # High crane productivity
                
                # Enhanced processing rate parameters
                "include_time_variation": True,  # Include shift-based variations
                "include_equipment_factors": True,  # Include equipment efficiency factors
                
                # Enhanced berth characteristics (Peak = high utilization, efficiency)
                "berth_occupancy_range": (85, 95),  # High berth occupancy
                "berth_efficiency_range": (90, 98),  # High berth efficiency
            },
            
            ScenarioType.NORMAL.value: {
                # Existing parameters (from scenario_tab_consolidation.py)
                "throughput_range": (85, 125),
                "utilization_range": (72, 85),
                "revenue_range": (110_000_000, 145_000_000),
                "handling_time_range": (2.2, 3.2),
                "queue_length_range": (10, 16),
                "waiting_time_exponential_scale": 2.8,
                # Enhanced wait time parameters (Normal = standard operations)
                "waiting_time_distribution": "enhanced_gamma",
                "max_waiting_time": 14.0,  # Standard cap at 14 hours
                "include_time_variation": True,
                "include_seasonal_variation": True,
                "seasonal_multiplier": 1.0,  # No seasonal adjustment for normal
                "scenario_type": "Normal Operations",
                "efficiency_range": (80, 90),
                "cargo_volume_range": (280_000, 420_000),
                "trade_balance_range": (20_000, 90_000),
                
                # Enhanced ship characteristics (Normal = medium ships, moderate containers)
                "ship_containers_range": (400, 800),  # Medium container ships
                "ship_teu_size_range": (4000, 8000),  # Medium TEU capacity
                "ship_cargo_volume_range": (6000, 12000),  # Medium cargo volume per ship
                "ship_processing_time_range": (6, 12),  # Moderate processing time
                "ship_length_range": (200, 300),  # Medium ships (200-300 meters)
                "ship_draft_range": (8, 12),  # Medium draft (8-12 meters)
                
                # Enhanced processing rates (Normal = moderate processing capacity)
                "containers_processed_range": (80, 150),  # Moderate container processing
                "ships_processed_range": (5, 8),  # Moderate ships processed
                "processing_rate_range": (28, 45),  # Moderate processing rate per hour
                "crane_moves_range": (28, 38),  # Moderate crane productivity
                
                # Enhanced processing rate parameters
                "include_time_variation": True,  # Include shift-based variations
                "include_equipment_factors": True,  # Include equipment efficiency factors
                
                # Enhanced berth characteristics (Normal = moderate utilization, efficiency)
                "berth_occupancy_range": (65, 85),  # Moderate berth occupancy
                "berth_efficiency_range": (75, 90),  # Moderate berth efficiency
            },
            
            ScenarioType.LOW.value: {
                # Existing parameters (from scenario_tab_consolidation.py)
                "throughput_range": (40, 80),
                "utilization_range": (45, 70),
                "revenue_range": (60_000_000, 105_000_000),
                "handling_time_range": (3.5, 5.5),
                "queue_length_range": (3, 8),
                "waiting_time_exponential_scale": 4.2,
                # Enhanced wait time parameters (Low = variable, longer waits)
                "waiting_time_distribution": "enhanced_gamma",
                "max_waiting_time": 21.0,  # Higher cap at 21 hours for low season
                "include_time_variation": True,
                "include_seasonal_variation": True,
                "seasonal_multiplier": 1.2,  # 20% increase during low efficiency
                "scenario_type": "Low Season",
                "efficiency_range": (60, 78),
                "cargo_volume_range": (120_000, 270_000),
                "trade_balance_range": (-80_000, 15_000),
                
                # Enhanced ship characteristics (Low = smaller ships, fewer containers)
                "ship_containers_range": (100, 400),  # Small container ships
                "ship_teu_size_range": (1000, 4000),  # Small TEU capacity
                "ship_cargo_volume_range": (2000, 6000),  # Low cargo volume per ship
                "ship_processing_time_range": (8, 16),  # Slower processing due to reduced efficiency
                "ship_length_range": (100, 200),  # Small ships (100-200 meters)
                "ship_draft_range": (6, 10),  # Shallow draft for small ships (6-10 meters)
                
                # Enhanced processing rates (Low = lower processing capacity)
                "containers_processed_range": (30, 80),  # Low container processing
                "ships_processed_range": (2, 5),  # Fewer ships processed
                "processing_rate_range": (15, 28),  # Low processing rate per hour
                "crane_moves_range": (15, 25),  # Low crane productivity
                
                # Enhanced processing rate parameters
                "include_time_variation": True,  # Include shift-based variations
                "include_equipment_factors": True,  # Include equipment efficiency factors
                
                # Enhanced berth characteristics (Low = low utilization, efficiency)
                "berth_occupancy_range": (35, 65),  # Low berth occupancy
                "berth_efficiency_range": (55, 75),  # Low berth efficiency
            }
        }
    
    def generate_value(self, 
                      scenario: Union[str, ScenarioType], 
                      value_type: Union[str, ValueType],
                      count: int = 1,
                      **kwargs) -> Union[float, int, List[Union[float, int]]]:
        """
        Generate scenario-aware values with logical ordering.
        
        Args:
            scenario: Scenario type (Peak Season, Normal Operations, Low Season)
            value_type: Type of value to generate
            count: Number of values to generate (default: 1)
            **kwargs: Additional parameters for specific value types
            
        Returns:
            Generated value(s) - single value if count=1, list if count>1
            
        Raises:
            ValueError: If scenario or value_type is invalid
        """
        # Normalize scenario input
        if isinstance(scenario, str):
            scenario = self._normalize_scenario_name(scenario)
        elif isinstance(scenario, ScenarioType):
            scenario = scenario.value
            
        # Normalize value_type input
        if isinstance(value_type, ValueType):
            value_type = value_type.value
            
        # Validate inputs
        if scenario not in self.scenario_parameters:
            raise ValueError(f"Invalid scenario: {scenario}. Must be one of {list(self.scenario_parameters.keys())}")
            
        # Get scenario parameters
        params = self.scenario_parameters[scenario]
        
        # Generate values based on type
        try:
            values = self._generate_values_by_type(params, value_type, count, **kwargs)
            
            # Return single value or list based on count
            if count == 1:
                return values[0] if isinstance(values, (list, np.ndarray)) else values
            else:
                return values.tolist() if isinstance(values, np.ndarray) else values
                
        except Exception as e:
            logger.error(f"Error generating {value_type} values for {scenario}: {str(e)}")
            raise ValueError(f"Failed to generate {value_type} values for {scenario}: {str(e)}")
    
    def _normalize_scenario_name(self, scenario: str) -> str:
        """
        Normalize scenario name to standard format.
        
        Args:
            scenario: Input scenario name
            
        Returns:
            Normalized scenario name
        """
        scenario_lower = scenario.lower().strip()
        
        if scenario_lower in ['peak', 'peak_season', 'peak season']:
            return ScenarioType.PEAK.value
        elif scenario_lower in ['normal', 'normal_operations', 'normal operations']:
            return ScenarioType.NORMAL.value
        elif scenario_lower in ['low', 'low_season', 'low season']:
            return ScenarioType.LOW.value
        else:
            # Try to match partial strings
            if 'peak' in scenario_lower:
                return ScenarioType.PEAK.value
            elif 'low' in scenario_lower:
                return ScenarioType.LOW.value
            else:
                return ScenarioType.NORMAL.value  # Default to normal
    
    def _generate_values_by_type(self, 
                                params: Dict[str, Any], 
                                value_type: str, 
                                count: int,
                                **kwargs) -> Union[np.ndarray, List, float, int]:
        """
        Generate values based on the specified type and parameters.
        
        Args:
            params: Scenario parameters dictionary
            value_type: Type of value to generate
            count: Number of values to generate
            **kwargs: Additional parameters
            
        Returns:
            Generated values
        """
        # Map value types to parameter keys and generation methods
        if value_type == ValueType.THROUGHPUT.value:
            return self._generate_uniform_values(params['throughput_range'], count)
            
        elif value_type == ValueType.UTILIZATION.value:
            return self._generate_uniform_values(params['utilization_range'], count)
            
        elif value_type == ValueType.REVENUE.value:
            return self._generate_uniform_values(params['revenue_range'], count)
            
        elif value_type == ValueType.HANDLING_TIME.value:
            return self._generate_uniform_values(params['handling_time_range'], count)
            
        elif value_type == ValueType.QUEUE_LENGTH.value:
            return self._generate_integer_values(params['queue_length_range'], count)
            
        elif value_type == ValueType.WAITING_TIME.value:
            return self._generate_enhanced_waiting_times(params, count)
            
        elif value_type == ValueType.EFFICIENCY.value:
            return self._generate_uniform_values(params['efficiency_range'], count)
            
        elif value_type == ValueType.CARGO_VOLUME.value:
            return self._generate_uniform_values(params['cargo_volume_range'], count)
            
        elif value_type == ValueType.TRADE_BALANCE.value:
            return self._generate_uniform_values(params['trade_balance_range'], count)
            
        # Enhanced ship characteristics (using correlated generation)
        elif value_type == ValueType.SHIP_CONTAINERS.value:
            ship_chars = self._generate_enhanced_ship_characteristics(params, count)
            return ship_chars['containers']
            
        elif value_type == ValueType.SHIP_TEU_SIZE.value:
            ship_chars = self._generate_enhanced_ship_characteristics(params, count)
            return ship_chars['teu_capacity']
            
        elif value_type == ValueType.SHIP_CARGO_VOLUME.value:
            ship_chars = self._generate_enhanced_ship_characteristics(params, count)
            return ship_chars['cargo_volume']
            
        elif value_type == ValueType.SHIP_PROCESSING_TIME.value:
            ship_chars = self._generate_enhanced_ship_characteristics(params, count)
            return ship_chars['processing_time']
            
        elif value_type == ValueType.SHIP_LENGTH.value:
            ship_chars = self._generate_enhanced_ship_characteristics(params, count)
            return ship_chars['length']
            
        elif value_type == ValueType.SHIP_DRAFT.value:
            ship_chars = self._generate_enhanced_ship_characteristics(params, count)
            return ship_chars['draft']
            
        # Enhanced processing rates (using correlated generation)
        elif value_type == ValueType.CONTAINERS_PROCESSED.value:
            processing_rates = self._generate_enhanced_processing_rates(params, count)
            return processing_rates['containers_processed']
            
        elif value_type == ValueType.SHIPS_PROCESSED.value:
            processing_rates = self._generate_enhanced_processing_rates(params, count)
            return processing_rates['ships_processed']
            
        elif value_type == ValueType.PROCESSING_RATE.value:
            processing_rates = self._generate_enhanced_processing_rates(params, count)
            return processing_rates['processing_rate']
            
        elif value_type == ValueType.CRANE_MOVES.value:
            processing_rates = self._generate_enhanced_processing_rates(params, count)
            return processing_rates['crane_moves']
            
        # Enhanced berth characteristics
        elif value_type == ValueType.BERTH_OCCUPANCY.value:
            return self._generate_uniform_values(params['berth_occupancy_range'], count)
            
        elif value_type == ValueType.BERTH_EFFICIENCY.value:
            return self._generate_uniform_values(params['berth_efficiency_range'], count)
            
        else:
            raise ValueError(f"Unknown value type: {value_type}")
    
    def _generate_uniform_values(self, value_range: Tuple[float, float], count: int) -> np.ndarray:
        """Generate uniform random values within the specified range."""
        min_val, max_val = value_range
        return np.random.uniform(min_val, max_val, count)
    
    def _generate_integer_values(self, value_range: Tuple[int, int], count: int) -> np.ndarray:
        """Generate integer random values within the specified range."""
        min_val, max_val = value_range
        return np.random.randint(min_val, max_val + 1, count)
    
    def _generate_enhanced_waiting_times(self, params: Dict[str, Any], count: int) -> np.ndarray:
        """
        Generate enhanced waiting times using multiple distribution methods.
        
        This method provides more realistic wait time modeling by:
        - Using gamma distribution for better tail behavior
        - Incorporating queue length effects
        - Adding time-of-day variations
        - Considering ship size impact on processing time
        
        Args:
            params: Scenario parameters containing wait time configuration
            count: Number of values to generate
            
        Returns:
            Array of waiting times in hours
        """
        # Get base exponential scale (backward compatibility)
        base_scale = params.get('waiting_time_exponential_scale', 2.0)
        
        # Enhanced parameters for more realistic modeling
        distribution_type = params.get('waiting_time_distribution', 'enhanced_gamma')
        
        if distribution_type == 'exponential':
            # Traditional exponential distribution (backward compatibility)
            return np.random.exponential(base_scale, count)
            
        elif distribution_type == 'enhanced_gamma':
            # Gamma distribution provides more realistic wait time modeling
            # Shape parameter controls the distribution shape (higher = more peaked)
            # Scale parameter controls the mean waiting time
            
            # Scenario-aware shape parameter (Peak = more predictable, Low = more variable)
            if 'Peak' in str(params.get('scenario_type', '')):
                shape = 2.5  # More predictable wait times during peak efficiency
                scale = base_scale * 0.8  # Shorter average wait due to better management
            elif 'Low' in str(params.get('scenario_type', '')):
                shape = 1.2  # More variable wait times during low season
                scale = base_scale * 1.3  # Longer average wait due to reduced efficiency
            else:  # Normal
                shape = 2.0  # Moderate variability
                scale = base_scale  # Standard wait times
                
            wait_times = np.random.gamma(shape, scale, count)
            
        elif distribution_type == 'queue_aware':
            # Queue-aware wait time calculation
            queue_lengths = params.get('queue_length_range', (5, 15))
            avg_queue = (queue_lengths[0] + queue_lengths[1]) / 2
            
            # Base wait time from exponential distribution
            base_waits = np.random.exponential(base_scale, count)
            
            # Queue multiplier (more ships in queue = longer wait)
            queue_multipliers = np.random.uniform(0.8, 1.5, count)
            queue_factor = avg_queue / 10.0  # Normalize queue impact
            
            wait_times = base_waits * (1 + queue_factor * queue_multipliers)
            
        elif distribution_type == 'ship_size_aware':
            # Ship size affects processing time and thus waiting time
            ship_containers = params.get('ship_containers_range', (200, 800))
            avg_containers = (ship_containers[0] + ship_containers[1]) / 2
            
            # Generate base wait times
            base_waits = np.random.exponential(base_scale, count)
            
            # Ship size multiplier (larger ships may wait longer for appropriate berths)
            size_multipliers = np.random.uniform(0.7, 1.4, count)
            size_factor = avg_containers / 500.0  # Normalize container impact
            
            wait_times = base_waits * (1 + 0.3 * size_factor * size_multipliers)
            
        else:
            # Default to enhanced gamma distribution
            shape = 2.0
            scale = base_scale
            wait_times = np.random.gamma(shape, scale, count)
        
        # Add time-of-day variation (optional enhancement)
        if params.get('include_time_variation', False):
            # Simulate higher wait times during peak hours (6-10 AM, 2-6 PM)
            time_factors = np.random.choice([1.0, 1.3, 0.8], count, p=[0.6, 0.25, 0.15])
            wait_times *= time_factors
        
        # Add seasonal variation (optional enhancement)
        if params.get('include_seasonal_variation', False):
            seasonal_factor = params.get('seasonal_multiplier', 1.0)
            wait_times *= seasonal_factor
        
        # Ensure minimum wait time (ships can't have negative wait times)
        wait_times = np.maximum(wait_times, 0.1)
        
        # Cap maximum wait time to prevent unrealistic values
        max_wait = params.get('max_waiting_time', base_scale * 5)
        wait_times = np.minimum(wait_times, max_wait)
        
        return wait_times
    
    def _generate_enhanced_ship_characteristics(self, params: Dict[str, Any], count: int) -> Dict[str, np.ndarray]:
        """
        Generate enhanced ship characteristics with realistic correlations.
        
        This method generates ship characteristics that are correlated with each other
        to create more realistic ship profiles. For example, larger ships typically
        have more containers and higher TEU capacity.
        
        Args:
            params: Scenario parameters containing ship characteristic ranges
            count: Number of ships to generate characteristics for
            
        Returns:
            Dictionary containing arrays of ship characteristics
        """
        try:
            # Get ship parameter ranges
            containers_range = params.get('ship_containers_range', (200, 800))
            teu_range = params.get('ship_teu_size_range', (2000, 8000))
            cargo_range = params.get('ship_cargo_volume_range', (4000, 12000))
            processing_range = params.get('ship_processing_time_range', (6, 12))
            length_range = params.get('ship_length_range', (150, 300))
            draft_range = params.get('ship_draft_range', (8, 12))
            
            # Generate base ship sizes (normalized 0-1)
            ship_sizes = np.random.beta(2, 2, count)  # Beta distribution for realistic size distribution
            
            # Generate correlated characteristics
            containers = containers_range[0] + ship_sizes * (containers_range[1] - containers_range[0])
            containers = containers.astype(int)
            
            # TEU capacity correlates with container count (with some variation)
            teu_base = ship_sizes * 0.8 + np.random.normal(0, 0.1, count) * 0.2
            teu_base = np.clip(teu_base, 0, 1)
            teu_capacity = teu_range[0] + teu_base * (teu_range[1] - teu_range[0])
            teu_capacity = teu_capacity.astype(int)
            
            # Cargo volume correlates with ship size but has more variation
            cargo_base = ship_sizes * 0.7 + np.random.normal(0, 0.15, count) * 0.3
            cargo_base = np.clip(cargo_base, 0, 1)
            cargo_volume = cargo_range[0] + cargo_base * (cargo_range[1] - cargo_range[0])
            
            # Processing time inversely correlates with efficiency (larger ships may be faster to process per unit)
            # But also depends on total volume
            efficiency_factor = params.get('efficiency_range', (70, 90))[0] / 100.0
            base_processing = np.random.uniform(processing_range[0], processing_range[1], count)
            
            # Adjust processing time based on ship size and efficiency
            size_factor = 1 + (ship_sizes - 0.5) * 0.3  # Larger ships take 15% more time
            efficiency_adjustment = 2.0 - efficiency_factor  # Higher efficiency = faster processing
            
            processing_time = base_processing * size_factor * efficiency_adjustment
            processing_time = np.clip(processing_time, processing_range[0], processing_range[1])
            
            # Ship length strongly correlates with ship size
            length_base = ship_sizes * 0.9 + np.random.normal(0, 0.05, count) * 0.1
            length_base = np.clip(length_base, 0, 1)
            ship_length = length_range[0] + length_base * (length_range[1] - length_range[0])
            
            # Ship draft correlates with ship size but with more variation (deeper ships can carry more)
            draft_base = ship_sizes * 0.7 + np.random.normal(0, 0.1, count) * 0.3
            draft_base = np.clip(draft_base, 0, 1)
            ship_draft = draft_range[0] + draft_base * (draft_range[1] - draft_range[0])
            
            return {
                'containers': containers,
                'teu_capacity': teu_capacity,
                'cargo_volume': cargo_volume,
                'processing_time': processing_time,
                'length': ship_length,
                'draft': ship_draft,
                'ship_sizes': ship_sizes  # Keep for reference
            }
            
        except Exception as e:
            logger.error(f"Error generating enhanced ship characteristics: {e}")
            # Fallback to simple generation
            return {
                'containers': self._generate_integer_values(containers_range, count),
                'teu_capacity': self._generate_integer_values(teu_range, count),
                'cargo_volume': self._generate_uniform_values(cargo_range, count),
                'processing_time': self._generate_uniform_values(processing_range, count),
                'ship_sizes': np.random.uniform(0, 1, count)
            }
    
    def generate_ship_profile(self, scenario: ScenarioType, ship_count: int = 1) -> Dict[str, Any]:
        """
        Generate a complete ship profile for a given scenario.
        
        This method creates realistic ship profiles that include all characteristics
        and their correlations, useful for simulation and analysis.
        
        Args:
            scenario: The scenario type to generate ships for
            ship_count: Number of ships to generate profiles for
            
        Returns:
            Dictionary containing ship profiles and statistics
        """
        try:
            # Get scenario parameters
            params = self.scenario_parameters.get(scenario.value, {})
            
            # Generate enhanced ship characteristics
            ship_chars = self._generate_enhanced_ship_characteristics(params, ship_count)
            
            # Generate ship types based on size distribution
            ship_types = []
            for size in ship_chars['ship_sizes']:
                if size < 0.3:
                    ship_types.append('Small Container')
                elif size < 0.7:
                    ship_types.append('Medium Container')
                else:
                    ship_types.append('Large Container')
            
            # Calculate derived metrics
            avg_containers_per_teu = np.mean(ship_chars['containers'] / ship_chars['teu_capacity'])
            avg_cargo_per_container = np.mean(ship_chars['cargo_volume'] / ship_chars['containers'])
            
            profile = {
                'scenario': scenario.value,
                'ship_count': ship_count,
                'characteristics': {
                    'containers': ship_chars['containers'].tolist(),
                    'teu_capacity': ship_chars['teu_capacity'].tolist(),
                    'cargo_volume': ship_chars['cargo_volume'].tolist(),
                    'processing_time': ship_chars['processing_time'].tolist(),
                    'ship_types': ship_types
                },
                'statistics': {
                    'avg_containers': float(np.mean(ship_chars['containers'])),
                    'avg_teu_capacity': float(np.mean(ship_chars['teu_capacity'])),
                    'avg_cargo_volume': float(np.mean(ship_chars['cargo_volume'])),
                    'avg_processing_time': float(np.mean(ship_chars['processing_time'])),
                    'containers_per_teu_ratio': float(avg_containers_per_teu),
                    'cargo_per_container_ratio': float(avg_cargo_per_container)
                },
                'ranges': {
                    'containers': {
                        'min': int(np.min(ship_chars['containers'])),
                        'max': int(np.max(ship_chars['containers'])),
                        'std': float(np.std(ship_chars['containers']))
                    },
                    'teu_capacity': {
                        'min': int(np.min(ship_chars['teu_capacity'])),
                        'max': int(np.max(ship_chars['teu_capacity'])),
                        'std': float(np.std(ship_chars['teu_capacity']))
                    },
                    'cargo_volume': {
                        'min': float(np.min(ship_chars['cargo_volume'])),
                        'max': float(np.max(ship_chars['cargo_volume'])),
                        'std': float(np.std(ship_chars['cargo_volume']))
                    },
                    'processing_time': {
                        'min': float(np.min(ship_chars['processing_time'])),
                        'max': float(np.max(ship_chars['processing_time'])),
                        'std': float(np.std(ship_chars['processing_time']))
                    }
                }
            }
            
            return profile
            
        except Exception as e:
            logger.error(f"Error generating ship profile for {scenario.value}: {e}")
            return {
                'scenario': scenario.value,
                'error': str(e),
                'ship_count': ship_count,
                'characteristics': {},
                'statistics': {},
                'ranges': {}
            }
    
    def _generate_enhanced_processing_rates(self, params: Dict[str, Any], count: int) -> Dict[str, np.ndarray]:
        """
        Generate enhanced processing rates with correlations and scenario-aware factors.
        
        This method generates processing rates that are correlated with each other
        and considers factors like equipment efficiency, workforce productivity,
        and operational conditions specific to each scenario.
        
        Args:
            params: Scenario parameters containing processing rate ranges
            count: Number of processing rate samples to generate
            
        Returns:
            Dictionary containing arrays of processing rate metrics
        """
        try:
            # Get processing parameter ranges
            containers_range = params.get('containers_processed_range', (50, 150))
            ships_range = params.get('ships_processed_range', (3, 10))
            rate_range = params.get('processing_rate_range', (20, 50))
            crane_range = params.get('crane_moves_range', (20, 40))
            
            # Get scenario-specific efficiency factors
            scenario_type = params.get('scenario_type', 'Normal Operations')
            
            # Base efficiency multipliers by scenario
            if 'Peak' in scenario_type:
                efficiency_base = 1.2  # 20% higher efficiency during peak
                variability = 0.15     # Lower variability (more consistent)
            elif 'Low' in scenario_type:
                efficiency_base = 0.8  # 20% lower efficiency during low season
                variability = 0.25     # Higher variability (less consistent)
            else:
                efficiency_base = 1.0  # Normal efficiency
                variability = 0.20     # Moderate variability
            
            # Generate base efficiency factors using beta distribution
            # Beta distribution creates realistic efficiency curves
            efficiency_factors = np.random.beta(2, 2, count)  # Bell-shaped around 0.5
            efficiency_factors = efficiency_factors * efficiency_base
            
            # Add operational variability
            operational_noise = np.random.normal(0, variability, count)
            efficiency_factors = np.clip(efficiency_factors + operational_noise, 0.3, 2.0)
            
            # Generate correlated processing rates
            # Base processing rate (foundation for other metrics)
            base_rates = np.random.uniform(rate_range[0], rate_range[1], count)
            processing_rates = base_rates * efficiency_factors
            
            # Containers processed (correlated with processing rate and efficiency)
            container_base = np.random.uniform(containers_range[0], containers_range[1], count)
            # Higher processing rates should correlate with more containers
            rate_correlation = (processing_rates - np.min(processing_rates)) / (np.max(processing_rates) - np.min(processing_rates))
            containers_processed = container_base * (0.7 + 0.6 * rate_correlation)
            containers_processed = np.clip(containers_processed, containers_range[0], containers_range[1])
            
            # Ships processed (inversely correlated with container processing - focus trade-off)
            ship_base = np.random.uniform(ships_range[0], ships_range[1], count)
            # When processing more containers per ship, fewer ships overall
            container_intensity = (containers_processed - np.min(containers_processed)) / (np.max(containers_processed) - np.min(containers_processed))
            ships_processed = ship_base * (1.2 - 0.4 * container_intensity)
            ships_processed = np.clip(ships_processed, ships_range[0], ships_range[1])
            
            # Crane moves (strongly correlated with container processing)
            crane_base = np.random.uniform(crane_range[0], crane_range[1], count)
            # More containers require more crane moves
            crane_moves = crane_base * (0.8 + 0.4 * rate_correlation)
            crane_moves = np.clip(crane_moves, crane_range[0], crane_range[1])
            
            # Add time-of-day variations if specified
            if params.get('include_time_variation', False):
                time_factors = self._generate_time_of_day_factors(count)
                processing_rates *= time_factors
                containers_processed *= time_factors
                crane_moves *= time_factors
            
            # Add equipment degradation factors
            if params.get('include_equipment_factors', True):
                equipment_factors = np.random.normal(1.0, 0.1, count)
                equipment_factors = np.clip(equipment_factors, 0.7, 1.3)
                processing_rates *= equipment_factors
                crane_moves *= equipment_factors
            
            return {
                'containers_processed': containers_processed.astype(int),
                'ships_processed': ships_processed.astype(int),
                'processing_rate': processing_rates,
                'crane_moves': crane_moves
            }
            
        except Exception as e:
            logger.error(f"Error generating enhanced processing rates: {e}")
            # Fallback to simple generation
            return {
                'containers_processed': self._generate_integer_values(params.get('containers_processed_range', (50, 150)), count),
                'ships_processed': self._generate_integer_values(params.get('ships_processed_range', (3, 10)), count),
                'processing_rate': self._generate_uniform_values(params.get('processing_rate_range', (20, 50)), count),
                'crane_moves': self._generate_uniform_values(params.get('crane_moves_range', (20, 40)), count)
            }
    
    def _generate_time_of_day_factors(self, count: int) -> np.ndarray:
        """Generate time-of-day efficiency factors."""
        # Simulate different efficiency during different shifts
        # Day shift (higher), Evening shift (moderate), Night shift (lower)
        shift_probs = [0.4, 0.35, 0.25]  # Probability of each shift
        shifts = np.random.choice([1.1, 1.0, 0.9], count, p=shift_probs)
        return shifts
    
    def get_wait_time_statistics(self, scenario: ScenarioType, sample_size: int = 1000) -> Dict[str, Any]:
        """
        Generate wait time statistics for a given scenario.
        
        This method is useful for validation and understanding the distribution
        characteristics of wait times across different scenarios.
        
        Args:
            scenario: The scenario type to analyze
            sample_size: Number of samples to generate for statistics
            
        Returns:
            Dictionary containing wait time statistics
        """
        try:
            # Get scenario parameters
            params = self.scenario_parameters.get(scenario.value, {})
            
            # Generate sample wait times
            wait_times = self._generate_enhanced_waiting_times(params, sample_size)
            
            # Calculate statistics
            stats = {
                'scenario': scenario.value,
                'sample_size': sample_size,
                'distribution_type': params.get('waiting_time_distribution', 'enhanced_gamma'),
                'statistics': {
                    'mean': float(np.mean(wait_times)),
                    'median': float(np.median(wait_times)),
                    'std_dev': float(np.std(wait_times)),
                    'min': float(np.min(wait_times)),
                    'max': float(np.max(wait_times)),
                    'percentile_25': float(np.percentile(wait_times, 25)),
                    'percentile_75': float(np.percentile(wait_times, 75)),
                    'percentile_90': float(np.percentile(wait_times, 90)),
                    'percentile_95': float(np.percentile(wait_times, 95))
                },
                'parameters': {
                    'exponential_scale': params.get('waiting_time_exponential_scale', 2.0),
                    'max_waiting_time': params.get('max_waiting_time', 15.0),
                    'seasonal_multiplier': params.get('seasonal_multiplier', 1.0),
                    'includes_time_variation': params.get('include_time_variation', False),
                    'includes_seasonal_variation': params.get('include_seasonal_variation', False)
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error generating wait time statistics for {scenario.value}: {e}")
            return {
                'scenario': scenario.value,
                'error': str(e),
                'statistics': {}
            }
    
    def get_processing_rate_statistics(self, scenario: ScenarioType, num_samples: int = 1000) -> Dict[str, Any]:
        """
        Generate comprehensive processing rate statistics for a given scenario.
        
        Args:
            scenario: The scenario type to generate statistics for
            num_samples: Number of samples to generate for statistics
            
        Returns:
            Dictionary containing processing rate statistics and parameters
        """
        try:
            params = self.scenario_parameters[scenario.value]
            
            # Generate multiple samples of processing rates
            processing_data = []
            for _ in range(num_samples):
                rates = self._generate_enhanced_processing_rates(params, 1)  # Generate 1 sample at a time
                processing_data.append(rates)
            
            # Extract individual metrics (taking first element since count=1)
            containers_processed = [data['containers_processed'][0] for data in processing_data]
            ships_processed = [data['ships_processed'][0] for data in processing_data]
            processing_rates = [data['processing_rate'][0] for data in processing_data]
            crane_moves = [data['crane_moves'][0] for data in processing_data]
            
            # Calculate statistics for each metric
            stats = {
                'scenario': scenario.value,
                'sample_size': num_samples,
                'containers_processed': {
                    'mean': float(np.mean(containers_processed)),
                    'std': float(np.std(containers_processed)),
                    'min': float(np.min(containers_processed)),
                    'max': float(np.max(containers_processed)),
                    'median': float(np.median(containers_processed)),
                    'percentile_25': float(np.percentile(containers_processed, 25)),
                    'percentile_75': float(np.percentile(containers_processed, 75)),
                    'percentile_90': float(np.percentile(containers_processed, 90)),
                    'percentile_95': float(np.percentile(containers_processed, 95))
                },
                'ships_processed': {
                    'mean': float(np.mean(ships_processed)),
                    'std': float(np.std(ships_processed)),
                    'min': float(np.min(ships_processed)),
                    'max': float(np.max(ships_processed)),
                    'median': float(np.median(ships_processed)),
                    'percentile_25': float(np.percentile(ships_processed, 25)),
                    'percentile_75': float(np.percentile(ships_processed, 75)),
                    'percentile_90': float(np.percentile(ships_processed, 90)),
                    'percentile_95': float(np.percentile(ships_processed, 95))
                },
                'processing_rate': {
                    'mean': float(np.mean(processing_rates)),
                    'std': float(np.std(processing_rates)),
                    'min': float(np.min(processing_rates)),
                    'max': float(np.max(processing_rates)),
                    'median': float(np.median(processing_rates)),
                    'percentile_25': float(np.percentile(processing_rates, 25)),
                    'percentile_75': float(np.percentile(processing_rates, 75)),
                    'percentile_90': float(np.percentile(processing_rates, 90)),
                    'percentile_95': float(np.percentile(processing_rates, 95))
                },
                'crane_moves': {
                    'mean': float(np.mean(crane_moves)),
                    'std': float(np.std(crane_moves)),
                    'min': float(np.min(crane_moves)),
                    'max': float(np.max(crane_moves)),
                    'median': float(np.median(crane_moves)),
                    'percentile_25': float(np.percentile(crane_moves, 25)),
                    'percentile_75': float(np.percentile(crane_moves, 75)),
                    'percentile_90': float(np.percentile(crane_moves, 90)),
                    'percentile_95': float(np.percentile(crane_moves, 95))
                },
                'parameters': {
                    'containers_processed_range': params.get('containers_processed_range', (50, 200)),
                    'ships_processed_range': params.get('ships_processed_range', (3, 10)),
                    'processing_rate_range': params.get('processing_rate_range', (20, 50)),
                    'crane_moves_range': params.get('crane_moves_range', (20, 40)),
                    'includes_time_variation': params.get('include_time_variation', False),
                    'includes_equipment_factors': params.get('include_equipment_factors', False)
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error generating processing rate statistics for {scenario.value}: {e}")
            return {
                'scenario': scenario.value,
                'error': str(e),
                'statistics': {}
            }
    
    def validate_scenario_ordering(self) -> Dict[str, Any]:
        """
        Validate that all scenario parameters maintain logical ordering.
        
        Returns:
            Dictionary containing validation results
        """
        validation_results = {
            'errors': [],
            'warnings': [],
            'status': 'valid',
            'parameter_checks': {}
        }
        
        # Get parameters for all scenarios
        peak_params = self.scenario_parameters[ScenarioType.PEAK.value]
        normal_params = self.scenario_parameters[ScenarioType.NORMAL.value]
        low_params = self.scenario_parameters[ScenarioType.LOW.value]
        
        # Define parameters that should follow Peak > Normal > Low ordering
        ascending_params = [
            'throughput_range', 'utilization_range', 'revenue_range',
            'efficiency_range', 'cargo_volume_range', 'trade_balance_range',
            'ship_containers_range', 'ship_teu_size_range', 'ship_cargo_volume_range',
            'containers_processed_range', 'ships_processed_range', 'processing_rate_range',
            'crane_moves_range', 'berth_occupancy_range', 'berth_efficiency_range'
        ]
        
        # Define parameters that should follow Peak < Normal < Low ordering (inverse)
        descending_params = [
            'handling_time_range', 'waiting_time_exponential_scale', 'ship_processing_time_range'
        ]
        
        # Validate ascending parameters
        for param in ascending_params:
            if param in peak_params and param in normal_params and param in low_params:
                result = self._validate_ascending_parameter(
                    param, peak_params[param], normal_params[param], low_params[param]
                )
                validation_results['parameter_checks'][param] = result
                validation_results['errors'].extend(result.get('errors', []))
                validation_results['warnings'].extend(result.get('warnings', []))
        
        # Validate descending parameters
        for param in descending_params:
            if param in peak_params and param in normal_params and param in low_params:
                result = self._validate_descending_parameter(
                    param, peak_params[param], normal_params[param], low_params[param]
                )
                validation_results['parameter_checks'][param] = result
                validation_results['errors'].extend(result.get('errors', []))
                validation_results['warnings'].extend(result.get('warnings', []))
        
        # Set overall status
        if validation_results['errors']:
            validation_results['status'] = 'invalid'
        elif validation_results['warnings']:
            validation_results['status'] = 'warning'
        
        return validation_results
    
    def _validate_ascending_parameter(self, param_name: str, peak_val: Any, normal_val: Any, low_val: Any) -> Dict[str, Any]:
        """Validate that a parameter follows Peak > Normal > Low ordering."""
        result = {'errors': [], 'warnings': [], 'status': 'valid'}
        
        if isinstance(peak_val, tuple) and isinstance(normal_val, tuple) and isinstance(low_val, tuple):
            peak_min, peak_max = peak_val
            normal_min, normal_max = normal_val
            low_min, low_max = low_val
            
            # Check minimum values ordering
            if not (peak_min > normal_min > low_min):
                result['errors'].append(
                    f"{param_name} minimum values don't follow Peak > Normal > Low ordering: "
                    f"Peak({peak_min}) > Normal({normal_min}) > Low({low_min})"
                )
            
            # Check maximum values ordering
            if not (peak_max > normal_max > low_max):
                result['errors'].append(
                    f"{param_name} maximum values don't follow Peak > Normal > Low ordering: "
                    f"Peak({peak_max}) > Normal({normal_max}) > Low({low_max})"
                )
            
            # Check for range overlaps
            if normal_max >= peak_min:
                result['warnings'].append(
                    f"{param_name} Normal and Peak ranges overlap: "
                    f"Normal({normal_min}-{normal_max}) vs Peak({peak_min}-{peak_max})"
                )
            
            if low_max >= normal_min:
                result['warnings'].append(
                    f"{param_name} Low and Normal ranges overlap: "
                    f"Low({low_min}-{low_max}) vs Normal({normal_min}-{normal_max})"
                )
        
        if result['errors']:
            result['status'] = 'invalid'
        elif result['warnings']:
            result['status'] = 'warning'
            
        return result
    
    def _validate_descending_parameter(self, param_name: str, peak_val: Any, normal_val: Any, low_val: Any) -> Dict[str, Any]:
        """Validate that a parameter follows Peak < Normal < Low ordering."""
        result = {'errors': [], 'warnings': [], 'status': 'valid'}
        
        if isinstance(peak_val, tuple) and isinstance(normal_val, tuple) and isinstance(low_val, tuple):
            peak_min, peak_max = peak_val
            normal_min, normal_max = normal_val
            low_min, low_max = low_val
            
            # Check minimum values ordering (inverse)
            if not (peak_min < normal_min < low_min):
                result['errors'].append(
                    f"{param_name} minimum values don't follow Peak < Normal < Low ordering: "
                    f"Peak({peak_min}) < Normal({normal_min}) < Low({low_min})"
                )
            
            # Check maximum values ordering (inverse)
            if not (peak_max < normal_max < low_max):
                result['errors'].append(
                    f"{param_name} maximum values don't follow Peak < Normal < Low ordering: "
                    f"Peak({peak_max}) < Normal({normal_max}) < Low({low_max})"
                )
        else:
            # Single value parameters
            if not (peak_val < normal_val < low_val):
                result['errors'].append(
                    f"{param_name} values don't follow Peak < Normal < Low ordering: "
                    f"Peak({peak_val}) < Normal({normal_val}) < Low({low_val})"
                )
        
        if result['errors']:
            result['status'] = 'invalid'
        elif result['warnings']:
            result['status'] = 'warning'
            
        return result
    
    def get_scenario_summary(self, scenario: Union[str, ScenarioType]) -> Dict[str, Any]:
        """
        Get a summary of parameters for a specific scenario.
        
        Args:
            scenario: Scenario type
            
        Returns:
            Dictionary containing scenario parameter summary
        """
        # Normalize scenario input
        if isinstance(scenario, str):
            scenario = self._normalize_scenario_name(scenario)
        elif isinstance(scenario, ScenarioType):
            scenario = scenario.value
            
        if scenario not in self.scenario_parameters:
            raise ValueError(f"Invalid scenario: {scenario}")
            
        params = self.scenario_parameters[scenario]
        
        return {
            'scenario': scenario,
            'parameters': params,
            'parameter_count': len(params),
            'enhanced_parameters': [
                key for key in params.keys() 
                if key.startswith(('ship_', 'containers_processed', 'ships_processed', 'processing_rate', 'crane_moves', 'berth_'))
            ]
        }

# Convenience functions for backward compatibility and ease of use
def generate_scenario_value(scenario: str, value_type: str, count: int = 1, **kwargs) -> Union[float, int, List]:
    """
    Convenience function to generate scenario-aware values.
    
    Args:
        scenario: Scenario name
        value_type: Type of value to generate
        count: Number of values to generate
        **kwargs: Additional parameters
        
    Returns:
        Generated value(s)
    """
    calculator = ScenarioAwareCalculator()
    return calculator.generate_value(scenario, value_type, count, **kwargs)

def validate_all_scenarios() -> Dict[str, Any]:
    """
    Convenience function to validate all scenario parameters.
    
    Returns:
        Validation results dictionary
    """
    calculator = ScenarioAwareCalculator()
    return calculator.validate_scenario_ordering()

def get_available_value_types() -> List[str]:
    """
    Get list of available value types that can be generated.
    
    Returns:
        List of value type strings
    """
    return [vt.value for vt in ValueType]

def get_available_scenarios() -> List[str]:
    """
    Get list of available scenario types.
    
    Returns:
        List of scenario type strings
    """
    return [st.value for st in ScenarioType]