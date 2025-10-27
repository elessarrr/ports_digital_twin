"""
Computation Optimizer for Streamlit Dashboard Performance

This module provides optimized computation functions using vectorization,
parallel processing, and efficient algorithms to improve dashboard performance.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional, Union
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
from functools import lru_cache, wraps
import time
import logging

logger = logging.getLogger(__name__)


class VectorizedOptimizer:
    """Vectorized optimization calculations for improved performance."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize the optimizer with optional random seed."""
        self.rng = np.random.RandomState(seed)
        self._cache = {}
    
    def generate_optimization_results_vectorized(
        self, 
        objective: str, 
        weights: Dict[str, float], 
        constraints: Dict[str, Any],
        num_scenarios: int = 4
    ) -> Dict[str, Any]:
        """
        Generate optimization results using vectorized operations.
        
        Args:
            objective: Optimization objective
            weights: Scenario weights
            constraints: Operational constraints
            num_scenarios: Number of scenarios to process
            
        Returns:
            Optimization results dictionary
        """
        # Create deterministic seed from inputs
        seed_str = f"{objective}_{sorted(weights.items())}_{sorted(constraints.items())}"
        seed = hash(seed_str) % 2**32
        self.rng = np.random.RandomState(seed)
        
        # Define scenario names
        scenarios = ['normal', 'peak_season', 'maintenance', 'typhoon_season']
        
        # Vectorized base performance calculation
        base_ranges = self._get_objective_ranges_vectorized(objective)
        base_performance = self.rng.uniform(
            base_ranges['min'], 
            base_ranges['max'], 
            size=len(scenarios)
        )
        
        # Vectorized weight adjustments
        weight_values = np.array([weights.get(scenario, 0.25) for scenario in scenarios])
        weight_adjustments = 1 + (weight_values - 0.25) * 0.2
        weighted_performance = np.minimum(0.98, base_performance * weight_adjustments)
        
        # Calculate optimal resources
        optimal_berths, optimal_cranes = self._calculate_optimal_resources_vectorized(objective)
        
        # Apply constraint adjustments
        constraint_factor = self._calculate_constraint_factor_vectorized(
            optimal_berths, optimal_cranes, constraints
        )
        
        # Apply constraints
        if constraints['max_berths'] < optimal_berths:
            optimal_berths = constraints['max_berths']
        if constraints['max_cranes'] < optimal_cranes:
            optimal_cranes = constraints['max_cranes']
        
        # Final performance calculation
        final_performance = weighted_performance * constraint_factor
        objective_value = np.mean(final_performance) * self.rng.uniform(0.95, 1.05)
        
        return {
            'objective': objective,
            'objective_value': round(float(objective_value), 3),
            'optimal_berths': int(optimal_berths),
            'optimal_cranes': int(optimal_cranes),
            'scenario_performance': {
                scenario: round(float(perf), 3) 
                for scenario, perf in zip(scenarios, final_performance)
            },
            'weights_used': weights,
            'constraints_applied': constraints
        }
    
    def _get_objective_ranges_vectorized(self, objective: str) -> Dict[str, np.ndarray]:
        """Get performance ranges for each objective using vectorized operations."""
        ranges_map = {
            "Minimize Total Waiting Time": {
                'min': np.array([0.88, 0.75, 0.82, 0.68]),
                'max': np.array([0.95, 0.85, 0.90, 0.78])
            },
            "Maximize Throughput": {
                'min': np.array([0.90, 0.85, 0.78, 0.70]),
                'max': np.array([0.97, 0.92, 0.88, 0.80])
            },
            "Minimize Costs": {
                'min': np.array([0.85, 0.72, 0.80, 0.65]),
                'max': np.array([0.92, 0.82, 0.87, 0.75])
            }
        }
        
        return ranges_map.get(objective, {
            'min': np.array([0.87, 0.76, 0.81, 0.67]),
            'max': np.array([0.94, 0.86, 0.89, 0.77])
        })
    
    def _calculate_optimal_resources_vectorized(self, objective: str) -> Tuple[int, int]:
        """Calculate optimal berths and cranes using vectorized operations."""
        resource_ranges = {
            "Minimize Total Waiting Time": ((16, 22), (32, 42)),
            "Maximize Throughput": ((18, 25), (35, 45)),
            "Minimize Costs": ((14, 20), (28, 38)),
        }
        
        berth_range, crane_range = resource_ranges.get(objective, ((16, 22), (30, 40)))
        
        optimal_berths = self.rng.randint(berth_range[0], berth_range[1] + 1)
        optimal_cranes = self.rng.randint(crane_range[0], crane_range[1] + 1)
        
        return optimal_berths, optimal_cranes
    
    def _calculate_constraint_factor_vectorized(
        self, 
        optimal_berths: int, 
        optimal_cranes: int, 
        constraints: Dict[str, Any]
    ) -> float:
        """Calculate constraint factor using vectorized operations."""
        factors = np.array([1.0])
        
        if constraints['max_berths'] < optimal_berths:
            factors = np.append(factors, 0.95)
        if constraints['max_cranes'] < optimal_cranes:
            factors = np.append(factors, 0.93)
        
        return np.prod(factors)


class ParallelProcessor:
    """Parallel processing utilities for computation-heavy operations."""
    
    def __init__(self, max_workers: Optional[int] = None):
        """Initialize with optional worker count."""
        self.max_workers = max_workers or min(4, mp.cpu_count())
    
    def process_scenarios_parallel(
        self, 
        scenarios: List[str], 
        processing_func: callable, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process multiple scenarios in parallel.
        
        Args:
            scenarios: List of scenario names
            processing_func: Function to process each scenario
            **kwargs: Additional arguments for processing function
            
        Returns:
            Dictionary of scenario results
        """
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(processing_func, scenario, **kwargs): scenario 
                for scenario in scenarios
            }
            
            results = {}
            for future in futures:
                scenario = futures[future]
                try:
                    results[scenario] = future.result()
                except Exception as e:
                    logger.error(f"Error processing scenario {scenario}: {e}")
                    results[scenario] = None
            
            return results
    
    def batch_calculate_metrics(
        self, 
        data_batches: List[pd.DataFrame], 
        metric_func: callable
    ) -> List[Dict[str, Any]]:
        """
        Calculate metrics for data batches in parallel.
        
        Args:
            data_batches: List of data batches
            metric_func: Function to calculate metrics
            
        Returns:
            List of metric results
        """
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(metric_func, batch) for batch in data_batches]
            results = [future.result() for future in futures]
            
        return results


class MemoryOptimizer:
    """Memory optimization utilities for large datasets."""
    
    @staticmethod
    def optimize_dataframe_memory(df: pd.DataFrame) -> pd.DataFrame:
        """
        Optimize DataFrame memory usage by downcasting numeric types.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Memory-optimized DataFrame
        """
        optimized_df = df.copy()
        
        # Optimize numeric columns
        for col in optimized_df.select_dtypes(include=['int64']).columns:
            optimized_df[col] = pd.to_numeric(optimized_df[col], downcast='integer')
        
        for col in optimized_df.select_dtypes(include=['float64']).columns:
            optimized_df[col] = pd.to_numeric(optimized_df[col], downcast='float')
        
        # Optimize object columns
        for col in optimized_df.select_dtypes(include=['object']).columns:
            if optimized_df[col].nunique() / len(optimized_df) < 0.5:
                optimized_df[col] = optimized_df[col].astype('category')
        
        return optimized_df
    
    @staticmethod
    def chunk_large_dataset(
        df: pd.DataFrame, 
        chunk_size: int = 10000
    ) -> List[pd.DataFrame]:
        """
        Split large DataFrame into smaller chunks for processing.
        
        Args:
            df: Input DataFrame
            chunk_size: Size of each chunk
            
        Returns:
            List of DataFrame chunks
        """
        return [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]


def performance_timer(func):
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
        
        return result
    return wrapper


@lru_cache(maxsize=128)
def cached_calculation(calculation_key: str, *args) -> Any:
    """
    LRU cached calculation for expensive operations.
    
    Args:
        calculation_key: Unique key for the calculation
        *args: Calculation arguments
        
    Returns:
        Cached calculation result
    """
    # This is a placeholder - actual calculations would be implemented
    # based on the calculation_key
    return f"Cached result for {calculation_key} with args {args}"


class BatchProcessor:
    """Batch processing utilities for efficient data operations."""
    
    def __init__(self, batch_size: int = 1000):
        """Initialize with batch size."""
        self.batch_size = batch_size
    
    def process_in_batches(
        self, 
        data: Union[List, pd.DataFrame], 
        processing_func: callable,
        **kwargs
    ) -> List[Any]:
        """
        Process data in batches to optimize memory usage.
        
        Args:
            data: Input data (list or DataFrame)
            processing_func: Function to process each batch
            **kwargs: Additional arguments for processing function
            
        Returns:
            List of batch processing results
        """
        if isinstance(data, pd.DataFrame):
            batches = [
                data[i:i + self.batch_size] 
                for i in range(0, len(data), self.batch_size)
            ]
        else:
            batches = [
                data[i:i + self.batch_size] 
                for i in range(0, len(data), self.batch_size)
            ]
        
        results = []
        for batch in batches:
            try:
                result = processing_func(batch, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing batch: {e}")
                results.append(None)
        
        return results


# Global instances for easy access
vectorized_optimizer = VectorizedOptimizer()
parallel_processor = ParallelProcessor()
memory_optimizer = MemoryOptimizer()
batch_processor = BatchProcessor()


def optimize_computation_performance():
    """
    Main function to apply all computation optimizations.
    
    Returns:
        Dictionary of optimization status
    """
    return {
        'vectorized_optimizer': 'initialized',
        'parallel_processor': f'initialized with {parallel_processor.max_workers} workers',
        'memory_optimizer': 'initialized',
        'batch_processor': f'initialized with batch size {batch_processor.batch_size}',
        'status': 'ready'
    }