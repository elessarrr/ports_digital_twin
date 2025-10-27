"""
Data pipeline for loading, preprocessing, and caching data.
"""

import pandas as pd
from hk_port_digital_twin.dashboard.data.vessel_data_loader import VesselDataLoader
from hk_port_digital_twin.utils.scenario_caching import cache_scenario_result, get_cached_scenario_result

class DataPipeline:
    """
    A data pipeline for loading, preprocessing, and caching data.
    """

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.vessel_data_loader = VesselDataLoader(data_path)

    def run(self) -> pd.DataFrame:
        """
        Runs the data pipeline.
        """
        # Try to get the data from the cache
        cached_data = get_cached_scenario_result("vessel_data")
        if cached_data is not None:
            return cached_data

        # If the data is not in the cache, load it
        data = self.vessel_data_loader.load_vessel_data()

        # Preprocess the data
        data = self._preprocess_data(data)

        # Cache the data
        cache_scenario_result("vessel_data", data)

        return data

    def _preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocesses the data.
        """
        if data.empty:
            return data
        # Fill missing values
        data["vessel_name"] = data["vessel_name"].fillna("Unknown")
        data["arrival_time"] = pd.to_datetime(data["arrival_time"], errors='coerce').fillna(pd.Timestamp.now())
        data["departure_time"] = pd.to_datetime(data["departure_time"], errors='coerce').fillna(pd.Timestamp.now())


        return data