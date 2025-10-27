"""
Cache decorators for data loading optimization in the scenarios tab.

This module provides comprehensive caching decorators for different types of data loading operations,
including scenario-aware caching, time-based invalidation, and memory-efficient storage.
"""

import functools
import hashlib
import time
import logging
from typing import Any, Dict, Optional, Callable, Union, Tuple
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Cache configuration
DEFAULT_CACHE_TTL = 300  # 5 minutes
SCENARIO_CACHE_TTL = 600  # 10 minutes for scenario data
CHART_CACHE_TTL = 180   # 3 minutes for chart data
HEAVY_COMPUTATION_TTL = 900  # 15 minutes for heavy computations

class CacheManager:
    """Centralized cache management for data loading operations."""
    
    def __init__(self):
        self._cache = {}
        self._cache_metadata = {}
        self._max_cache_size = 100  # Maximum number of cached items
        
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict, 
                          scenario: Optional[str] = None) -> str:
        """Generate a unique cache key for function calls."""
        # Create a string representation of arguments
        args_str = str(args)
        kwargs_str = str(sorted(kwargs.items()))
        scenario_str = scenario or "default"
        
        # Create hash for consistent key generation
        key_data = f"{func_name}:{args_str}:{kwargs_str}:{scenario_str}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str, ttl: int = DEFAULT_CACHE_TTL) -> Optional[Any]:
        """Retrieve cached data if valid."""
        if key not in self._cache:
            return None
            
        metadata = self._cache_metadata.get(key, {})
        cache_time = metadata.get('timestamp', 0)
        
        # Check if cache is still valid
        if time.time() - cache_time > ttl:
            self._invalidate(key)
            return None
            
        # Update access time for LRU tracking
        metadata['last_access'] = time.time()
        self._cache_metadata[key] = metadata
        
        logger.debug(f"Cache hit for key: {key[:16]}...")
        return self._cache[key]
    
    def set(self, key: str, value: Any, scenario: Optional[str] = None) -> None:
        """Store data in cache with metadata."""
        # Implement LRU eviction if cache is full
        if len(self._cache) >= self._max_cache_size:
            self._evict_lru()
        
        self._cache[key] = value
        self._cache_metadata[key] = {
            'timestamp': time.time(),
            'last_access': time.time(),
            'scenario': scenario,
            'size': self._estimate_size(value)
        }
        
        logger.debug(f"Cached data for key: {key[:16]}...")
    
    def _invalidate(self, key: str) -> None:
        """Remove expired cache entry."""
        if key in self._cache:
            del self._cache[key]
        if key in self._cache_metadata:
            del self._cache_metadata[key]
        logger.debug(f"Invalidated cache for key: {key[:16]}...")
    
    def _evict_lru(self) -> None:
        """Evict least recently used cache entry."""
        if not self._cache_metadata:
            return
            
        # Find LRU entry
        lru_key = min(self._cache_metadata.keys(), 
                     key=lambda k: self._cache_metadata[k].get('last_access', 0))
        self._invalidate(lru_key)
        logger.debug(f"Evicted LRU cache entry: {lru_key[:16]}...")
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate memory size of cached value."""
        try:
            if isinstance(value, pd.DataFrame):
                return value.memory_usage(deep=True).sum()
            elif isinstance(value, np.ndarray):
                return value.nbytes
            elif isinstance(value, (list, dict, tuple)):
                return len(str(value))
            else:
                return len(str(value))
        except Exception:
            return 1000  # Default estimate
    
    def clear_scenario_cache(self, scenario: str) -> None:
        """Clear all cache entries for a specific scenario."""
        keys_to_remove = []
        for key, metadata in self._cache_metadata.items():
            if metadata.get('scenario') == scenario:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            self._invalidate(key)
        
        logger.info(f"Cleared cache for scenario: {scenario}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring."""
        total_size = sum(meta.get('size', 0) for meta in self._cache_metadata.values())
        scenarios = set(meta.get('scenario') for meta in self._cache_metadata.values())
        
        return {
            'total_entries': len(self._cache),
            'total_size_bytes': total_size,
            'scenarios_cached': len(scenarios),
            'max_size': self._max_cache_size,
            'cache_utilization': len(self._cache) / self._max_cache_size
        }

# Global cache manager instance
_cache_manager = CacheManager()

def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    return _cache_manager

def scenario_aware_cache(ttl: int = SCENARIO_CACHE_TTL, 
                        scenario_key: str = 'scenario'):
    """
    Decorator for caching scenario-aware data loading functions.
    
    Args:
        ttl: Time to live in seconds
        scenario_key: Parameter name that contains scenario information
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract scenario from arguments
            scenario = kwargs.get(scenario_key, 'default')
            if not scenario and args:
                # Try to extract from positional args if it's the first argument
                scenario = args[0] if args else 'default'
            
            # Generate cache key
            cache_key = _cache_manager._generate_cache_key(
                func.__name__, args, kwargs, scenario
            )
            
            # Try to get from cache
            cached_result = _cache_manager.get(cache_key, ttl)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            try:
                result = func(*args, **kwargs)
                _cache_manager.set(cache_key, result, scenario)
                return result
            except Exception as e:
                logger.error(f"Error in cached function {func.__name__}: {e}")
                raise
        
        # Add cache management methods to the wrapper
        wrapper.clear_cache = lambda scenario=None: (
            _cache_manager.clear_scenario_cache(scenario) if scenario 
            else _cache_manager._cache.clear()
        )
        wrapper.cache_stats = _cache_manager.get_cache_stats
        
        return wrapper
    return decorator

def data_loading_cache(ttl: int = DEFAULT_CACHE_TTL, 
                      invalidate_on_error: bool = True):
    """
    Decorator for caching general data loading functions.
    
    Args:
        ttl: Time to live in seconds
        invalidate_on_error: Whether to invalidate cache on function errors
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = _cache_manager._generate_cache_key(
                func.__name__, args, kwargs
            )
            
            # Try to get from cache
            cached_result = _cache_manager.get(cache_key, ttl)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            try:
                result = func(*args, **kwargs)
                _cache_manager.set(cache_key, result)
                return result
            except Exception as e:
                if invalidate_on_error:
                    _cache_manager._invalidate(cache_key)
                logger.error(f"Error in cached function {func.__name__}: {e}")
                raise
        
        return wrapper
    return decorator

def chart_data_cache(ttl: int = CHART_CACHE_TTL):
    """
    Decorator for caching chart data generation functions.
    
    Args:
        ttl: Time to live in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = _cache_manager._generate_cache_key(
                f"chart_{func.__name__}", args, kwargs
            )
            
            # Try to get from cache
            cached_result = _cache_manager.get(cache_key, ttl)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            try:
                result = func(*args, **kwargs)
                _cache_manager.set(cache_key, result)
                return result
            except Exception as e:
                logger.error(f"Error in cached chart function {func.__name__}: {e}")
                raise
        
        return wrapper
    return decorator

def heavy_computation_cache(ttl: int = HEAVY_COMPUTATION_TTL):
    """
    Decorator for caching heavy computational functions.
    
    Args:
        ttl: Time to live in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = _cache_manager._generate_cache_key(
                f"heavy_{func.__name__}", args, kwargs
            )
            
            # Try to get from cache
            cached_result = _cache_manager.get(cache_key, ttl)
            if cached_result is not None:
                logger.info(f"Heavy computation cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"Heavy computation {func.__name__} took {execution_time:.2f}s")
                _cache_manager.set(cache_key, result)
                return result
            except Exception as e:
                logger.error(f"Error in heavy computation {func.__name__}: {e}")
                raise
        
        return wrapper
    return decorator

def conditional_cache(condition_func: Callable[..., bool], 
                     ttl: int = DEFAULT_CACHE_TTL):
    """
    Decorator for conditional caching based on custom logic.
    
    Args:
        condition_func: Function that returns True if caching should be applied
        ttl: Time to live in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check if caching should be applied
            if not condition_func(*args, **kwargs):
                return func(*args, **kwargs)
            
            # Generate cache key
            cache_key = _cache_manager._generate_cache_key(
                func.__name__, args, kwargs
            )
            
            # Try to get from cache
            cached_result = _cache_manager.get(cache_key, ttl)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            try:
                result = func(*args, **kwargs)
                _cache_manager.set(cache_key, result)
                return result
            except Exception as e:
                logger.error(f"Error in conditionally cached function {func.__name__}: {e}")
                raise
        
        return wrapper
    return decorator

# Utility functions for cache management
def clear_all_caches():
    """Clear all cached data."""
    _cache_manager._cache.clear()
    _cache_manager._cache_metadata.clear()
    logger.info("Cleared all caches")

def get_cache_statistics() -> Dict[str, Any]:
    """Get comprehensive cache statistics."""
    return _cache_manager.get_cache_stats()

def invalidate_scenario_cache(scenario: str):
    """Invalidate all cache entries for a specific scenario."""
    _cache_manager.clear_scenario_cache(scenario)

# Context manager for temporary cache settings
class TemporaryCacheSettings:
    """Context manager for temporarily modifying cache settings."""
    
    def __init__(self, max_size: Optional[int] = None):
        self.max_size = max_size
        self.original_max_size = None
    
    def __enter__(self):
        if self.max_size is not None:
            self.original_max_size = _cache_manager._max_cache_size
            _cache_manager._max_cache_size = self.max_size
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.original_max_size is not None:
            _cache_manager._max_cache_size = self.original_max_size