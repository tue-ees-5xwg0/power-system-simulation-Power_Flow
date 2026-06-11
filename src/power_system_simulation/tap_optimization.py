"""Assignment 3: transformer tap position optimization."""

from typing import Literal

import pandas as pd
from power_grid_model import ComponentType

from power_system_simulation.case import PowerSystemCase
from power_system_simulation.power_flow_processing import PowerFlowProcessor
from power_system_simulation.validation import validate_case

TAP_OPTIMIZATION_COLUMNS = [
    "Tap_Position",
    "Total_Loss",
    "Voltage_Deviation",
    "Is_Optimal",
]


def _tap_positions(transformer) -> list[int]:
    """Return all available transformer tap positions."""
    tap_min = int(transformer["tap_min"])
    tap_max = int(transformer["tap_max"])

    lower = min(tap_min, tap_max)
    upper = max(tap_min, tap_max)

    return list(range(lower, upper + 1))


def _scenario_input_data(input_data: dict, tap_position: int) -> dict:
    """Copy the grid and set the transformer tap position."""
    transformer = input_data[ComponentType.transformer].copy()
    transformer["tap_pos"][0] = tap_position

    scenario = dict(input_data)
    scenario[ComponentType.transformer] = transformer
    return scenario


def _voltage_deviation(processor: PowerFlowProcessor) -> float:
    """
    Calculate average deviation of node voltage extrema from 1.0 p.u.

    For each node, the maximum and minimum voltage over all timestamps are
    compared to 1.0 p.u., then averaged over all nodes.
    """
    node_results = processor.output_data[ComponentType.node]
    voltages = node_results["u_pu"]

    max_deviation = abs(voltages.max(axis=0) - 1.0)
    min_deviation = abs(voltages.min(axis=0) - 1.0)

    return float(((max_deviation + min_deviation) / 2).mean())


def optimize_tap_position(
    case: PowerSystemCase,
    criterion: Literal["loss", "voltage_deviation"] = "loss",
) -> pd.DataFrame:
    """
    Find the optimal transformer tap position.

    Evaluates all available tap positions using the original household load
    profiles only. The optimal tap is selected based on total energy loss or
    average voltage deviation from 1.0 p.u.
    """
    validate_case(case)

    if criterion not in {"loss", "voltage_deviation"}:
        raise ValueError("criterion must be either 'loss' or 'voltage_deviation'.")

    transformer = case.input_data[ComponentType.transformer][0]

    rows = []
    for tap_position in _tap_positions(transformer):
        scenario_input = _scenario_input_data(case.input_data, tap_position)

        processor = PowerFlowProcessor(
            scenario_input,
            case.active_power_profile,
            case.reactive_power_profile,
        )
        processor.run_time_series()

        line_summary = processor.get_line_summary()
        total_loss = float(line_summary["Total_Loss"].sum())
        voltage_deviation = _voltage_deviation(processor)

        rows.append(
            {
                "Tap_Position": tap_position,
                "Total_Loss": total_loss,
                "Voltage_Deviation": voltage_deviation,
            }
        )

    result = pd.DataFrame(rows, columns=TAP_OPTIMIZATION_COLUMNS[:-1])

    metric_column = {
        "loss": "Total_Loss",
        "voltage_deviation": "Voltage_Deviation",
    }[criterion]

    optimal_index = result[metric_column].idxmin()
    result["Is_Optimal"] = False
    result.loc[optimal_index, "Is_Optimal"] = True

    return result[TAP_OPTIMIZATION_COLUMNS]
