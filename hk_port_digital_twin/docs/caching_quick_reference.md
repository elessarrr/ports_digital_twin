# Caching System Quick Reference

## 🚀 Quick Start

```python
from src.utils.performance_cache import (
    get_cached_optimization_result,
    cache_optimization_result,
    get_cache_stats
)

# Check cache first
cached = get_cached_optimization_result(objective, weights, constraints)
if cached is None:
    result = expensive_optimization()
    cache_optimization_result(objective, weights, constraints, result)
else:
    result = cached
```

## 📊 Common Operations

### Cache a Result
```python
cache_optimization_result(
    objective="minimize_cost",
    weights={"cost": 0.8, "time": 0.2},
    constraints={"vessels": 20},
    result=optimization_result
)
```

### Get Cached Result
```python
result = get_cached_optimization_result(
    objective="minimize_cost",
    weights={"cost": 0.8, "time": 0.2},
    constraints={"vessels": 20}
)
```

### Check Cache Stats
```python
stats = get_cache_stats()
print(f"Hit rate: {stats['hit_rate']:.2%}")
print(f"Size: {stats['size']}/{stats['max_size']}")
```

### Clear Cache
```python
from src.utils.performance_cache import clear_optimization_cache
cleared = clear_optimization_cache()
```

## 🔧 Advanced Usage

### Custom TTL
```python
from src.utils.performance_cache import optimization_cache
optimization_cache._cache.set(objective, weights, constraints, result, ttl=300)
```

### Selective Invalidation
```python
optimization_cache.invalidate_cache(objective="minimize_cost")
```

### Health Check
```python
is_healthy, message = optimization_cache.is_cache_healthy()
```

## 📈 Monitoring

```python
def cache_dashboard():
    stats = get_cache_stats()
    print(f"📊 Hit Rate: {stats['hit_rate']:.2%}")
    print(f"📦 Size: {stats['size']}/{stats['max_size']}")
    print(f"💾 Memory: {stats['memory_usage_estimate']}")
    print(f"🔄 Requests: {stats['total_requests']}")
```

## ⚠️ Best Practices

1. **Always check cache first** before expensive operations
2. **Use consistent parameters** for cache keys
3. **Handle cache failures gracefully** with try/catch
4. **Monitor hit rates** regularly
5. **Clear cache** when data changes

## 🐛 Debugging

```python
import logging
logging.getLogger('src.utils.performance_cache').setLevel(logging.DEBUG)
```

## 🧪 Testing

```bash
python test_caching_system.py
```

## 📚 Full Documentation

See `docs/caching_system_guide.md` for comprehensive documentation.