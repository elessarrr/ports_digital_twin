"""Tests for Sample Data Generator

This module tests the sample data generation functionality.
"""

import unittest
import pandas as pd
import sys
import os

from hk_port_digital_twin.utils.sample_data_generator import generate_sample_vessel_data


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
        required_columns = ['ship_id', 'vessel_name', 'vessel_type', 'port_of_origin', 
                          'destination_port', 'arrival_time', 'berth_time', 'departure_time']
        for col in required_columns:
            self.assertIn(col, ships_df.columns)
        
        # Check data types and ranges
        self.assertTrue(all(ships_df['vessel_type'].isin(['Container Ship', 'Bulk Carrier'])))
    

if __name__ == '__main__':
    unittest.main()