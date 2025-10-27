"""
Data processing pipeline for vessel information.
"""

import pandas as pd
from hk_port_digital_twin.dashboard.data.vessel_data_loader import VesselDataLoader

class DataPipeline:
    """
    A class to manage the data processing pipeline for vessel data.
    """

    def __init__(self, file_path):
        """
        Initialize the DataPipeline.

        Args:
            file_path (str): The path to the vessel data.
        """
        self.loader = VesselDataLoader(file_path)
        self.data = None

    def run(self):
        """
        Run the data processing pipeline.
        """
        self.data = self.loader.load_all_vessel_data()
        if self.data is not None:
            self.data = self.preprocess_data(self.data)
        return self.data

    def preprocess_data(self, df):
        """
        Preprocess the vessel data.

        Args:
            df (pd.DataFrame): The input vessel data.

        Returns:
            pd.DataFrame: The preprocessed vessel data.
        """
        # Example preprocessing: convert columns to datetime
        if 'arrival_time' in df.columns:
            df['arrival_time'] = pd.to_datetime(df['arrival_time'], errors='coerce')
        if 'departure_time' in df.columns:
            df['departure_time'] = pd.to_datetime(df['departure_time'], errors='coerce')
        
        return df