"""Data Loader for Port Digital Twin

This module provides robust and flexible data loading capabilities for the Hong Kong Port Digital Twin project.
It handles loading of various data sources including real-time APIs, historical datasets, and configuration files.

Key Features:
- Manages configuration for different data sources.
- Provides a unified interface for loading both real-time and historical data.
- Implements caching to optimize data retrieval performance.
- Supports data transformation and preprocessing.

Main Components:
- `ConfigManager`: Manages data source configurations.
- `DataLoader`: Main class for data loading operations.
- `DataCache`: In-memory cache for frequently accessed data.
"""

import os
import yaml
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages data source configurations."""
    
    def __init__(self, config_path: str = 'hk_port_digital_twin/src/config/api_config.yml'):
        """
        Initializes the ConfigManager.

        Args:
            config_path: Path to the configuration file.
        """
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Loads the configuration from a YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info("Configuration loaded successfully.")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found at {self.config_path}")
            return {}
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return {}

    def get_api_endpoint(self, endpoint_name: str) -> Optional[str]:
        """
        Gets the URL for a specific API endpoint.

        Args:
            endpoint_name: The name of the endpoint.

        Returns:
            The URL of the endpoint, or None if not found.
        """
        return self.config.get('api_endpoints', {}).get(endpoint_name)

class DataCache:
    """In-memory cache for frequently accessed data."""
    
    def __init__(self, max_size: int = 100):
        """
        Initializes the DataCache.

        Args:
            max_size: Maximum number of items to store in the cache.
        """
        self.cache = {}
        self.max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves an item from the cache.

        Args:
            key: The key of the item to retrieve.

        Returns:
            The cached item, or None if not found.
        """
        return self.cache.get(key)

    def set(self, key: str, value: Any):
        """
        Adds an item to the cache.

        Args:
            key: The key of the item to add.
            value: The item to add to the cache.
        """
        if len(self.cache) >= self.max_size:
            # Simple FIFO eviction strategy
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[key] = value

class DataLoader:
    """Main class for data loading operations."""
    
    def __init__(self, config_manager: ConfigManager, cache: DataCache):
        """
        Initializes the DataLoader.

        Args:
            config_manager: An instance of ConfigManager.
            cache: An instance of DataCache.
        """
        self.config_manager = config_manager
        self.cache = cache

    def load_data(self, source_name: str, **kwargs) -> Optional[Any]:
        """
        Loads data from a specified source.

        Args:
            source_name: The name of the data source to load from.
            **kwargs: Additional arguments for the data loading function.

        Returns:
            The loaded data, or None if loading fails.
        """
        cache_key = f"{source_name}_{str(kwargs)}"
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"Loading data from cache: {source_name}")
            return cached_data

        logger.info(f"Loading data from source: {source_name}")
        if source_name == "cargo_throughput":
            data = self._load_cargo_throughput(**kwargs)
        elif source_name == "vessel_arrivals":
            data = self._load_vessel_arrivals(**kwargs)
        else:
            logger.warning(f"Unknown data source: {source_name}")
            data = None
        
        if data is not None:
            self.cache.set(cache_key, data)
            
        return data

    def _load_cargo_throughput(self, from_date: str, to_date: str) -> Optional[pd.DataFrame]:
        """Loads cargo throughput data from the API."""
        endpoint = self.config_manager.get_api_endpoint("cargo_throughput")
        if not endpoint:
            return None
        
        # In a real implementation, this would make an API call.
        # For this example, we generate synthetic data.
        logger.info(f"Fetching cargo throughput from {endpoint} for {from_date} to {to_date}")
        return self._generate_synthetic_cargo_data(from_date, to_date)

    def _load_vessel_arrivals(self, from_date: str, to_date: str) -> Optional[pd.DataFrame]:
        """Loads vessel arrival data from the API."""
        endpoint = self.config_manager.get_api_endpoint("vessel_arrivals")
        if not endpoint:
            return None
            
        logger.info(f"Fetching vessel arrivals from {endpoint} for {from_date} to {to_date}")
        return self._generate_synthetic_vessel_data(from_date, to_date)

    def _generate_synthetic_cargo_data(self, from_date: str, to_date: str) -> pd.DataFrame:
        """Generates synthetic cargo throughput data for demonstration."""
        dates = pd.date_range(start=from_date, end=to_date, freq='MS')
        data = {
            'Date': dates,
            'TotalTEUs': [1800000 + (i % 12) * 50000 for i in range(len(dates))],
            'IncomingTEUs': [900000 + (i % 12) * 25000 for i in range(len(dates))],
            'OutgoingTEUs': [900000 + (i % 12) * 25000 for i in range(len(dates))]
        }
        return pd.DataFrame(data)

    def _generate_synthetic_vessel_data(self, from_date: str, to_date: str) -> pd.DataFrame:
        """Generates synthetic vessel arrival data for demonstration."""
        dates = pd.date_range(start=from_date, end=to_date, freq='D')
        data = {
            'Date': dates,
            'VesselType': ['Container', 'Bulk', 'Tanker'] * (len(dates) // 3 + 1),
            'Count': [abs(int(10 + 5 * (i % 5))) for i in range(len(dates))]
        }
        return pd.DataFrame(data).iloc[:len(dates)]

def get_time_series_data(cargo_stats: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Provides a dictionary of time series dataframes for trend analysis.

    Args:
        cargo_stats: A dictionary of cargo statistics dataframes.

    Returns:
        A dictionary of time series dataframes.
    """
    return {
        "monthly_throughput": cargo_stats.get("monthly_throughput"),
        "shipment_types": cargo_stats.get("shipment_types"),
    }

def forecast_cargo_throughput(time_series_data: Dict[str, pd.DataFrame], forecast_years: int = 2) -> Optional[pd.DataFrame]:
    """Generates a forecast for cargo throughput for the coming years.

    Args:
        time_series_data: Dictionary of time series dataframes.
        forecast_years: Number of years to forecast.

    Returns:
        A dataframe with forecasted cargo throughput, or None.
    """
    # This is a placeholder for a real forecasting model
    # For now, it generates a simple linear projection
    last_year_data = time_series_data.get("monthly_throughput")
    if last_year_data is None or last_year_data.empty:
        return None

    last_year = last_year_data['year'].max()
    last_year_total = last_year_data[last_year_data['year'] == last_year]['total_teus'].sum()

    forecast_data = []
    for i in range(1, forecast_years + 1):
        forecast_data.append({
            'year': last_year + i,
            'forecasted_teus': last_year_total * (1 + 0.02 * i)  # Simple 2% annual growth
        })
    
    return pd.DataFrame(forecast_data)

def get_enhanced_cargo_analysis() -> Dict[str, Any]:
    """Provides enhanced cargo analysis, including seasonality and growth trends.

    Returns:
        A dictionary with analysis results.
    """
    # Placeholder for more complex analysis
    return {
        "seasonality_pattern": "Peak in Q3, dip in Q1",
        "annual_growth_rate": 0.02,
        "top_cargo_types": ["Electronics", "Textiles", "Machinery"],
    }

def _analyze_seasonal_patterns(time_series_data: pd.DataFrame) -> Dict[str, Any]:
    """Analyzes seasonal patterns in the provided time series data.

    Args:
        time_series_data: DataFrame with a datetime index and a 'total_teus' column.

    Returns:
        A dictionary with seasonal analysis results.
    """
    if time_series_data is None or time_series_data.empty:
        return {}

    # Ensure index is datetime
    if not isinstance(time_series_data.index, pd.DatetimeIndex):
        time_series_data.index = pd.to_datetime(time_series_data.index)

    monthly_avg = time_series_data.groupby(time_series_data.index.month)['total_teus'].mean()
    
    monthly_patterns = {}
    for month, avg_teu in monthly_avg.items():
        monthly_patterns[month] = {
            'total_teu': avg_teu
        }

    return {
        "monthly_patterns": monthly_patterns
    }

def load_focused_cargo_statistics() -> Dict[str, pd.DataFrame]:
    """Loads specific cargo statistics required for scenario analysis.

    Returns:
        A dictionary of pandas DataFrames for different statistics.
    """
    # In a real application, this would load from a file or database
    # Here we generate synthetic data for demonstration
    
    # Monthly throughput data
    years = range(2018, 2024)
    months = range(1, 13)
    monthly_data = []
    for year in years:
        for month in months:
            base_teu = 1.5e6 + (year - 2018) * 0.1e6
            seasonal_factor = 1 + 0.2 * (1 if 6 <= month <= 10 else -1)
            monthly_data.append({
                'year': year,
                'month': month,
                'total_teus': base_teu * seasonal_factor
            })
    monthly_throughput = pd.DataFrame(monthly_data)

    # Shipment types data
    shipment_data = []
    for year in years:
        total = 20e6 + (year - 2018) * 0.5e6
        shipment_data.append({
            'year': year,
            'Direct shipment cargo': total * 0.7,
            'Transhipment cargo': total * 0.3
        })
    shipment_types = pd.DataFrame(shipment_data).set_index('year')

    return {
        "monthly_throughput": monthly_throughput,
        "shipment_types": shipment_types,
    }


def load_container_throughput():
    """Loads container throughput data for the dashboard."""
    config_manager = ConfigManager()
    # We are not using cache here, as it's not clear if it's initialized
    data_loader = DataLoader(config_manager, DataCache(max_size=0))
    data = data_loader._load_cargo_throughput(from_date="2023-01-01", to_date="2023-12-31")
    
    # If API data is not available, generate synthetic data as fallback
    if data is None:
        data = data_loader._generate_synthetic_cargo_data("2023-01-01", "2023-12-31")
    
    return data