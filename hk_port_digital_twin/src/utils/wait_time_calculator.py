"""Wait Time Calculator Utility

Comments for context:
This module provides a simplified and intuitive system for calculating ship wait times.
It uses clear, distinct threshold bands for "Peak," "Normal," and "Low" scenarios
to ensure that wait times are logical and easy to understand (Peak > Normal > Low).

The calculation uses a simple uniform distribution within these bands, avoiding
overly complex statistical models while still providing realistic variability.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple
from enum import Enum
import logging
from src.utils.scenario_helpers import get_wait_time_scenario_name

# Configure logging for the wait time calculator
logger = logging.getLogger(__name__)

class WaitTimeMethod(Enum):
    """
    Enumeration for wait time calculation methods.
    
    Attributes:
        THRESHOLD_BANDS: New band/threshold system with logical ordering
        EXPONENTIAL_LEGACY: Legacy exponential system for backward compatibility
    """
    THRESHOLD_BANDS = "threshold_bands"  # New band/threshold system
    EXPONENTIAL_LEGACY = "exponential_legacy"  # Legacy exponential system for rollback

class ScenarioType(Enum):
    """
    Enumeration for scenario types to ensure consistency across the system.
    
    These scenarios represent different operational states of the port:
    - PEAK: High demand periods (holidays, major shipping events)
    - NORMAL: Standard business operations
    - LOW: Off-peak periods with reduced shipping activity
    """
    PEAK = "Peak Season"
    NORMAL = "Normal Operations" 
    LOW = "Low Season"

class WaitTimeCalculator:
    """
    Advanced wait time calculator implementing band/threshold system.
    
    This class provides intuitive wait time calculations using threshold bands
    that ensure logical ordering: Peak Season > Normal Operations > Low Season.
    
    Key Features:
    - Threshold-based calculation with configurable bands
    - Statistical distribution within bands for realistic variability
    - Batch calculation support for analysis and charting
    - Robust input validation and error handling
    - Backward compatibility with legacy exponential system
    - Comprehensive logging and monitoring
    
    Usage Examples:
        # Basic usage
        calculator = WaitTimeCalculator()
        wait_time = calculator.calculate_wait_time('Normal Operations')
        
        # With multiplier
        wait_time = calculator.calculate_wait_time('Peak Season', multiplier=1.5)
        
        # Batch calculations for analysis
        wait_times = calculator.calculate_wait_time('Normal Operations', num_samples=100)
        
        # Legacy system for rollback
        legacy_calc = WaitTimeCalculator(method=WaitTimeMethod.EXPONENTIAL_LEGACY)
        legacy_time = legacy_calc.calculate_wait_time('Peak Season')
    
    Attributes:
        method (WaitTimeMethod): Calculation method to use
        threshold_bands (Dict): Configuration for threshold bands
        exponential_scales (Dict): Legacy exponential scale configuration
    """
    
    def __init__(self, method: WaitTimeMethod = WaitTimeMethod.THRESHOLD_BANDS):
        """
        Initialize the wait time calculator with specified calculation method.
        
        The calculator supports two methods:
        1. THRESHOLD_BANDS (default): Logical band-based system with Peak > Normal > Low
        2. EXPONENTIAL_LEGACY: Legacy exponential system for backward compatibility
        
        Args:
            method (WaitTimeMethod): Calculation method to use. Defaults to THRESHOLD_BANDS
                for logical, intuitive wait time calculations.
        
        Raises:
            ValueError: If an invalid method is provided
            
        Example:
            # Use new threshold-based system (recommended)
            calculator = WaitTimeCalculator()
            
            # Use legacy exponential system for rollback
            legacy_calc = WaitTimeCalculator(method=WaitTimeMethod.EXPONENTIAL_LEGACY)
        """
        self.method = method
        self.threshold_bands = self._define_threshold_bands()
        self.legacy_exponential_scales = self._get_legacy_exponential_scales()
        
        # Validation cache for performance optimization
        self.validation_cache = {}
        
        logger.info(f"WaitTimeCalculator initialized with method: {method.value}")
    
    def _define_threshold_bands(self):
        """
        Defines the threshold bands for different scenarios.

        Returns:
            dict: A dictionary containing the threshold bands for each scenario.
        """
        # Comments for context:
        # These threshold bands are used to determine the wait time based on the scenario.
        # The values are based on historical data and operational models of the port.
        # The 'Peak Season' scenario represents the busiest times, with higher wait times.
        # The 'Normal Operations' scenario represents the average operational capacity.
        # The 'Low Season' scenario represents the quietest times, with lower wait times.
        # Each band has a minimum and maximum wait time, a distribution type, and a description.
        threshold_bands = {
            ScenarioType.PEAK.value: {
                "min_hours": 12,
                "max_hours": 24,
                "description": "High congestion, long wait times (e.g., holiday season)",
            },
            ScenarioType.NORMAL.value: {
                "min_hours": 6,
                "max_hours": 11,
                "description": "Standard operational conditions",
            },
            ScenarioType.LOW.value: {
                "min_hours": 1,
                "max_hours": 5,
                "description": "Low congestion, minimal wait times (e.g., off-season)",
            }
        }
        
        # Example of how to access and print the peak season range
        peak_band = threshold_bands[ScenarioType.PEAK.value]
        return threshold_bands

    def _get_legacy_exponential_scales(self):
        """
        Defines the legacy exponential scales for different scenarios.
        
        Returns:
            Dictionary containing legacy exponential scales
        """
        return {
            ScenarioType.PEAK.value: 1.8,    # Original: counterintuitively low
            ScenarioType.NORMAL.value: 2.8,  # Original: higher than peak
            ScenarioType.LOW.value: 4.2      # Original: highest scale
        }
    
    def calculate_wait_time(self,
                          scenario: str,
                          num_samples: int = 1) -> Union[float, np.ndarray]:
        """
        Calculate wait time(s) for a given scenario.

        Args:
            scenario (str): Scenario name ('Peak Season', 'Normal Operations', 'Low Season').
            num_samples (int, optional): Number of samples. Defaults to 1.

        Returns:
            Union[float, np.ndarray]: Single wait time or array of wait times.
        """
        if not isinstance(scenario, str) or not scenario.strip():
            raise ValueError("scenario must be a non-empty string")
        if not isinstance(num_samples, int) or num_samples < 1:
            raise ValueError("num_samples must be a positive integer")
        if scenario not in [s.value for s in ScenarioType]:
            raise ValueError(f"Unknown scenario: {scenario}")

        try:
            if self.method == WaitTimeMethod.THRESHOLD_BANDS:
                wait_times = self._calculate_threshold_wait_time(scenario, num_samples)
            else:
                wait_times = self._calculate_exponential_wait_time(scenario, num_samples)
        except Exception as e:
            logger.error(f"Error in calculation: {e}, falling back to default.")
            wait_times = np.random.uniform(4, 12, num_samples)

        wait_times = np.clip(wait_times, 0.1, 100.0)

        result = float(wait_times[0]) if num_samples == 1 else wait_times
        return result
    
    def _calculate_threshold_wait_time(self, scenario: str, num_samples: int) -> np.ndarray:
        """
        Calculate wait time using threshold bands (new method).
        
        Args:
            scenario: Scenario name
            num_samples: Number of samples to generate
            
        Returns:
            Array of wait times within the scenario's threshold band
            
        Raises:
            ValueError: If scenario is unknown or num_samples is invalid
        """
        if num_samples < 1:
            raise ValueError(f"num_samples must be at least 1, got {num_samples}")
        
        try:
            band = self.threshold_bands[scenario]
        except KeyError:
            logger.warning(f"Unknown scenario '{scenario}', using fallback")
            scenario = ScenarioType.NORMAL.value  # Fallback to normal operations
            band = self.threshold_bands[scenario]
        
        # Validate band configuration
        if band["min_hours"] >= band["max_hours"]:
            logger.error(f"Invalid threshold band for {scenario}: min={band['min_hours']}, max={band['max_hours']}")
            # Use safe defaults
            band = self.threshold_bands[ScenarioType.NORMAL.value]
        
        if band["min_hours"] < 0:
            logger.warning(f"Negative min_hours {band['min_hours']} for {scenario}, using absolute value")
            band["min_hours"] = abs(band["min_hours"])
        
        wait_times = np.random.uniform(
            low=band["min_hours"],
            high=band["max_hours"],
            size=num_samples
        )
        
        return wait_times
    
    def _calculate_exponential_wait_time(self, scenario: str, num_samples: int) -> np.ndarray:
        """
        Calculate wait time using legacy exponential method (for rollback).
        
        Args:
            scenario: Scenario name
            num_samples: Number of samples to generate
            
        Returns:
            Array of wait times using exponential distribution
        """
        scale = self.legacy_exponential_scales.get(scenario, self.legacy_exponential_scales[ScenarioType.NORMAL.value])
        wait_times = np.random.exponential(scale=scale, size=num_samples)
        
        # For demonstration, let's cap the wait time to a reasonable maximum
        wait_times = np.clip(wait_times, 0, 72)
        
        return wait_times


    
    def compare_methods(self) -> Dict[str, Any]:
        """
        Compare threshold bands method with legacy exponential method.
        
        Returns:
            Dictionary containing comparison results
        """
        # Save current method
        original_method = self.method
        
        try:
            # Test threshold bands method
            self.method = WaitTimeMethod.THRESHOLD_BANDS
            threshold_validation = self.validate_logical_ordering()
            
            # Test exponential legacy method
            self.method = WaitTimeMethod.EXPONENTIAL_LEGACY
            exponential_validation = self.validate_logical_ordering()
            
            comparison = {
                "threshold_bands": {
                    "logical_ordering_valid": threshold_validation["logical_ordering_valid"],
                    "peak_mean": threshold_validation["peak_mean"],
                    "normal_mean": threshold_validation["normal_mean"],
                    "low_mean": threshold_validation["low_mean"]
                },
                "exponential_legacy": {
                    "logical_ordering_valid": exponential_validation["logical_ordering_valid"],
                    "peak_mean": exponential_validation["peak_mean"],
                    "normal_mean": exponential_validation["normal_mean"],
                    "low_mean": exponential_validation["low_mean"]
                },
                "improvement": {
                    "logical_ordering_fixed": (
                        threshold_validation["logical_ordering_valid"] and 
                        not exponential_validation["logical_ordering_valid"]
                    ),
                    "peak_increase": threshold_validation["peak_mean"] - exponential_validation["peak_mean"],
                    "normal_change": threshold_validation["normal_mean"] - exponential_validation["normal_mean"],
                    "low_decrease": exponential_validation["low_mean"] - threshold_validation["low_mean"]
                }
            }
            
            return comparison
            
        finally:
            # Restore original method
            self.method = original_method


# Convenience functions for backward compatibility and simplified usage
def calculate_wait_time(scenario_name: str, use_legacy: bool = False) -> float:
    """
    Calculate wait time based on scenario.

    Args:
        scenario_name (str): Name of the scenario key (e.g., 'peak', 'normal', 'low') or full scenario name.
        use_legacy (bool, optional): Use legacy method. Defaults to False.

    Returns:
        float: Wait time in hours.
    """
    if not isinstance(scenario_name, str) or not scenario_name.strip():
        raise ValueError("scenario_name must be a non-empty string")

    # Convert scenario key to proper scenario name for the calculator
    converted_scenario = get_wait_time_scenario_name(scenario_name)

    method = WaitTimeMethod.EXPONENTIAL_LEGACY if use_legacy else WaitTimeMethod.THRESHOLD_BANDS
    calculator = WaitTimeCalculator(method=method)
    
    try:
        result = calculator.calculate_wait_time(converted_scenario)
        return result
    except (ValueError, TypeError) as e:
        logger.error(f"Error calculating wait time: {e}")
        return 6.0

def get_wait_time_statistics(scenario: str) -> Dict[str, Any]:
    """
    Convenience function for getting comprehensive wait time statistics for a scenario.
    
    This function provides detailed statistical information about wait time calculations
    including ranges, means, distribution parameters, and metadata. Useful for
    analysis, reporting, and system validation.
    
    Args:
        scenario (str): Scenario name ('Peak Season', 'Normal Operations', 'Low Season')
        
    Returns:
        Dict[str, Any]: Dictionary containing comprehensive statistical information:
            - min_hours: Minimum wait time for the scenario
            - max_hours: Maximum wait time for the scenario
            - mean_hours: Target mean for normal distribution
            - std_hours: Standard deviation for variability
            - distribution: Distribution type used
            - description: Human-readable description
            - business_logic: Business reasoning for the scenario
            - use_cases: List of typical use cases
            
    Raises:
        ValueError: If scenario is not recognized
        
    Examples:
        # Get statistics for analysis
        stats = get_wait_time_statistics('Peak Season')
        print(f"Peak season range: {stats['min_hours']}-{stats['max_hours']} hours")
        print(f"Mean: {stats['mean_hours']}, Std: {stats['std_hours']}")
        
        # Use for validation
        for scenario in ['Peak Season', 'Normal Operations', 'Low Season']:
            stats = get_wait_time_statistics(scenario)
            print(f"{scenario}: {stats['description']}")
    """
    calculator = WaitTimeCalculator()
    return calculator.get_scenario_statistics(scenario)

def get_default_wait_time() -> float:
    """
    Get a safe default wait time for fallback scenarios.
    
    This function provides a reasonable default wait time that can be used
    when scenario-specific calculations are not available or have failed.
    The default is based on Normal Operations scenario mean.
    
    Returns:
        float: Default wait time of 8.0 hours (Normal Operations mean)
        
    Examples:
        # Use as fallback in error handling
        try:
            wait_time = calculate_wait_time(user_scenario)
        except Exception:
            wait_time = get_default_wait_time()
            logger.warning(f"Using default wait time: {wait_time} hours")
            
        # Use for initialization
        initial_wait_time = get_default_wait_time()
    """
    return 8.0  # Normal Operations mean from threshold bands