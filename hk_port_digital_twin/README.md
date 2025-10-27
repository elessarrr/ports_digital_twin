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