"""
Unit tests for the wait time calculator module.

This module tests the threshold-based wait time calculation system that provides
scenario-aware wait times for port operations. The tests cover:
- Threshold band calculations for different scenarios
- Input validation and error handling
- Edge cases and boundary conditions
"""

import unittest
import numpy as np
from unittest.mock import patch, MagicMock
import sys
import os

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from hk_port_digital_twin.src.utils.wait_time_calculator import WaitTimeCalculator, calculate_wait_time, ScenarioType
except ImportError:
    # Fallback for testing environment
    WaitTimeCalculator = None
    calculate_wait_time = None
    ScenarioType = None


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
            ScenarioType.PEAK.value, ScenarioType.NORMAL.value, ScenarioType.LOW.value
        ]
        for scenario in expected_scenarios:
            self.assertIn(scenario, self.calculator.threshold_bands)

    def test_threshold_bands_structure(self):
        """Test that threshold bands have the correct structure."""
        for scenario, bands in self.calculator.threshold_bands.items():
            self.assertIsInstance(bands, dict)
            self.assertIn('min_hours', bands)
            self.assertIn('max_hours', bands)
            self.assertIsInstance(bands['min_hours'], (int, float))
            self.assertIsInstance(bands['max_hours'], (int, float))
            self.assertGreater(bands['max_hours'], bands['min_hours'])
            self.assertGreaterEqual(bands['min_hours'], 0)

    def test_calculate_wait_time_normal_operations(self):
        """Test wait time calculation for normal operations."""
        result = self.calculator.calculate_wait_time(ScenarioType.NORMAL.value)
        self.assertIsInstance(result, (int, float))
        self.assertGreaterEqual(result, 0.1)
        self.assertLessEqual(result, 100)

    def test_calculate_wait_time_all_scenarios(self):
        """Test wait time calculation for all scenarios."""
        scenarios = [ScenarioType.PEAK.value, ScenarioType.NORMAL.value, ScenarioType.LOW.value]

        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                result = self.calculator.calculate_wait_time(scenario)
                self.assertIsInstance(result, (int, float))
                self.assertGreaterEqual(result, 0.1)
                self.assertLessEqual(result, 100)

    def test_calculate_wait_time_invalid_scenario(self):
        """Test calculate_wait_time with invalid scenario."""
        with self.assertRaises(ValueError):
            self.calculator.calculate_wait_time('invalid_scenario')

    def test_calculate_wait_time_none_inputs(self):
        """Test wait time calculation with None inputs."""
        with self.assertRaises(ValueError):
            self.calculator.calculate_wait_time(None)

        with self.assertRaises(ValueError):
            self.calculator.calculate_wait_time('')

    def test_calculate_wait_time_num_samples_parameter(self):
        """Test wait time calculation with different num_samples values."""
        result_1 = self.calculator.calculate_wait_time(ScenarioType.NORMAL.value, num_samples=1)
        self.assertIsInstance(result_1, (int, float))

        result_10 = self.calculator.calculate_wait_time(ScenarioType.NORMAL.value, num_samples=10)
        self.assertIsInstance(result_10, np.ndarray)
        self.assertEqual(len(result_10), 10)

        with self.assertRaises(ValueError):
            self.calculator.calculate_wait_time(ScenarioType.NORMAL.value, num_samples=0)

        with self.assertRaises(ValueError):
            self.calculator.calculate_wait_time(ScenarioType.NORMAL.value, num_samples=-1)


class TestCalculateWaitTimeFunction(unittest.TestCase):
    """Test cases for the standalone calculate_wait_time function."""

    def setUp(self):
        """Set up test fixtures."""
        if calculate_wait_time is None:
            self.skipTest("calculate_wait_time function not available")

    def test_calculate_wait_time_function_basic(self):
        """Test basic functionality of the standalone function."""
        result = calculate_wait_time(ScenarioType.NORMAL.value)
        self.assertIsInstance(result, (int, float))

    def test_calculate_wait_time_function_with_legacy(self):
        """Test the function with legacy mode."""
        result = calculate_wait_time(ScenarioType.PEAK.value, use_legacy=True)
        self.assertIsInstance(result, (int, float))

    def test_calculate_wait_time_function_invalid_inputs(self):
        """Test the function with invalid inputs."""
        with self.assertRaises(ValueError):
            calculate_wait_time(None)

        with self.assertRaises(ValueError):
            calculate_wait_time('')


if __name__ == '__main__':
    unittest.main(verbosity=2)