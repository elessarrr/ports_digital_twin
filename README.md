# Hong Kong Port Digital Twin

**Real-time intelligence for port operations planning and scenario analysis**

🔗 **Live Demo**: [https://portsdigitaltwin-5hgeebdz2ipzcuja5skblx.streamlit.app](https://portsdigitaltwin-5hgeebdz2ipzcuja5skblx.streamlit.app)

---

## Overview

A digital twin simulation built on publicly available data from Hong Kong's Marine Department. The system processes real vessel movement data to enable port planners to test allocation strategies, model disruption scenarios, and identify optimization opportunities.

The dashboard ingests live XML feeds of vessel arrivals and departures, combined with 14+ years of historical throughput statistics (2011-2025), translating complex operational questions into interactive simulations with quantifiable outputs.

**Presented at**: IET Digital Twins and Applications Conference, Hong Kong Polytechnic University (January 2026)

---

## Problem Space

Port operations planning traditionally relies on reactive coordination—responding to vessel arrivals as they occur, allocating berths based on availability, and managing disruptions manually. This approach works but leaves optimization opportunities unexplored.

Planners face recurring questions:
- How would berth allocation perform under peak demand (+30% volume)?
- What happens to wait times when typhoons close specific berths?
- Where are the bottlenecks when vessel arrival patterns shift?
- How much capacity headroom exists before queuing becomes problematic?

Standard tools (Excel models, PowerBI dashboards) excel at historical reporting but can't simulate forward scenarios or test allocation strategies before implementation. Digital twins shift the paradigm from reactive operations to predictive intelligence—anticipating issues before they occur and quantifying the impact of operational changes before committing resources.

---

## Key Capabilities

### Real-Time Data Processing
- Automated parsing of Hong Kong Marine Department XML feeds (20-minute refresh cycle)
- Vessel categorization by type, size, and cargo classification
- Live berth occupancy tracking and queue status monitoring
- Historical data integration across 1.7M+ TEU throughput records

### Scenario Simulation
- **Demand Modeling**: Peak traffic (+30%), normal operations, off-peak conditions
- **Disruption Analysis**: Typhoon impacts with berth closures and reduced capacity
- **Capacity Planning**: Infrastructure changes (berth additions, handling rate improvements)
- **Comparative Analysis**: Side-by-side scenario evaluation with quantified metrics

### Operational Metrics
- Berth utilization rates and capacity constraints
- Wait time distributions across demand scenarios
- Container throughput by mode (sea vs. river)
- Year-over-year trend analysis with seasonal patterns

### Visualization Layer
- Port status dashboard with live vessel positions
- Scenario comparison charts (baseline vs. stress tests)
- Historical trend analysis (14+ years)
- Interactive maritime traffic map (MarineTraffic integration)

---

## Technical Architecture

### Data Pipeline
```
Hong Kong Marine Dept XML Feeds → Parser → Validation → SQLite Storage
                                                           ↓
                                              Simulation Engine (SimPy)
                                                           ↓
                                              Streamlit Dashboard
```

### Core Components

**Simulation Engine** (`src/core/`)
- Discrete event simulation using SimPy
- Ship queuing and berth allocation logic
- Container handling time calculations
- Multi-scenario state management

**Data Processing** (`src/utils/`)
- XML parsing for real-time vessel data
- CSV processing for historical statistics
- Data validation and quality checks
- Automated deduplication and cleaning

**Analytics Layer** (`src/analytics/`, `src/ai/`)
- Time series forecasting using historical trends
- Berth optimization algorithms
- Predictive models for wait time estimation
- Scenario-aware performance calculations

**Dashboard** (`src/dashboard/`)
- Streamlit-based interactive interface
- Plotly visualizations for metrics
- Real-time data refresh capabilities
- Scenario configuration and comparison tools

### Technology Stack
- **Frontend**: Streamlit (rapid prototyping, interactive widgets)
- **Simulation**: SimPy 4.0+ (discrete event modeling)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly (interactive charts)
- **Analytics**: Scikit-learn, Statsmodels (forecasting, optimization)
- **Storage**: SQLite (local caching), file-based data lake
- **Deployment**: Streamlit Community Cloud

---

## Data Sources

### Primary Sources (Public Data)
1. **Hong Kong Marine Department**
   - Vessel arrival/departure XML feeds
   - Real-time vessel movement tracking
   - Updated every 36 hours

2. **Hong Kong Census and Statistics Department**
   - Container throughput statistics (2011-2025)
   - Cargo breakdown by type and handling location
   - Seasonal and trend data for forecasting

3. **MarineTraffic** (Optional Enhancement)
   - Live vessel position mapping
   - AIS data integration for real-time tracking
   - Global maritime traffic visualization

All data used is publicly available. No proprietary or restricted port operational data is included.

---

## Project Structure

```
ports_digital_twin/
├── hk_port_digital_twin/          # Main application package
│   ├── src/
│   │   ├── core/                  # Simulation engine (ships, berths, containers)
│   │   ├── dashboard/             # Streamlit interface
│   │   ├── scenarios/             # Scenario definitions and simulators
│   │   ├── analytics/             # Performance analysis and forecasting
│   │   ├── ai/                    # Optimization and predictive models
│   │   ├── utils/                 # Data loading and processing utilities
│   │   └── integration/           # Enhanced simulation features
│   ├── config/                    # Port specifications and settings
│   ├── data/                      # Sample and processed data
│   └── raw_data/                  # Original government datasets
├── planning/                      # Implementation roadmaps and documentation
├── tasks/                         # PRDs and task breakdowns
├── requirements.txt               # Python dependencies
└── streamlit_app.py              # Application entry point
```

**Lines of Code**: 80+ Python modules across simulation, analytics, and dashboard layers

---

## Getting Started

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. Clone the repository
```bash
git clone https://github.com/elessarrr/ports_digital_twin.git
cd ports_digital_twin
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the dashboard locally
```bash
streamlit run streamlit_app.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Running Simulations

Navigate through the dashboard tabs:
- **📊 Dashboard**: Overview of current port status and key metrics
- **🎯 Scenarios**: Run and compare different operational scenarios
- **📈 Analytics**: Historical trends and forecasting
- **🌊 Live Map**: Real-time vessel positions via MarineTraffic

---

## Use Cases

### Port Authority Planning
- Capacity planning for infrastructure investments
- Impact analysis of new berth construction
- Disruption preparedness and contingency planning

### Operations Optimization
- Berth allocation strategy testing
- Peak season resource planning
- Maintenance window scheduling

### Policy Analysis
- Regulatory impact assessment
- Environmental compliance modeling
- Safety protocol effectiveness

---

## Limitations and Disclaimers

**This is a prototype for exploration, not a production operations system.**

Current limitations:
- Simplified berth allocation logic (FCFS with basic constraints)
- Container handling times use averaged estimates, not real-time equipment data
- Weather impacts are modeled parametrically, not integrated with live forecasts
- No integration with terminal operator systems or proprietary data
- Validation against actual operational outcomes is limited

**This project was developed in a personal capacity using publicly available data and tools, independent of any current employment.**

---

## Implementation Notes

### Technical Challenges
- Data quality in XML feeds required extensive validation and edge-case handling (vessel name encoding, missing fields, duplicate records)
- Balancing simulation fidelity against performance requirements for interactive use
- Determining acceptable simplifications without breaking operational realism
- Managing state across multiple concurrent scenarios

### Future Enhancements
- Real-time AIS data integration for vessel position tracking
- Predictive models for arrival time estimation using historical patterns
- Multi-objective optimization (throughput vs. wait time vs. emissions)
- Terminal operator API integration for actual equipment performance data

---

## Conference Presentation

Presented at the **IET Digital Twins and Applications Conference** (Hong Kong Polytechnic University, January 2026) as a demonstration of real-time intelligence for physical operations.

The presentation included a live dashboard demonstration with audience interaction via QR code. Q&A discussions covered extending these concepts to rail transit systems, manufacturing operations, and other domains requiring physical-digital integration.

---

## License

This project is released for educational and demonstration purposes. Data sources retain their original licenses (Hong Kong Government Open Data License).

---

## Contact

**Bhavesh Rajwani**  
Product Manager, Digital Transformation & Industry 4.0  

- LinkedIn: [linkedin.com/in/bhavesh-rajwani](https://www.linkedin.com/in/bhavesh-rajwani/)
- Conference Presentation: IET Digital Twins Conference, PolyU Hong Kong (January 2026)

**Note**: This project was developed in a personal capacity, independent of current employment, using publicly available data and open-source tools.

---

## Acknowledgments

- Hong Kong Marine Department for providing accessible vessel data
- IET Hong Kong for hosting the digital twin conference
- Conference organizers and attendees for valuable feedback
- Open-source community for simulation and visualization libraries

---

*Exploring real-time intelligence for physical operations.*
