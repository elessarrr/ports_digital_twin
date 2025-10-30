"""Tests for Sample Data Generator

This module tests the sample data generation functionality.
"""

import unittest
import pandas as pd
import sys
import os
from datetime import datetime

from hk_port_digital_twin.src.utils.sample_data_generator import generate_sample_vessel_data


class TestSampleDataGenerator(unittest.TestCase):
    """Test cases for sample data generator functions"""

    def test_generate_sample_vessel_data(self):
        """Test generating sample vessel data"""
        num_records = 50
        df = generate_sample_vessel_data(num_records)

        # Check if a DataFrame is returned
        self.assertIsInstance(df, pd.DataFrame)

        # Check if the number of records is correct
        self.assertEqual(len(df), num_records)

        # Check if all expected columns are present
        expected_columns = [
            'vessel_name', 'arrival_time', 'berth_time', 'departure_time',
            'vessel_type', 'port_of_origin', 'destination_port'
        ]
        self.assertListEqual(list(df.columns), expected_columns)

        # Check data types
        self.assertTrue(pd.api.types.is_string_dtype(df['vessel_name']))
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df['arrival_time']))
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df['berth_time']))
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df['departure_time']))
        self.assertTrue(pd.api.types.is_string_dtype(df['vessel_type']))
        self.assertTrue(pd.api.types.is_string_dtype(df['port_of_origin']))
        self.assertTrue(pd.api.types.is_string_dtype(df['destination_port']))

if __name__ == '__main__':
    unittest.main()