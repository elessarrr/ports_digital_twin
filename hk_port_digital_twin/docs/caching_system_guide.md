# Performance Caching System Guide

## Overview

The Hong Kong Port Digital Twin implements a sophisticated performance caching system designed to optimize dashboard performance by avoiding redundant calculations. This system provides intelligent caching for optimization results with automatic invalidation, TTL support, and comprehensive monitoring.

## Key Features

- **LRU (Least Recently Used) Cache**: Automatically evicts oldest entries when cache is full
- **Parameter-based Cache Keys**: Generates unique keys from optimization parameters
- **TTL (Time To Live) Support**: Automatic expiration of cached results
- **Memory-efficient Storage**: Controlled memory usage through size limits
- **Cache Hit/Miss Metrics**: Comprehensive performance monitoring
- **Thread-safe Operations**: Safe for concurrent access
- **Automatic Invalidation**: Cache invalidation on data file changes

## Architecture

### Core Components

1. **LRUCache**: Low-level cache implementation with TTL support
2. **PerformanceCache**: High-level interface for optimization results
3. **Global Cache Instance**: Singleton cache instance for the application
4. **File Monitoring Integration**: Automatic cache invalidation on data changes

### Cache Hierarchy

```
Application Layer
    ↓
PerformanceCache (High-level API)
    ↓
LRUCache (Low-level implementation)
    ↓
OrderedDict (Storage backend)
```

## Usage Examples

### Basic Cache Operations

```python
from src.utils.performance_cache import (
    get_cached_optimization_result,
    cache_optimization_result,
    get_cache_stats,
    clear_optimization_cache
)

# Define optimization parameters
objective = "minimize_wait_time"
weights = {"efficiency": 0.6, "cost": 0.4}
constraints = {"max_berths": 10, "time_horizon": 24}

# Try to get cached result
cached_result = get_cached_optimization_result(objective, weights, constraints)

if cached_result is None:
    # Cache miss - perform optimization
    result = perform_optimization(objective, weights, constraints)
    
    # Cache the result for future use
    cache_optimization_result(objective, weights, constraints, result)
    print("Result computed and cached")
else:
    # Cache hit - use cached result
    result = cached_result
    print("Using cached result")
```

### Using the PerformanceCache Class Directly

```python
from src.utils.performance_cache import PerformanceCache

# Create cache instance with custom settings
cache = PerformanceCache(max_size=50, default_ttl=1800)  # 30 minutes TTL

# Cache an optimization result
optimization_result = {
    "berth_assignments": [1, 2, 3, 4],
    "total_cost": 150000,
    "wait_time": 2.5,
    "efficiency_score": 0.85
}

cache.cache_optimization_result(
    objective="minimize_cost",
    weights={"cost": 0.8, "time": 0.2},
    constraints={"vessels": 20},
    result=optimization_result
)

# Retrieve cached result
cached = cache.get_optimization_result(
    objective="minimize_cost",
    weights={"cost": 0.8, "time": 0.2},
    constraints={"vessels": 20}
)

if cached:
    print(f"Cached result: {cached}")
```

### Cache Monitoring and Statistics

```python
from src.utils.performance_cache import get_cache_stats

# Get comprehensive cache statistics
stats = get_cache_stats()

print(f"Cache size: {stats['size']}/{stats['max_size']}")
print(f"Hit rate: {stats['hit_rate']:.2%}")
print(f"Total requests: {stats['total_requests']}")
print(f"Memory usage: {stats['memory_usage_estimate']}")
print(f"Most accessed keys: {stats['most_accessed_keys']}")

# Check cache health
from src.utils.performance_cache import optimization_cache

is_healthy, message = optimization_cache.is_cache_healthy()
print(f"Cache health: {'✅' if is_healthy else '❌'} {message}")
```

### Cache Invalidation

```python
from src.utils.performance_cache import clear_optimization_cache

# Clear all cached entries
cleared_count = clear_optimization_cache()
print(f"Cleared {cleared_count} cache entries")

# Selective invalidation using PerformanceCache
cache = PerformanceCache()

# Invalidate specific entries
invalidated = cache.invalidate_cache(
    objective="minimize_cost",
    weights={"cost": 0.8, "time": 0.2}
)
print(f"Invalidated {invalidated} entries")

# Invalidate all entries for a specific objective
invalidated = cache.invalidate_cache(objective="minimize_wait_time")
print(f"Invalidated {invalidated} entries for wait time optimization")
```

## Integration with Data Loading

The caching system is automatically integrated with the data loading pipeline to ensure cache consistency:

### Automatic Cache Invalidation

When data files change, the cache is automatically invalidated:

```python
# File monitoring callbacks automatically clear cache
def _on_vessel_file_change(self, event):
    """Handle vessel data file changes"""
    if self.auto_reload_on_file_change:
        logger.info(f"Vessel file changed: {event.src_path}")
        
        # Clear optimization cache when data changes
        try:
            from .performance_cache import clear_optimization_cache
            cleared = clear_optimization_cache()
            logger.info(f"Cleared {cleared} optimization cache entries due to vessel data change")
        except Exception as e:
            logger.warning(f"Could not clear optimization cache: {e}")
        
        # Trigger data reload
        self._update_vessel_data()
```

### Manual Data Refresh

The manual refresh function also clears the cache:

```python
from src.utils.data_loader import refresh_vessel_data

# This function automatically clears both optimization and data caches
success = refresh_vessel_data()
if success:
    print("Data refreshed and caches cleared")
```

## Configuration

### Cache Settings

```python
# Default configuration
MAX_CACHE_SIZE = 100        # Maximum number of cached results
DEFAULT_TTL = 3600          # 1 hour default TTL in seconds
MEMORY_THRESHOLD = 0.8      # Memory usage warning threshold

# Custom configuration
cache = PerformanceCache(
    max_size=200,           # Larger cache
    default_ttl=7200        # 2 hours TTL
)
```

### Environment Variables

You can configure cache behavior through environment variables:

```bash
# Set cache size limit
export CACHE_MAX_SIZE=150

# Set default TTL (in seconds)
export CACHE_DEFAULT_TTL=1800

# Enable cache debugging
export CACHE_DEBUG=true
```

## Best Practices

### 1. Cache Key Design

- Use consistent parameter ordering
- Include all relevant optimization parameters
- Avoid including timestamps or random values in cache keys

```python
# Good: Consistent parameters
weights = {"efficiency": 0.6, "cost": 0.4}
constraints = {"max_berths": 10, "time_horizon": 24}

# Bad: Including timestamp makes cache ineffective
constraints = {"max_berths": 10, "timestamp": time.time()}
```

### 2. TTL Management

- Use shorter TTL for frequently changing data
- Use longer TTL for stable optimization results
- Consider data freshness requirements

```python
# Short TTL for real-time optimizations
cache.cache_optimization_result(objective, weights, constraints, result)

# Custom TTL for specific use cases
cache._cache.set(objective, weights, constraints, result, ttl=300)  # 5 minutes
```

### 3. Memory Management

- Monitor cache statistics regularly
- Set appropriate cache size limits
- Clear cache when memory usage is high

```python
# Monitor cache health
stats = get_cache_stats()
if stats['size'] > stats['max_size'] * 0.9:
    print("Cache is nearly full, consider clearing old entries")

# Check memory usage
if 'memory_usage_estimate' in stats:
    print(f"Current memory usage: {stats['memory_usage_estimate']}")
```

### 4. Error Handling

Always handle cache operations gracefully:

```python
try:
    cached_result = get_cached_optimization_result(objective, weights, constraints)
    if cached_result is not None:
        return cached_result
except Exception as e:
    logger.warning(f"Cache retrieval failed: {e}")
    # Fall back to computation

# Always compute if cache fails
result = perform_optimization(objective, weights, constraints)

try:
    cache_optimization_result(objective, weights, constraints, result)
except Exception as e:
    logger.warning(f"Cache storage failed: {e}")
    # Continue without caching

return result
```

## Performance Monitoring

### Key Metrics

1. **Hit Rate**: Percentage of requests served from cache
2. **Cache Size**: Number of entries currently cached
3. **Memory Usage**: Estimated memory consumption
4. **Eviction Rate**: How often entries are evicted
5. **Average Request Time**: Time saved by caching

### Monitoring Dashboard

```python
def print_cache_dashboard():
    """Print a comprehensive cache performance dashboard"""
    stats = get_cache_stats()
    
    print("🚀 Cache Performance Dashboard")
    print("=" * 40)
    print(f"📊 Hit Rate: {stats['hit_rate']:.2%}")
    print(f"📦 Cache Size: {stats['size']}/{stats['max_size']}")
    print(f"💾 Memory Usage: {stats['memory_usage_estimate']}")
    print(f"🔄 Total Requests: {stats['total_requests']}")
    print(f"✅ Cache Hits: {stats['hits']}")
    print(f"❌ Cache Misses: {stats['misses']}")
    print(f"🗑️ Evictions: {stats['evictions']}")
    
    if stats['most_accessed_keys']:
        print(f"🔥 Most Accessed: {stats['most_accessed_keys'][:3]}")
    
    # Health check
    cache = optimization_cache
    is_healthy, message = cache.is_cache_healthy()
    print(f"🏥 Health: {'✅' if is_healthy else '❌'} {message}")
```

## Troubleshooting

### Common Issues

1. **Low Hit Rate**
   - Check if parameters are consistent
   - Verify TTL is not too short
   - Ensure cache is not being cleared too frequently

2. **High Memory Usage**
   - Reduce cache size limit
   - Implement more aggressive eviction
   - Check for memory leaks in cached objects

3. **Cache Misses**
   - Verify parameter consistency
   - Check if cache is being invalidated unexpectedly
   - Monitor TTL expiration

### Debug Mode

Enable debug logging to troubleshoot cache issues:

```python
import logging
logging.getLogger('src.utils.performance_cache').setLevel(logging.DEBUG)

# This will log all cache operations
result = get_cached_optimization_result(objective, weights, constraints)
```

## Testing

The caching system includes comprehensive tests:

```bash
# Run cache system tests
python test_caching_system.py

# Expected output:
# 🚀 Starting Cache System End-to-End Tests
# ✅ Basic cache operations test passed!
# ✅ Cache invalidation test passed!
# ✅ Cache TTL mechanism verified!
# ✅ Cache memory management test passed!
# ✅ Integration test completed!
# 🎉 All cache system tests passed successfully!
```

## API Reference

### Global Functions

- `get_cached_optimization_result(objective, weights, constraints)`: Retrieve cached result
- `cache_optimization_result(objective, weights, constraints, result)`: Store result in cache
- `get_cache_stats()`: Get comprehensive cache statistics
- `clear_optimization_cache()`: Clear all cached entries

### PerformanceCache Class

- `get_optimization_result(objective, weights, constraints)`: Get cached result
- `cache_optimization_result(objective, weights, constraints, result)`: Cache result
- `invalidate_cache(objective, weights, constraints)`: Invalidate specific entries
- `get_performance_metrics()`: Get detailed performance metrics
- `is_cache_healthy()`: Check cache health status

### LRUCache Class (Low-level)

- `get(objective, weights, constraints, ttl)`: Get with custom TTL
- `set(objective, weights, constraints, result)`: Store result
- `invalidate(objective, weights, constraints)`: Invalidate entries
- `get_stats()`: Get basic statistics

## Conclusion

The performance caching system significantly improves the Hong Kong Port Digital Twin's responsiveness by avoiding redundant optimization calculations. By following the best practices and monitoring guidelines in this document, you can ensure optimal cache performance and maintain system efficiency.

For additional support or questions, refer to the test files and implementation code in `src/utils/performance_cache.py`.