import os
import time
import logging
import requests
from datetime import datetime
from typing import Dict, Optional

class MarineTrafficFetcher:
    """
    Handles downloading vessel data from the MarineTraffic API.
    """

    def __init__(self):
        """
        Initializes the MarineTraffic fetcher.
        """
        self.api_key = os.getenv("MARINETRAFFIC_API_KEY")
        self.base_url = "https://services.marinetraffic.com/api"
        self.logger = logging.getLogger(__name__)

    def fetch_data(self, area_bounds: Optional[Dict] = None) -> Optional[Dict]:
        """
        Fetches vessel data from the MarineTraffic API.
        """
        if not self.api_key:
            self.logger.warning("MarineTraffic API key not configured.")
            return None

        if not area_bounds:
            # Default to Hong Kong waters
            area_bounds = {
                "minlat": 22.1,
                "maxlat": 22.5,
                "minlon": 113.8,
                "maxlon": 114.5,
            }

        try:
            endpoint = f"{self.base_url}/exportvessels/v:8"
            params = {
                "key": self.api_key,
                "protocol": "jsono",
                "minlat": area_bounds["minlat"],
                "maxlat": area_bounds["maxlat"],
                "minlon": area_bounds["minlon"],
                "maxlon": area_bounds["maxlon"],
                "timespan": 10,  # Last 10 minutes
            }

            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            self.logger.error(f"MarineTraffic API request failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching vessel data: {e}")
            return None