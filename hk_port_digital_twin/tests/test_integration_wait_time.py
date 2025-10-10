"""
Integration tests for wait time calculator with the broader system.

This module tests the integration of the wait time calculator with:
- Streamlit dashboard components
- Data pipeline integration
- Cross-module compatibility
- End-to-end functionality

Comments for context:
This integration test suite verifies that the enhanced wait time calculator
works correctly within the broader port digital twin system. It tests the
integration points with the dashboard, ensures data flows correctly, and
validates that the new threshold-based system maintains compatibility with
existing components.
"""

import unittest
import sys
import os
import numpy as np
from unittest.mock import patch, MagicMock
import importlib.util

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from utils.wait_time_calculator import WaitTimeCalculator, calculate_wait_time
    WAIT_TIME_AVAILABLE = True
except ImportError:
    WAIT_TIME_AVAILABLE = False
    WaitTimeCalculator = None
    calculate_wait_time = None


class TestWaitTimeCalculatorIntegration(unittest.TestCase):
    """Integration tests for wait time calculator with the broader system."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not WAIT_TIME_AVAILABLE:
            self.skipTest("Wait time calculator not available")
        self.calculator = WaitTimeCalculator()
    
    def test_dashboard_integration_import(self):
        """Test that the dashboard can import wait time calculator components."""
        # Test importing from dashboard context
        dashboard_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'dashboard', 'streamlit_app.py')
        
        if os.path.exists(dashboard_path):
            # Verify the import statements work
            with open(dashboard_path, 'r') as f:
                content = f.read()
                self.assertIn('wait_time_calculator', content)
                self.assertIn('WaitTimeCalculator', content)
                self.assertIn('calculate_wait_time', content)
    
    def test_scenario_compatibility_with_dashboard(self):
        """Test that scenario names are compatible with dashboard expectations."""
        # These are the scenarios expected by the dashboard
        dashboard_scenarios = ['Peak Season', 'Normal Operations', 'Low Season']
        
        for scenario in dashboard_scenarios:
            with self.subTest(scenario=scenario):
                # Should not raise any exceptions
                result = self.calculator.calculate_wait_time(scenario)
                self.assertIsInstance(result, (int, float))
                self.assertGreaterEqual(result, 0.1)
                self.assertLessEqual(result, 100)
    
    def test_multiplier_integration(self):
        """Test that multiplier functionality works as expected by dashboard."""
        base_scenario = 'Normal Operations'
        multipliers = [0.5, 1.0, 1.5, 2.0, 3.0]
        
        results = []
        for multiplier in multipliers:
            result = self.calculator.calculate_wait_time(base_scenario, multiplier=multiplier)
            results.append(result)
            
            # Verify result is reasonable
            self.assertIsInstance(result, (int, float))
            self.assertGreaterEqual(result, 0.1)
            self.assertLessEqual(result, 100)
        
        # Results should generally increase with multiplier (allowing for randomness)
        # Test that higher multipliers don't produce unreasonably low results
        self.assertGreaterEqual(results[-1], results[0])  # 3.0x should be >= 0.5x
    
    def test_batch_calculation_for_dashboard_charts(self):
        """Test batch calculation functionality used by dashboard charts."""
        scenario = 'Normal Operations'
        sample_sizes = [10, 50, 100, 1000]
        
        for size in sample_sizes:
            with self.subTest(sample_size=size):
                results = self.calculator.calculate_wait_time(scenario, num_samples=size)
                
                # Should return numpy array for multiple samples
                self.assertIsInstance(results, np.ndarray)
                self.assertEqual(len(results), size)
                
                # All values should be reasonable
                for value in results:
                    self.assertGreaterEqual(value, 0.1)
                    self.assertLessEqual(value, 100)
                
                # Should have some variability (not all identical)
                if size >= 10:
                    self.assertGreater(np.std(results), 0)
    
    def test_error_handling_integration(self):
        """Test error handling works correctly in integration context."""
        # Test invalid scenario handling
        with self.assertRaises(ValueError):
            self.calculator.calculate_wait_time('Invalid Scenario')
        
        # Test invalid multiplier handling
        with self.assertRaises(ValueError):
            self.calculator.calculate_wait_time('Normal Operations', multiplier=-1.0)
        
        # Test invalid num_samples handling
        with self.assertRaises(ValueError):
            self.calculator.calculate_wait_time('Normal Operations', num_samples=0)
    
    def test_standalone_function_integration(self):
        """Test that the standalone function works for simple dashboard usage."""
        # Test basic functionality
        result = calculate_wait_time('Normal Operations')
        self.assertIsInstance(result, (int, float))
        self.assertGreaterEqual(result, 0.1)
        self.assertLessEqual(result, 100)
        
        # Test with legacy flag
        result_legacy = calculate_wait_time('Peak Season', use_legacy=True)
        self.assertIsInstance(result_legacy, (int, float))
        self.assertGreaterEqual(result_legacy, 0.1)
        self.assertLessEqual(result_legacy, 100)
    
    def test_logical_ordering_consistency(self):
        """Test that logical ordering is maintained across multiple calls."""
        sample_size = 100
        
        # Generate multiple samples for each scenario
        peak_samples = [self.calculator.calculate_wait_time('Peak Season') for _ in range(sample_size)]
        normal_samples = [self.calculator.calculate_wait_time('Normal Operations') for _ in range(sample_size)]
        low_samples = [self.calculator.calculate_wait_time('Low Season') for _ in range(sample_size)]
        
        # Calculate means
        peak_mean = np.mean(peak_samples)
        normal_mean = np.mean(normal_samples)
        low_mean = np.mean(low_samples)
        
        # Verify logical ordering: Peak > Normal > Low
        self.assertGreater(peak_mean, normal_mean, 
                          f"Peak mean ({peak_mean:.2f}) should be > Normal mean ({normal_mean:.2f})")
        self.assertGreater(normal_mean, low_mean,
                          f"Normal mean ({normal_mean:.2f}) should be > Low mean ({low_mean:.2f})")
    
    def test_performance_for_dashboard_usage(self):
        """Test performance characteristics suitable for dashboard usage."""
        import time
        
        # Test single calculation performance (for real-time updates)
        start_time = time.time()
        for _ in range(100):
            self.calculator.calculate_wait_time('Normal Operations')
        single_calc_time = time.time() - start_time
        
        # Should complete 100 calculations quickly (< 0.5 seconds)
        self.assertLess(single_calc_time, 0.5)
        
        # Test batch calculation performance (for charts)
        start_time = time.time()
        for _ in range(10):
            self.calculator.calculate_wait_time('Normal Operations', num_samples=100)
        batch_calc_time = time.time() - start_time
        
        # Should complete batch calculations reasonably quickly (< 1 second)
        self.assertLess(batch_calc_time, 1.0)
    
    def test_memory_usage_stability(self):
        """Test that repeated calculations don't cause memory issues."""
        # Perform many calculations to test for memory leaks
        for i in range(1000):
            result = self.calculator.calculate_wait_time('Normal Operations')
            self.assertIsInstance(result, (int, float))
            
            # Occasionally test batch calculations
            if i % 100 == 0:
                batch_result = self.calculator.calculate_wait_time('Peak Season', num_samples=50)
                self.assertIsInstance(batch_result, np.ndarray)
                self.assertEqual(len(batch_result), 50)


class TestCrossModuleCompatibility(unittest.TestCase):
    """Test compatibility with other modules in the system."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not WAIT_TIME_AVAILABLE:
            self.skipTest("Wait time calculator not available")
    
    def test_numpy_compatibility(self):
        """Test compatibility with numpy operations used elsewhere."""
        calculator = WaitTimeCalculator()
        
        # Generate array of wait times
        wait_times = calculator.calculate_wait_time('Normal Operations', num_samples=100)
        
        # Test common numpy operations that might be used in other modules
        mean_time = np.mean(wait_times)
        std_time = np.std(wait_times)
        max_time = np.max(wait_times)
        min_time = np.min(wait_times)
        
        # Verify results are reasonable
        self.assertGreater(mean_time, 0)
        self.assertGreater(std_time, 0)
        self.assertGreaterEqual(min_time, 0.1)
        self.assertLessEqual(max_time, 100)
    
    def test_json_serialization_compatibility(self):
        """Test that results can be serialized for API/dashboard usage."""
        import json
        
        calculator = WaitTimeCalculator()
        
        # Test single value serialization
        single_result = calculator.calculate_wait_time('Normal Operations')
        json_single = json.dumps(float(single_result))
        self.assertIsInstance(json.loads(json_single), float)
        
        # Test array serialization
        array_result = calculator.calculate_wait_time('Normal Operations', num_samples=10)
        json_array = json.dumps(array_result.tolist())
        loaded_array = json.loads(json_array)
        self.assertIsInstance(loaded_array, list)
        self.assertEqual(len(loaded_array), 10)


if __name__ == '__main__':
    # Run the integration tests
    unittest.main(verbosity=2)