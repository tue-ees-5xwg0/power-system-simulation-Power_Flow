# power-system-simulation

A Python package developed for the TU/e *5XWG0 Power System Computation and Simulation* course by team Power_Flow. The package provides tools for graph-based distribution grid analysis, time-series power flow calculations, and low-voltage grid analytics.

## Features

### Assignment 1 – Graph Processing

Implements graph-based topology analysis for radial distribution grids.

- Validation of radial network topology
- Detection of disconnected networks
- Detection of cycles
- Downstream vertex identification
- Alternative edge identification for topology restoration

### Assignment 2 – Time-Series Power Flow

Provides a wrapper around the Power Grid Model (PGM) library for time-series power flow simulations.

- Import of PGM JSON network models
- Import of active and reactive load profiles
- Batch power flow calculations
- Voltage aggregation tables
- Line loading and loss aggregation tables

### Assignment 3 – Low-Voltage Grid Analytics

Implements higher-level LV grid analysis functionality.

- Input data validation
- EV penetration analysis
- Transformer tap optimization
- N-1 contingency analysis

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

Clone the repository:

```shell
git clone <https://github.com/tue-ees-5xwg0/power-system-simulation-Power_Flow.git>
cd power-system-simulation
```

Install dependencies:

```shell
uv sync
```

After installation, run the test suite:

```shell
uv run pytest
```

## Code Style and Quality Check

This project uses [ruff](https://docs.astral.sh/ruff/) for linting and formatting.

Check and automatically fix code issues:

```shell
uv run ruff check --fix .
```

Format the codebase:

```shell
uv run ruff format .
```

## Test Coverage

Run the full test suite with coverage:

```shell
uv run pytest --cov=src --cov-report=html
```

The project currently maintains approximately 99% test coverage.

## Package Structure

```text
src/
└── power_system_simulation/
    ├── case.py
    ├── validation.py
    ├── grid_graph.py
    ├── ev_analysis.py
    ├── tap_optimization.py
    ├── contingency_analysis.py
    ├── graph_processing.py
    ├── power_flow_processing.py
    └── __init__.py

tests/
├── test_graph_processing.py
├── test_power_flow_processing.py
├── test_validation.py
├── test_ev_analysis.py
├── test_tap_optimization.py
└── test_contingency_analysis.py
```

## Assignment 3 API

Assignment 3 functionality is built around the `PowerSystemCase` dataclass.

### PowerSystemCase

```python
from power_system_simulation import PowerSystemCase

case = PowerSystemCase(
    input_data=input_data,
    active_power_profile=active_profile,
    reactive_power_profile=reactive_profile,
    lv_feeder_ids=lv_feeder_ids,
    ev_active_power_profiles=ev_profiles,
)
```

### Input Validation

```python
from power_system_simulation import validate_case

validate_case(case)
```

### EV Penetration Analysis

```python
from power_system_simulation import run_ev_penetration_analysis

voltage_summary, line_summary = run_ev_penetration_analysis(
    case,
    penetration_level=0.20,
    random_seed=42,
)
```

#### EV Assignment Note

The number of EVs assigned per feeder is calculated according to the assignment specification:

```text
floor(
    penetration_level
    × total_number_of_houses
    ÷ number_of_feeders
)
```

If a feeder contains fewer houses than the requested number of EV assignments, the implementation assigns EVs to all available houses in that feeder.

### Transformer Tap Optimization

```python
from power_system_simulation import optimize_tap_position

results = optimize_tap_position(
    case,
    criterion="loss",
)
```

### N-1 Contingency Analysis

```python
from power_system_simulation import run_n_minus_one_analysis

results = run_n_minus_one_analysis(
    case,
    disconnected_line_id=123,
)
```

## Working with Jupyter Notebooks

Jupyter notebooks in the `example/` folder can be opened directly in VS Code. The project includes `ipykernel` in the development dependencies, which allows VS Code to run notebook cells using the `.venv` environment.

## Folder Structure of the Repository

- `src/power_system_simulation` contains the package source code.
- `tests` contains all unit tests.
- `example` contains demonstration notebooks.
- `.github/workflows` contains continuous integration configuration.
- `.vscode` contains Visual Studio Code settings.

## Testing

```shell
uv run pytest
```

```shell
uv run pytest --cov=src --cov-report=html
```

## Dependencies

Main dependencies:

- power-grid-model
- numpy
- pandas
- pytest

Additional development tools:

- ruff
- pytest-cov

## License

This project is licensed under the BSD 3-Clause License.
