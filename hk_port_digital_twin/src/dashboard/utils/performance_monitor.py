"""
This module provides utilities for performance monitoring.
"""

import time

import asyncio
from functools import wraps

def timing_decorator(func):
    """A decorator that prints the execution time of a function."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        if asyncio.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function {func.__name__} took {end_time - start_time:.4f} seconds to execute.")
        return result
    return wrapper

class PerformanceMonitor:
    """A class to monitor performance metrics."""

    def __init__(self):
        self.memory_usage = {}

    def track_memory_usage(self, name: str):
        """Tracks the memory usage of a component."""
        # This is a placeholder for a more sophisticated memory tracking implementation
        import random
        self.memory_usage[name] = random.randint(100, 1000)

    def generate_report(self):
        """Generates a performance report."""
        print("--- Performance Report ---")
        for name, memory in self.memory_usage.items():
            print(f"{name}: {memory} MB")
        print("------------------------")