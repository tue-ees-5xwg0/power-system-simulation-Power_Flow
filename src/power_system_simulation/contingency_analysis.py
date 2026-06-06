"""Assignment 3: N-1 contingency analysis."""

import pandas as pd
from power_grid_model import ComponentType

from power_system_simulation.case import PowerSystemCase
from power_system_simulation.grid_graph import build_graph_processor
from power_system_simulation.power_flow_processing import PowerFlowProcessor

N_MINUS_ONE_COLUMNS = [
    "Alternative_Line_ID",
    "Max_Loading",
    "Max_Loading_Line_ID",
    "Max_Loading_Timestamp",
]


class LineNotFoundError(Exception):
    """Raised when the line ID does not exist in the grid."""


class LineNotConnectedError(Exception):
    """Raised when the line is not connected on both sides in the base case."""


def _empty_result() -> pd.DataFrame:
    """Empty result table with the correct columns and dtypes."""
    return pd.DataFrame(
        {
            "Alternative_Line_ID": pd.Series(dtype="int64"),
            "Max_Loading": pd.Series(dtype="float64"),
            "Max_Loading_Line_ID": pd.Series(dtype="int64"),
            "Max_Loading_Timestamp": pd.Series(dtype="datetime64[ns]"),
        }
    )


def _scenario_input_data(input_data: dict, line_to_open: int, line_to_close: int) -> dict:
    """Copy the grid with one line opened and one alternative line closed."""
    lines = input_data[ComponentType.line].copy()

    open_mask = lines["id"] == line_to_open
    lines["from_status"][open_mask] = 0
    lines["to_status"][open_mask] = 0

    close_mask = lines["id"] == line_to_close
    lines["from_status"][close_mask] = 1
    lines["to_status"][close_mask] = 1

    scenario = dict(input_data)
    scenario[ComponentType.line] = lines
    return scenario


def run_n_minus_one_analysis(
    case: PowerSystemCase,
    disconnected_line_id: int,
) -> pd.DataFrame:
    """
    Take a line out of service and test which disconnected lines can replace it.

    For each alternative line, run a time-series power flow over the whole period
    and report the worst line loading. Returns one row per alternative, or an
    empty table if there are none.
    """
    lines = case.input_data[ComponentType.line]

    if disconnected_line_id not in set(lines["id"].tolist()):
        raise LineNotFoundError(f"Line ID {disconnected_line_id} is not a valid line.")

    line_row = lines[lines["id"] == disconnected_line_id][0]
    if not (line_row["from_status"] and line_row["to_status"]):
        raise LineNotConnectedError(f"Line {disconnected_line_id} must be connected on both sides.")

    graph = build_graph_processor(case.input_data)
    alternative_line_ids = graph.find_alternative_edges(disconnected_line_id)

    if not alternative_line_ids:
        return _empty_result()

    rows = []
    for alternative_line_id in alternative_line_ids:
        scenario_input = _scenario_input_data(
            case.input_data,
            line_to_open=disconnected_line_id,
            line_to_close=alternative_line_id,
        )

        processor = PowerFlowProcessor(
            scenario_input,
            case.active_power_profile,
            case.reactive_power_profile,
        )
        processor.run_time_series()
        line_summary = processor.get_line_summary()

        worst_line_id = line_summary["Max_Loading"].idxmax()
        rows.append(
            {
                "Alternative_Line_ID": alternative_line_id,
                "Max_Loading": line_summary.loc[worst_line_id, "Max_Loading"],
                "Max_Loading_Line_ID": worst_line_id,
                "Max_Loading_Timestamp": line_summary.loc[worst_line_id, "Max_Loading_Timestamp"],
            }
        )

    return pd.DataFrame(rows, columns=N_MINUS_ONE_COLUMNS)
