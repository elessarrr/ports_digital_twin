"""
Rendering optimization utilities for dashboard components.

This module provides utilities to optimize rendering performance by:
- Reducing redundant computations
- Implementing efficient data sharing between components
- Providing memoization for expensive operations
- Managing component state efficiently
"""

import functools
import hashlib
import time
from typing import Any, Dict, List, Optional, Callable, Union
import streamlit as st
import pandas as pd
import numpy as np

from .session_state_manager import get_session_manager


class RenderingOptimizer:
    """Manages rendering optimizations and shared computations."""
    
    def __init__(self):
        self.computation_cache = {}
        self.shared_data = {}
        self.last_computed = {}
        self.computation_stats = {}
    
    def get_shared_data(self, key: str, compute_func: Callable, *args, **kwargs) -> Any:
        """Get shared data, computing only if not cached or expired."""
        cache_key = self._generate_cache_key(key, args, kwargs)
        current_time = time.time()
        
        # Check if we have cached data and it's still valid
        if (cache_key in self.computation_cache and 
            current_time - self.last_computed.get(cache_key, 0) < 300):  # 5 min cache
            self._update_stats(key, hit=True)
            return self.computation_cache[cache_key]
        
        # Compute new data
        start_time = time.time()
        result = compute_func(*args, **kwargs)
        computation_time = time.time() - start_time
        
        # Cache the result
        self.computation_cache[cache_key] = result
        self.last_computed[cache_key] = current_time
        self._update_stats(key, hit=False, computation_time=computation_time)
        
        return result
    
    def _generate_cache_key(self, key: str, args: tuple, kwargs: dict) -> str:
        """Generate a unique cache key."""
        key_data = f"{key}_{str(args)}_{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _update_stats(self, key: str, hit: bool, computation_time: float = 0):
        """Update computation statistics."""
        if key not in self.computation_stats:
            self.computation_stats[key] = {
                'hits': 0, 'misses': 0, 'total_time': 0, 'avg_time': 0
            }
        
        if hit:
            self.computation_stats[key]['hits'] += 1
        else:
            self.computation_stats[key]['misses'] += 1
            self.computation_stats[key]['total_time'] += computation_time
            total_computations = self.computation_stats[key]['misses']
            self.computation_stats[key]['avg_time'] = (
                self.computation_stats[key]['total_time'] / total_computations
            )
    
    def clear_cache(self, pattern: Optional[str] = None):
        """Clear cache entries, optionally matching a pattern."""
        if pattern is None:
            self.computation_cache.clear()
            self.last_computed.clear()
        else:
            keys_to_remove = [k for k in self.computation_cache.keys() if pattern in k]
            for key in keys_to_remove:
                self.computation_cache.pop(key, None)
                self.last_computed.pop(key, None)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get computation statistics."""
        return self.computation_stats.copy()


# Global optimizer instance
_optimizer = RenderingOptimizer()


def optimized_computation(key: str, ttl: int = 300):
    """Decorator for optimizing expensive computations."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return _optimizer.get_shared_data(key, func, *args, **kwargs)
        return wrapper
    return decorator


def batch_compute(computations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Batch multiple computations for efficiency."""
    results = {}
    
    for comp in computations:
        key = comp['key']
        func = comp['func']
        args = comp.get('args', ())
        kwargs = comp.get('kwargs', {})
        
        results[key] = _optimizer.get_shared_data(key, func, *args, **kwargs)
    
    return results


def memoize_dataframe(func: Callable) -> Callable:
    """Memoize DataFrame operations based on data hash."""
    cache = {}
    
    @functools.wraps(func)
    def wrapper(df: pd.DataFrame, *args, **kwargs):
        # Create hash of DataFrame content
        df_hash = hashlib.md5(
            pd.util.hash_pandas_object(df, index=True).values
        ).hexdigest()
        
        cache_key = f"{df_hash}_{str(args)}_{str(sorted(kwargs.items()))}"
        
        if cache_key in cache:
            return cache[cache_key]
        
        result = func(df, *args, **kwargs)
        cache[cache_key] = result
        
        # Limit cache size
        if len(cache) > 100:
            # Remove oldest entries
            oldest_keys = list(cache.keys())[:20]
            for key in oldest_keys:
                cache.pop(key, None)
        
        return result
    
    return wrapper


def optimize_chart_data(data: Union[pd.DataFrame, Dict], 
                       max_points: int = 1000) -> Union[pd.DataFrame, Dict]:
    """Optimize data for chart rendering by reducing points if necessary."""
    if isinstance(data, pd.DataFrame):
        if len(data) > max_points:
            # Sample data intelligently
            step = len(data) // max_points
            return data.iloc[::step].copy()
        return data
    
    elif isinstance(data, dict):
        optimized = {}
        for key, value in data.items():
            if isinstance(value, (list, np.ndarray)) and len(value) > max_points:
                step = len(value) // max_points
                optimized[key] = value[::step]
            else:
                optimized[key] = value
        return optimized
    
    return data


class ComponentStateManager:
    """Manages component state efficiently."""
    
    def __init__(self):
        self.component_states = {}
        self.state_history = {}
        self.session_manager = get_session_manager()
    
    def get_component_state(self, component_id: str, default: Any = None) -> Any:
        """Get component state with session state integration."""
        session_key = f"component_state_{component_id}"
        return self.session_manager.get_value(session_key, self.component_states.get(component_id, default))
    
    def set_component_state(self, component_id: str, state: Any,
                          persist: bool = True) -> None:
        """Set component state with optional persistence."""
        self.component_states[component_id] = state
    
        if persist:
            session_key = f"component_state_{component_id}"
            self.session_manager.set_value(session_key, state)
    
        # Track state history for debugging
        if component_id not in self.state_history:
            self.state_history[component_id] = []
    
        self.state_history[component_id].append({
            'timestamp': time.time(),
            'state': state
        })
    
        # Limit history size
        if len(self.state_history[component_id]) > 10:
            self.state_history[component_id] = self.state_history[component_id][-10:]
    
    def clear_component_state(self, component_id: str) -> None:
        """Clear component state."""
        self.component_states.pop(component_id, None)
        session_key = f"component_state_{component_id}"
        if self.session_manager.has_key(session_key):
            self.session_manager.set_value(session_key, None)


# Global state manager
_state_manager = ComponentStateManager()


def get_component_state(component_id: str, default: Any = None) -> Any:
    """Get component state."""
    return _state_manager.get_component_state(component_id, default)


def set_component_state(component_id: str, state: Any, persist: bool = True) -> None:
    """Set component state."""
    _state_manager.set_component_state(component_id, state, persist)


def clear_optimization_cache():
    """Clear all optimization caches."""
    _optimizer.clear_cache()


def get_optimization_stats() -> Dict[str, Any]:
    """Get optimization statistics."""
    return _optimizer.get_stats()


# Utility decorators for common optimizations
def optimize_for_scenario(func: Callable) -> Callable:
    """Optimize function for scenario-based computations."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        scenario = kwargs.get('scenario_name') or getattr(st.session_state, 'current_scenario', 'default')
        cache_key = f"{func.__name__}_{scenario}"
        return _optimizer.get_shared_data(cache_key, func, *args, **kwargs)
    return wrapper


def debounce_computation(delay: float = 0.5):
    """Debounce expensive computations."""
    def decorator(func: Callable) -> Callable:
        last_call = {'time': 0, 'result': None, 'args': None, 'kwargs': None}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            
            # Check if we can reuse the last result
            if (current_time - last_call['time'] < delay and 
                last_call['args'] == args and 
                last_call['kwargs'] == kwargs):
                return last_call['result']
            
            # Compute new result
            result = func(*args, **kwargs)
            last_call.update({
                'time': current_time,
                'result': result,
                'args': args,
                'kwargs': kwargs
            })
            
            return result
        
        return wrapper
    return decorator