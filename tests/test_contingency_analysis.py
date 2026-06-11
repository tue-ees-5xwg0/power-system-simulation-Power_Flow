"""Tests for the Assignment 3 N-1 contingency analysis."""

import pandas as pd
import pytest
from grid_fixtures import TIMESTAMPS, build_case
from power_grid_model import ComponentType

from power_system_simulation.contingency_analysis import (
    N_MINUS_ONE_COLUMNS,
    LineNotConnectedError,
    LineNotFoundError,
    run_n_minus_one_analysis,
)


def test_invalid_line_id_raises():
    with pytest.raises(LineNotFoundError):
        run_n_minus_one_analysis(build_case(), disconnected_line_id=999)


def test_disconnected_line_raises():
    # Line 32 is open in the base case.
    with pytest.raises(LineNotConnectedError):
        run_n_minus_one_analysis(build_case(), disconnected_line_id=32)


def test_returns_alternative_scenario_table():
    # Opening line 30 isolates node 3; closing line 32 restores the grid.
    result = run_n_minus_one_analysis(build_case(), disconnected_line_id=30)

    assert list(result.columns) == N_MINUS_ONE_COLUMNS
    assert len(result) == 1

    row = result.iloc[0]
    assert row["Alternative_Line_ID"] == 32
    assert row["Max_Loading"] > 0.0
    assert row["Max_Loading_Line_ID"] in {30, 31, 32}
    assert row["Max_Loading_Timestamp"] in set(TIMESTAMPS)


def test_no_alternatives_returns_empty_table():
    # Drop line 32 so there is no spare line to restore the grid.
    case = build_case()
    case.input_data[ComponentType.line] = case.input_data[ComponentType.line][:2]

    result = run_n_minus_one_analysis(case, disconnected_line_id=30)

    assert result.empty
    assert list(result.columns) == N_MINUS_ONE_COLUMNS
    assert result["Max_Loading_Timestamp"].dtype == "datetime64[ns]"
    assert result["Alternative_Line_ID"].dtype == "int64"


def test_max_loading_is_a_valid_value():
    result = run_n_minus_one_analysis(build_case(), disconnected_line_id=30)
    row = result.iloc[0]

    assert row["Max_Loading"] > 0.0
    assert isinstance(row["Max_Loading_Timestamp"], pd.Timestamp)
