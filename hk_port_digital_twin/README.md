# Hong Kong Port Digital Twin

A comprehensive digital twin simulation system for Hong Kong's port operations.

## Project Structure

- `src/` - Source code modules
  - `core/` - Core business logic (ships, berths, containers)
  - `dashboard/` - Web dashboard components
  - `utils/` - Utility functions and helpers
- `tests/` - Test files
- `config/` - Configuration files
- `data/` - Data files and samples
  - `raw/` - Raw input data
  - `processed/` - Processed data
  - `sample/` - Sample data for testing
- `docs/` - Documentation
  - `caching_system_guide.md` - Comprehensive caching system documentation
  - `caching_quick_reference.md` - Quick reference for developers

## Features Implemented

### Phase 2.1: Ship Management Module ✅
- Ship dataclass with validation
- ShipManager for ship operations
- Comprehensive test coverage

### Phase 2.2: Berth Management Module ✅
- Berth dataclass with type validation
- BerthManager for berth allocation
- Smart allocation algorithms
- Statistics and history tracking

### Performance Caching System ✅
- LRU cache with TTL support for optimization results
- Automatic cache invalidation on data changes
- Comprehensive performance monitoring and statistics
- Thread-safe operations with memory management
- Integration with data loading pipeline

## Technical Scope and Honest Limitations

- **Optimization is heuristic, not learned AI.** Berth allocation and most scenario recommendations use deterministic rules, configured multipliers, historical averages, standard deviations, and sampled values. They are useful prototype decision aids, not trained optimization models.
- **The narrow trained-model exception is throughput forecasting.** Cargo forecasting fits scikit-learn `LinearRegression` models to historical throughput trends and applies simple seasonal adjustments. It does not power the broader scenario optimizer.
- **Scenario outputs are illustrative.** Scenario parameter sets adjust arrival rates, vessel sizes, crane efficiency, processing rates, and related assumptions. Production decision support would require calibrated inputs, repeated Monte Carlo runs, confidence intervals, and validation against real outcomes.
- **Persistence is file-based, not SQLite.** Source and generated data are stored in XML/CSV/JSON files; runtime state is held in Streamlit session state and in-memory caches. There is no application database in the current implementation.

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Run tests:
   ```bash
   pytest tests/
   ```

4. Start the application:
   ```bash
   python -m src.main
   ```

## Development Roadmap

- ✅ Phase 2.1: Ship Management Module
- ✅ Phase 2.2: Berth Management Module
- 🔄 Phase 2.3: Container Handling Module
- 📋 Phase 3: Simulation Integration
- 📋 Phase 4: Dashboard Development

## Contributing

This project follows standard Python development practices. Please ensure all tests pass before submitting changes.

## License

This project is part of the Hong Kong Port Digital Twin initiative.