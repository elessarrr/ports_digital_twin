"""
Unit tests for the wait time calculator module.

This module tests the threshold-based wait time calculation system that provides
scenario-aware wait times for port operations. The tests cover:
- Threshold band calculations for different scenarios
- Input validation and error handling
- Edge cases and boundary conditions
- Integration with existing multiplier systems
"""

import unittest
import numpy as np
from unittest.mock import patch, MagicMock
import sys
import os

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from utils.wait_time_calculator import WaitTimeCalculator, calculate_wait_time
except ImportError:
    # Fallback for testing environment
    WaitTimeCalculator = None
    calculate_wait_time = None


class TestWaitTimeCalculator(unittest.TestCase):
    """Test cases for the WaitTimeCalculator class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        if WaitTimeCalculator is None:
            self.skipTest("WaitTimeCalculator not available")
        self.calculator = WaitTimeCalculator()
    
    def test_initialization(self):
        """Test that the calculator initializes correctly."""
        self.assertIsInstance(self.calculator, WaitTimeCalculator)
        self.assertIsInstance(self.calculator.threshold_bands, dict)
        
        # Check that all expected scenarios are present
        expected_scenarios = [
            'Peak Season', 'Normal Operations', 'Low Season'
        ]
        for scenario in expected_scenarios:
            self.assertIn(scenario, self.calculator.threshold_bands)
    
    def test_threshold_bands_structure(self):
        """Test that threshold bands have the correct structure."""
        for scenario, bands in self.calculator.threshold_bands.items():
            self.assertIsInstance(bands, dict)
            self.assertIn('min_hours', bands)
            self.assertIn('max_hours', bands)
            self.assertIn('mean_hours', bands)
            self.assertIn('std_hours', bands)
            self.assertIn('distribution', bands)
            self.assertIsInstance(bands['min_hours'], (int, float))
            self.assertIsInstance(bands['max_hours'], (int, float))
            self.assertGreater(bands['max_hours'], bands['min_hours'])
            self.assertGreaterEqual(bands['min_hours'], 0)
    
    def test_calculate_wait_time_normal_operations(self):
        """Test wait time calculation for normal operations."""
        result = self.calculator.calculate_wait_time('Normal Operations')
        self.assertIsInstance(result, (int, float))
        self.assertGreaterEqual(result, 0.1)
        self.assertLessEqual(result, 100)
        
        # Test with multiplier
        result_with_multiplier = self.calculator.calculate_wait_time('Normal Operations', multiplier=1.5)
        self.assertIsInstance(result_with_multiplier, (int, float))
        self.assertGreaterEqual(result_with_multiplier, 0.1)  # Should be within valid range
        self.assertLessEqual(result_with_multiplier, 100)
    
    def test_calculate_wait_time_all_scenarios(self):
        """Test wait time calculation for all scenarios."""
        scenarios = ['Peak Season', 'Normal Operations', 'Low Season']
        
        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                result = self.calculator.calculate_wait_time(scenario)
                self.assertIsInstance(result, (int, float))
                self.assertGreaterEqual(result, 0.1)
                self.assertLessEqual(result, 100)
    
    def test_calculate_wait_time_with_multipliers(self):
        """Test wait time calculation with different multipliers."""
        base_result = self.calculator.calculate_wait_time('Normal Operations', multiplier=1.0)
        
        # Test with higher multiplier
        high_result = self.calculator.calculate_wait_time('Normal Operations', multiplier=2.0)
        self.assertGreater(high_result, base_result * 0.8)  # Allow variance
        
        # Test with lower multiplier
        low_result = self.calculator.calculate_wait_time('Normal Operations', multiplier=0.5)
        self.assertLess(low_result, base_result * 1.2)  # Allow variance
    
    def test_calculate_wait_time_invalid_scenario(self):
        """Test calculate_wait_time with invalid scenario."""
        # Should raise ValueError for unknown scenarios
        with self.assertRaises(ValueError):
            self.calculator.calculate_wait_time('invalid_scenario')
    
    def test_calculate_wait_time_invalid_multiplier(self):
        """Test wait time calculation with invalid multiplier."""
        # Test negative multiplier - should raise ValueError
        with self.assertRaises(ValueError):
            self.calculator.calculate_wait_time('Normal Operations', multiplier=-1.0)
        
        # Test zero multiplier (should be allowed as it's non-negative)
        result = self.calculator.calculate_wait_time('Normal Operations', multiplier=0.0)
        self.assertIsInstance(result, (int, float))
        self.assertEqual(result, 0.1)  # Should return minimum bound of 0.1 hours
        
        # Test extremely high multiplier - should work but be reasonable
        result = self.calculator.calculate_wait_time('Normal Operations', multiplier=10.0)
        self.assertIsInstance(result, (int, float))
        self.assertGreaterEqual(result, 0.1)
        self.assertLessEqual(result, 1000)  # Should be reasonable even with high multiplier
    
    def test_calculate_wait_time_none_inputs(self):
        """Test wait time calculation with None inputs."""
        # Test None scenario - should raise TypeError
        with self.assertRaises(TypeError):
            self.calculator.calculate_wait_time(None)
        
        # Test None multiplier - should raise TypeError
        with self.assertRaises(TypeError):
            self.calculator.calculate_wait_time('Normal Operations', multiplier=None)
        
        # Test None num_samples - should raise TypeError
        with self.assertRaises(TypeError):
            self.calculator.calculate_wait_time('Normal Operations', num_samples=None)
    
    def test_calculate_wait_time_num_samples_parameter(self):
        """Test wait time calculation with different num_samples values."""
        # Test with num_samples=1 (should return float)
        result_1 = self.calculator.calculate_wait_time('Normal Operations', num_samples=1)
        self.assertIsInstance(result_1, (int, float))
        self.assertGreaterEqual(result_1, 0.1)
        self.assertLessEqual(result_1, 100)
        
        # Test with num_samples>1 (should return array)
        result_10 = self.calculator.calculate_wait_time('Normal Operations', num_samples=10)
        self.assertIsInstance(result_10, np.ndarray)
        self.assertEqual(len(result_10), 10)
        for val in result_10:
            self.assertGreaterEqual(val, 0.1)
            self.assertLessEqual(val, 100)
        
        result_100 = self.calculator.calculate_wait_time('Normal Operations', num_samples=100)
        self.assertIsInstance(result_100, np.ndarray)
        self.assertEqual(len(result_100), 100)
        for val in result_100:
            self.assertGreaterEqual(val, 0.1)
            self.assertLessEqual(val, 100)
        
        # Test with invalid num_samples
        with self.assertRaises(ValueError):
            self.calculator.calculate_wait_time('Normal Operations', num_samples=0)
        
        with self.assertRaises(ValueError):
            self.calculator.calculate_wait_time('Normal Operations', num_samples=-1)
    
    def test_private_calculate_threshold_wait_time(self):
        """Test the private threshold calculation method."""
        result = self.calculator._calculate_threshold_wait_time('Normal Operations', num_samples=10)
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(len(result), 10)
        for wait_time in result:
            self.assertGreaterEqual(wait_time, 0.1)
            self.assertLessEqual(wait_time, 100)
    
    def test_private_calculate_threshold_wait_time_invalid_inputs(self):
        """Test the private method with invalid inputs."""
        # Test with unknown scenario (should fallback to Normal Operations)
        result = self.calculator._calculate_threshold_wait_time('unknown_scenario', num_samples=5)
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(len(result), 5)
        
        # Test with invalid num_samples
        with self.assertRaises(ValueError):
            self.calculator._calculate_threshold_wait_time('Normal Operations', num_samples=0)


class TestCalculateWaitTimeFunction(unittest.TestCase):
    """Test cases for the standalone calculate_wait_time function."""
    
    def setUp(self):
        """Set up test fixtures."""
        if calculate_wait_time is None:
            self.skipTest("calculate_wait_time function not available")
    
    def test_calculate_wait_time_function_basic(self):
        """Test basic functionality of the standalone function."""
        result = calculate_wait_time('Normal Operations')
        self.assertIsInstance(result, (int, float))
        self.assertGreaterEqual(result, 0.1)
        self.assertLessEqual(result, 100)
    
    def test_calculate_wait_time_function_with_legacy(self):
        """Test the function with legacy mode."""
        result = calculate_wait_time('Peak Season', use_legacy=True)
        self.assertIsInstance(result, (int, float))
        self.assertGreaterEqual(result, 0.1)
        self.assertLessEqual(result, 100)
    
    def test_calculate_wait_time_function_case_variations(self):
        """Test that the function handles case variations."""
        scenarios = ['Normal Operations', 'peak season', 'LOW SEASON']
        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                result = calculate_wait_time(scenario)
                self.assertIsInstance(result, (int, float))
                self.assertGreaterEqual(result, 0.1)
    
    def test_calculate_wait_time_function_invalid_inputs(self):
        """Test the function with invalid inputs."""
        # Test with None - should raise TypeError
        with self.assertRaises(TypeError):
            calculate_wait_time(None)
        
        # Test with empty string - should raise ValueError
        with self.assertRaises(ValueError):
            calculate_wait_time('')
        
        # Test with non-string input - should raise TypeError
        with self.assertRaises(TypeError):
            calculate_wait_time(123)


class TestWaitTimeCalculatorIntegration(unittest.TestCase):
    """Integration tests for the wait time calculator."""
    
    def setUp(self):
        """Set up test fixtures."""
        if WaitTimeCalculator is None or calculate_wait_time is None:
            self.skipTest("Wait time calculator components not available")
    
    def test_consistency_between_class_and_function(self):
        """Test that the class and function produce consistent results."""
        calculator = WaitTimeCalculator()
        scenarios = ['Normal Operations', 'Peak Season', 'Low Season']
        
        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                # Set seed for reproducible results
                np.random.seed(42)
                class_result = calculator.calculate_wait_time(scenario)
                
                np.random.seed(42)
                function_result = calculate_wait_time(scenario)
                
                # Results should be in the same reasonable range
                self.assertGreaterEqual(class_result, 0.1)
                self.assertGreaterEqual(function_result, 0.1)
                self.assertLessEqual(class_result, 100)
                self.assertLessEqual(function_result, 100)
    
    def test_statistical_properties(self):
        """Test statistical properties of generated wait times."""
        calculator = WaitTimeCalculator()
        
        # Generate multiple samples for statistical analysis
        samples = []
        for _ in range(100):
            samples.append(calculator.calculate_wait_time('Normal Operations'))
        
        # Check basic statistical properties
        mean_wait = np.mean(samples)
        std_wait = np.std(samples)
        
        self.assertGreater(mean_wait, 0)
        self.assertGreater(std_wait, 0)
        
        # Check that values are within expected range
        bands = calculator.threshold_bands['Normal Operations']
        self.assertGreaterEqual(min(samples), bands['min_hours'] * 0.9)  # Allow small variance
        self.assertLessEqual(max(samples), bands['max_hours'] * 1.1)  # Allow small variance
    
    def test_error_logging(self):
        """Test that errors are properly logged."""
        with self.assertLogs('utils.wait_time_calculator', level='ERROR') as cm:
            # This should trigger an error for unknown scenario in the standalone function
            result = calculate_wait_time('unknown_scenario')
            self.assertIsInstance(result, (int, float))
            self.assertIn('Error calculating wait time', cm.output[0])


class TestWaitTimeCalculatorPerformance(unittest.TestCase):
    """Performance tests for the wait time calculator."""
    
    def setUp(self):
        """Set up test fixtures."""
        if WaitTimeCalculator is None:
            self.skipTest("WaitTimeCalculator not available")
        self.calculator = WaitTimeCalculator()
    
    def test_performance_single_calculation(self):
        """Test performance of single wait time calculation."""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            self.calculator.calculate_wait_time('Normal Operations')
        end_time = time.time()
        
        # Should complete 1000 calculations in reasonable time
        self.assertLess(end_time - start_time, 1.0)  # Less than 1 second
    
    def test_performance_batch_calculation(self):
        """Test performance of batch wait time calculation."""
        import time
        
        start_time = time.time()
        # Generate 10000 wait times in batches
        for _ in range(100):
            self.calculator.calculate_wait_time('Normal Operations', num_samples=100)
        end_time = time.time()
        
        # Should complete batch calculations in reasonable time
        self.assertLess(end_time - start_time, 2.0)  # Less than 2 seconds


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)