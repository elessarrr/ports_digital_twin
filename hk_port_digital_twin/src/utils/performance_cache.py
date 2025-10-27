"""
Performance Cache Module for Streamlit Dashboard Optimization

This module provides intelligent caching for optimization results to improve
dashboard performance by avoiding redundant calculations.

Key Features:
- LRU (Least Recently Used) cache implementation
- Parameter-based cache key generation
- TTL (Time To Live) support
- Memory-efficient storage
- Cache hit/miss metrics
- Thread-safe operations
"""

import hashlib
import json
import time
import threading
from collections import OrderedDict
from typing import Any, Dict, Optional, Tuple, Union
from datetime import datetime, timedelta
import logging

# Configure logging
logger = logging.getLogger(__name__)


class LRUCache:
    """
    Thread-safe LRU (Least Recently Used) cache implementation with TTL support.
    
    This cache is specifically designed for optimization results where:
    - Cache keys are generated from optimization parameters
    - Results have a time-to-live (TTL) for freshness
    - Memory usage is controlled through size limits
    - Access patterns are tracked for monitoring
    """
    
    def __init__(self, max_size: int = 100, default_ttl: int = 3600):
        """
        Initialize the LRU cache.
        
        Args:
            max_size: Maximum number of items to cache (default: 100)
            default_ttl: Default time-to-live in seconds (default: 1 hour)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        
        # Thread-safe data structures
        self._cache = OrderedDict()
        self._timestamps = {}
        self._access_counts = {}
        self._lock = threading.RLock()
        
        # Statistics tracking
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        
    def _generate_key(self, objective: str, weights: Dict[str, float], 
                     constraints: Dict[str, Any]) -> str:
        """
        Generate a deterministic cache key from optimization parameters.
        
        Args:
            objective: Optimization objective (e.g., 'minimize_wait_time')
            weights: Weight parameters for optimization
            constraints: Constraint parameters for optimization
            
        Returns:
            str: MD5 hash of the parameters
        """
        # Create a deterministic representation of parameters
        key_data = {
            'objective': objective,
            'weights': sorted(weights.items()) if weights else [],
            'constraints': sorted(constraints.items()) if constraints else []
        }
        
        # Convert to JSON string with sorted keys for consistency
        key_string = json.dumps(key_data, sort_keys=True, separators=(',', ':'))
        
        # Generate MD5 hash for compact key
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()
    
    def get(self, objective: str, weights: Dict[str, float], 
            constraints: Dict[str, Any], ttl: Optional[int] = None) -> Optional[Any]:
        """
        Retrieve cached optimization result if available and fresh.
        
        Args:
            objective: Optimization objective
            weights: Weight parameters
            constraints: Constraint parameters
            ttl: Custom TTL in seconds (uses default if None)
            
        Returns:
            Cached result if available and fresh, None otherwise
        """
        key = self._generate_key(objective, weights, constraints)
        
        with self._lock:
            # Check if key exists
            if key not in self._cache:
                self._misses += 1
                logger.debug(f"Cache miss for key: {key[:8]}...")
                return None
            
            # Check TTL
            ttl = ttl or self.default_ttl
            age = time.time() - self._timestamps[key]
            
            if age > ttl:
                # Data is stale, remove and count as miss
                self._remove_key(key)
                self._misses += 1
                logger.debug(f"Cache expired for key: {key[:8]}... (age: {age:.1f}s)")
                return None
            
            # Move to end (most recently used)
            value = self._cache.pop(key)
            self._cache[key] = value
            
            # Update statistics
            self._hits += 1
            self._access_counts[key] = self._access_counts.get(key, 0) + 1
            
            logger.debug(f"Cache hit for key: {key[:8]}... (age: {age:.1f}s)")
            return value
    
    def set(self, objective: str, weights: Dict[str, float], 
            constraints: Dict[str, Any], result: Any) -> None:
        """
        Cache an optimization result.
        
        Args:
            objective: Optimization objective
            weights: Weight parameters
            constraints: Constraint parameters
            result: Optimization result to cache
        """
        key = self._generate_key(objective, weights, constraints)
        
        with self._lock:
            # Remove existing entry if present
            if key in self._cache:
                self._cache.pop(key)
            
            # Add new entry
            self._cache[key] = result
            self._timestamps[key] = time.time()
            self._access_counts[key] = 0
            
            # Enforce size limit (LRU eviction)
            while len(self._cache) > self.max_size:
                # Remove least recently used item (first item in OrderedDict)
                oldest_key = next(iter(self._cache))
                self._remove_key(oldest_key)
                self._evictions += 1
                logger.debug(f"Evicted key: {oldest_key[:8]}... (cache full)")
            
            logger.debug(f"Cached result for key: {key[:8]}...")
    
    def _remove_key(self, key: str) -> None:
        """Remove a key and its associated data."""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
        self._access_counts.pop(key, None)
    
    def invalidate(self, objective: str = None, weights: Dict[str, float] = None, 
                   constraints: Dict[str, Any] = None) -> int:
        """
        Invalidate cached entries. If no parameters provided, clears all.
        
        Args:
            objective: Specific objective to invalidate (optional)
            weights: Specific weights to invalidate (optional)
            constraints: Specific constraints to invalidate (optional)
            
        Returns:
            Number of entries invalidated
        """
        with self._lock:
            if objective is None and weights is None and constraints is None:
                # Clear all
                count = len(self._cache)
                self._cache.clear()
                self._timestamps.clear()
                self._access_counts.clear()
                logger.info(f"Cleared all cache entries ({count} items)")
                return count
            
            # Invalidate specific entry
            key = self._generate_key(objective, weights, constraints)
            if key in self._cache:
                self._remove_key(key)
                logger.debug(f"Invalidated key: {key[:8]}...")
                return 1
            
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Dictionary containing cache statistics
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': hit_rate,
                'evictions': self._evictions,
                'total_requests': total_requests,
                'memory_usage_estimate': self._estimate_memory_usage(),
                'oldest_entry_age': self._get_oldest_entry_age(),
                'most_accessed_keys': self._get_most_accessed_keys(5)
            }
    
    def _estimate_memory_usage(self) -> str:
        """Estimate memory usage of cached data."""
        try:
            import sys
            total_size = 0
            
            # Estimate size of cache data structures
            total_size += sys.getsizeof(self._cache)
            total_size += sys.getsizeof(self._timestamps)
            total_size += sys.getsizeof(self._access_counts)
            
            # Estimate size of cached values (rough approximation)
            for value in self._cache.values():
                total_size += sys.getsizeof(value)
            
            # Convert to human-readable format
            if total_size < 1024:
                return f"{total_size} B"
            elif total_size < 1024 * 1024:
                return f"{total_size / 1024:.1f} KB"
            else:
                return f"{total_size / (1024 * 1024):.1f} MB"
                
        except Exception:
            return "Unknown"
    
    def _get_oldest_entry_age(self) -> Optional[float]:
        """Get the age of the oldest cache entry in seconds."""
        if not self._timestamps:
            return None
        
        oldest_timestamp = min(self._timestamps.values())
        return time.time() - oldest_timestamp
    
    def _get_most_accessed_keys(self, limit: int = 5) -> list:
        """Get the most frequently accessed cache keys."""
        sorted_keys = sorted(
            self._access_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return [(key[:8] + "...", count) for key, count in sorted_keys[:limit]]


class PerformanceCache:
    """
    High-level performance cache manager for optimization results.
    
    This class provides a simple interface for caching optimization results
    with automatic key generation and comprehensive monitoring.
    """
    
    def __init__(self, max_size: int = 100, default_ttl: int = 3600):
        """
        Initialize the performance cache.
        
        Args:
            max_size: Maximum number of cached results
            default_ttl: Default cache TTL in seconds
        """
        self._cache = LRUCache(max_size=max_size, default_ttl=default_ttl)
        self._start_time = time.time()
        
    def get_optimization_result(self, objective: str, weights: Dict[str, float], 
                              constraints: Dict[str, Any]) -> Optional[Any]:
        """
        Get cached optimization result.
        
        Args:
            objective: Optimization objective
            weights: Weight parameters
            constraints: Constraint parameters
            
        Returns:
            Cached result if available, None otherwise
        """
        return self._cache.get(objective, weights, constraints)
    
    def cache_optimization_result(self, objective: str, weights: Dict[str, float], 
                                constraints: Dict[str, Any], result: Any) -> None:
        """
        Cache an optimization result.
        
        Args:
            objective: Optimization objective
            weights: Weight parameters
            constraints: Constraint parameters
            result: Result to cache
        """
        self._cache.set(objective, weights, constraints, result)
    
    def invalidate_cache(self, objective: str = None, weights: Dict[str, float] = None, 
                        constraints: Dict[str, Any] = None) -> int:
        """
        Invalidate cached entries.
        
        Args:
            objective: Specific objective to invalidate (optional)
            weights: Specific weights to invalidate (optional)
            constraints: Specific constraints to invalidate (optional)
            
        Returns:
            Number of entries invalidated
        """
        return self._cache.invalidate(objective, weights, constraints)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive performance metrics.
        
        Returns:
            Dictionary containing performance metrics
        """
        stats = self._cache.get_stats()
        
        # Add additional metrics
        uptime = time.time() - self._start_time
        stats.update({
            'cache_uptime_seconds': uptime,
            'cache_uptime_formatted': str(timedelta(seconds=int(uptime))),
            'average_requests_per_minute': (stats['total_requests'] / (uptime / 60)) if uptime > 0 else 0
        })
        
        return stats
    
    def is_cache_healthy(self) -> Tuple[bool, str]:
        """
        Check if cache is performing well.
        
        Returns:
            Tuple of (is_healthy, status_message)
        """
        stats = self.get_performance_metrics()
        
        # Health checks
        if stats['total_requests'] == 0:
            return True, "Cache initialized, no requests yet"
        
        hit_rate = stats['hit_rate']
        if hit_rate >= 70:
            return True, f"Cache performing well (hit rate: {hit_rate:.1f}%)"
        elif hit_rate >= 50:
            return True, f"Cache performing adequately (hit rate: {hit_rate:.1f}%)"
        else:
            return False, f"Cache hit rate low (hit rate: {hit_rate:.1f}%)"


# Global cache instance for optimization results
optimization_cache = PerformanceCache(max_size=100, default_ttl=3600)


def get_cached_optimization_result(objective: str, weights: Dict[str, float], 
                                 constraints: Dict[str, Any]) -> Optional[Any]:
    """
    Convenience function to get cached optimization result.
    
    Args:
        objective: Optimization objective
        weights: Weight parameters
        constraints: Constraint parameters
        
    Returns:
        Cached result if available, None otherwise
    """
    return optimization_cache.get_optimization_result(objective, weights, constraints)


def cache_optimization_result(objective: str, weights: Dict[str, float], 
                            constraints: Dict[str, Any], result: Any) -> None:
    """
    Convenience function to cache optimization result.
    
    Args:
        objective: Optimization objective
        weights: Weight parameters
        constraints: Constraint parameters
        result: Result to cache
    """
    optimization_cache.cache_optimization_result(objective, weights, constraints, result)


def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache performance statistics.
    
    Returns:
        Dictionary containing cache statistics
    """
    return optimization_cache.get_performance_metrics()


def clear_optimization_cache() -> int:
    """
    Clear all cached optimization results.
    
    Returns:
        Number of entries cleared
    """
    return optimization_cache.invalidate_cache()