# Wait Time Calculator Guide

## Overview

The Wait Time Calculator is an enhanced system for calculating ship waiting times in the Hong Kong Port Digital Twin. It provides scenario-aware wait time calculations using a threshold-based approach that ensures logical ordering: Peak Season > Normal Operations > Low Season.

## Key Features

### 🎯 Threshold-Based System
- **Intuitive Logic**: Peak season naturally produces longer wait times than normal operations, which are longer than low season
- **Configurable Bands**: Each scenario has defined minimum and maximum wait time ranges
- **Statistical Distribution**: Uses normal distribution within each band for realistic variability

### 📊 Multiple Calculation Methods
- **Single Values**: Get a single wait time for immediate use
- **Batch Calculations**: Generate multiple samples for statistical analysis and charting
- **Legacy Support**: Fallback to exponential system if needed

### 🔧 Robust Input Validation
- **Type Checking**: Ensures all inputs are of correct types
- **Range Validation**: Validates multipliers and sample counts
- **Scenario Validation**: Checks against known scenario names

## Usage Examples

### Basic Usage

```python
from utils.wait_time_calculator import WaitTimeCalculator, calculate_wait_time

# Using the class
calculator = WaitTimeCalculator()
wait_time = calculator.calculate_wait_time('Normal Operations')
print(f"Wait time: {wait_time:.2f} hours")

# Using the standalone function
wait_time = calculate_wait_time('Peak Season')
print(f"Peak season wait time: {wait_time:.2f} hours")
```

### Advanced Usage

```python
# Calculate with multiplier
wait_time = calculator.calculate_wait_time('Normal Operations', multiplier=1.5)

# Generate multiple samples for analysis
wait_times = calculator.calculate_wait_time('Peak Season', num_samples=100)
print(f"Average wait time: {np.mean(wait_times):.2f} hours")
print(f"Standard deviation: {np.std(wait_times):.2f} hours")

# Use legacy exponential method
from utils.wait_time_calculator import WaitTimeMethod
legacy_calculator = WaitTimeCalculator(method=WaitTimeMethod.EXPONENTIAL_LEGACY)
legacy_wait_time = legacy_calculator.calculate_wait_time('Normal Operations')
```

## Scenarios

### Peak Season
- **Range**: 8.0 - 20.0 hours
- **Mean**: 14.0 hours
- **Description**: High demand period with extended wait times
- **Use Case**: Holiday seasons, major shipping events

### Normal Operations
- **Range**: 4.0 - 12.0 hours  
- **Mean**: 8.0 hours
- **Description**: Standard operations with moderate wait times
- **Use Case**: Regular business operations

### Low Season
- **Range**: 1.0 - 6.0 hours
- **Mean**: 3.5 hours
- **Description**: Low demand period with minimal wait times
- **Use Case**: Off-peak periods, reduced shipping activity

## API Reference

### WaitTimeCalculator Class

#### Constructor
```python
WaitTimeCalculator(method: WaitTimeMethod = WaitTimeMethod.THRESHOLD_BANDS)
```

#### Methods

##### calculate_wait_time()
```python
calculate_wait_time(scenario: str, multiplier: float = 1.0, num_samples: int = 1) -> Union[float, np.ndarray]
```

**Parameters:**
- `scenario`: Scenario name ('Peak Season', 'Normal Operations', 'Low Season')
- `multiplier`: Multiplier to apply to calculated wait time (default: 1.0)
- `num_samples`: Number of wait time samples to generate (default: 1)

**Returns:**
- Single wait time (float) if `num_samples=1`
- Array of wait times (np.ndarray) if `num_samples > 1`

**Raises:**
- `ValueError`: Invalid scenario, negative multiplier, or invalid num_samples
- `TypeError`: Incorrect input types

##### get_scenario_statistics()
```python
get_scenario_statistics(scenario: str) -> Dict[str, Any]
```

Returns statistical information about a scenario including min/max ranges, mean, and distribution type.

##### validate_logical_ordering()
```python
validate_logical_ordering(sample_size: int = 1000) -> Dict[str, Any]
```

Validates that the logical ordering (Peak > Normal > Low) is maintained across multiple samples.

### Standalone Functions

##### calculate_wait_time()
```python
calculate_wait_time(scenario_name: str, use_legacy: bool = False) -> float
```

Convenience function for simple wait time calculations.

##### get_default_wait_time()
```python
get_default_wait_time() -> float
```

Returns a default wait time for fallback scenarios.

## Integration with Dashboard

The wait time calculator is integrated with the Streamlit dashboard in several ways:

### Real-time Calculations
```python
# Dashboard usage example
if calculate_wait_time:
    waiting_times = [calculate_wait_time(scenario_name) * params['waiting_time_multiplier']
                    for _ in range(num_ships)]
```

### Chart Generation
```python
# Generate data for wait time distribution charts
if calculate_wait_time:
    waiting_times = [calculate_wait_time(scenario_name) * params['waiting_time_multiplier'] 
                    for _ in range(20)]
```

### Performance Metrics
```python
# Calculate average wait times for KPIs
if calculate_wait_time:
    avg_waiting_time = calculate_wait_time(scenario_name) * params['waiting_time_multiplier']
```

## Performance Characteristics

### Single Calculations
- **Speed**: < 0.005 seconds per calculation
- **Memory**: Minimal memory footprint
- **Scalability**: Suitable for real-time dashboard updates

### Batch Calculations
- **Speed**: < 0.01 seconds for 100 samples
- **Memory**: Efficient numpy array operations
- **Scalability**: Suitable for statistical analysis and charting

## Error Handling

The system provides comprehensive error handling:

### Input Validation Errors
```python
# Invalid scenario
calculate_wait_time('Invalid Scenario')  # Raises ValueError

# Negative multiplier
calculate_wait_time('Normal Operations', multiplier=-1.0)  # Raises ValueError

# Invalid sample count
calculate_wait_time('Normal Operations', num_samples=0)  # Raises ValueError
```

### Graceful Degradation
- **Unknown Scenarios**: Returns safe default values with error logging
- **Calculation Errors**: Falls back to scenario-appropriate defaults
- **Type Errors**: Clear error messages for debugging

## Testing

### Unit Tests
- **Location**: `tests/test_wait_time_calculator.py`
- **Coverage**: 20 test cases covering all functionality
- **Command**: `python -m pytest tests/test_wait_time_calculator.py -v`

### Integration Tests
- **Location**: `tests/test_integration_wait_time.py`
- **Coverage**: Dashboard integration, cross-module compatibility
- **Command**: `python -m pytest tests/test_integration_wait_time.py -v`

## Configuration

### Threshold Bands
Threshold bands can be customized by modifying the `_define_threshold_bands()` method:

```python
def _define_threshold_bands(self) -> Dict[str, Dict[str, Any]]:
    return {
        ScenarioType.PEAK.value: {
            "min_hours": 8.0,    # Customize minimum
            "max_hours": 20.0,   # Customize maximum
            "mean_hours": 14.0,  # Customize target mean
            "std_hours": 2.0,    # Customize variability
            # ... other parameters
        }
        # ... other scenarios
    }
```

### Logging
The system uses structured logging for monitoring and debugging:

```python
import logging
logger = logging.getLogger('utils.wait_time_calculator')
logger.setLevel(logging.INFO)
```

## Migration from Legacy System

### Backward Compatibility
The new system maintains backward compatibility with the legacy exponential system:

```python
# Use legacy method
calculator = WaitTimeCalculator(method=WaitTimeMethod.EXPONENTIAL_LEGACY)
wait_time = calculator.calculate_wait_time('Normal Operations')

# Or use the standalone function with legacy flag
wait_time = calculate_wait_time('Peak Season', use_legacy=True)
```

### Gradual Migration
1. **Phase 1**: Deploy new system with legacy fallback
2. **Phase 2**: Test new system in parallel
3. **Phase 3**: Switch to new system as default
4. **Phase 4**: Remove legacy system (future)

## Troubleshooting

### Common Issues

#### Import Errors
```python
# Ensure proper path setup
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
```

#### Unexpected Results
- Check scenario name spelling and capitalization
- Verify multiplier is positive
- Ensure num_samples is at least 1

#### Performance Issues
- Use batch calculations for multiple samples
- Cache calculator instances for repeated use
- Monitor memory usage with large sample sizes

### Debug Mode
Enable debug logging for detailed information:

```python
import logging
logging.getLogger('utils.wait_time_calculator').setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features
- **Dynamic Thresholds**: Adjust bands based on historical data
- **Machine Learning**: Incorporate ML models for prediction
- **Real-time Updates**: Update thresholds based on current conditions
- **API Integration**: REST API for external system integration

### Contributing
To contribute to the wait time calculator:

1. **Fork** the repository
2. **Create** a feature branch
3. **Add** comprehensive tests
4. **Update** documentation
5. **Submit** a pull request

## Support

For questions or issues:
- **Documentation**: This guide and inline code comments
- **Tests**: Comprehensive test suites for examples
- **Logging**: Detailed error messages and warnings
- **Code Review**: Well-commented, maintainable code

---

*Last updated: October 2024*
*Version: 2.0.0 (Threshold-based system)*