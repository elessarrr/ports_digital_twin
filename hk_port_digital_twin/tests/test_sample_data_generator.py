"""Tests for Sample Data Generator

This module tests the sample data generation functionality.
"""

import unittest
import pandas as pd
import sys
import os

from hk_port_digital_twin.src.utils.sample_data_generator import generate_sample_vessel_data


class TestSampleDataGenerator(unittest.TestCase):
    """Test cases for sample data generator functions"""
    
    def test_generate_ship_arrivals(self):
        """Test ship arrivals generation"""
        # Test basic functionality
        ships_df = generate_sample_vessel_data(5)
        
        # Check DataFrame structure
        self.assertIsInstance(ships_df, pd.DataFrame)
        self.assertEqual(len(ships_df), 5)
        
        # Check required columns
        required_columns = ['ship_id', 'ship_name', 'ship_type', 'size_teu', 
                          'arrival_time', 'containers_to_unload', 'containers_to_load']
        for col in required_columns:
            self.assertIn(col, ships_df.columns)
        
        # Check data types and ranges
        self.assertTrue(all(ships_df['ship_type'].isin(['container', 'bulk'])))
        self.assertTrue(all(ships_df['size_teu'] > 0))
        self.assertTrue(all(ships_df['containers_to_unload'] >= 0))
        self.assertTrue(all(ships_df['containers_to_load'] >= 0))
    

if __name__ == '__main__':
    unittest.main()