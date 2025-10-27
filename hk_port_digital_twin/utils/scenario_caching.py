"""
This module provides a caching mechanism for scenario simulation results.
"""
import functools
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

_scenario_cache: Dict[str, Any] = {}

def get_scenario_cache() -> Dict[str, Any]:
    """Returns the scenario cache."""
    return _scenario_cache

def clear_scenario_cache():
    """Clears the scenario cache."""
    _scenario_cache.clear()

def cache_scenario_result(scenario_id: str, result: Any):
    """Caches the result of a scenario simulation."""
    _scenario_cache[scenario_id] = result
    logger.info(f"Cached result for scenario {scenario_id}")

def get_cached_scenario_result(scenario_id: str) -> Any:
    """Retrieves a cached scenario result."""
    return _scenario_cache.get(scenario_id)