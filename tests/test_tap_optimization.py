"""Tests for Assignment 3 transformer tap optimization."""

import pandas as pd
import pytest
from grid_fixtures import build_case

from power_system_simulation.tap_optimization import (
    TAP_OPTIMIZATION_COLUMNS,
    optimize_tap_position,
)


def test_optimize_tap_position_returns_expected_columns():
    result = optimize_tap_position(build_case(), criterion="loss")

    assert list(result.columns) == TAP_OPTIMIZATION_COLUMNS


def test_optimize_tap_position_evaluates_all_taps():
    result = optimize_tap_position(build_case(), criterion="loss")

    assert set(result["Tap_Position"]) == set(range(-5, 6))
    assert len(result) == 11


def test_optimize_tap_position_marks_one_optimal_tap():
    result = optimize_tap_position(build_case(), criterion="loss")

    assert result["Is_Optimal"].sum() == 1


def test_loss_criterion_selects_minimum_loss():
    result = optimize_tap_position(build_case(), criterion="loss")

    optimal_row = result[result["Is_Optimal"]].iloc[0]

    assert optimal_row["Total_Loss"] == result["Total_Loss"].min()


def test_voltage_deviation_criterion_selects_minimum_deviation():
    result = optimize_tap_position(build_case(), criterion="voltage_deviation")

    optimal_row = result[result["Is_Optimal"]].iloc[0]

    assert optimal_row["Voltage_Deviation"] == result["Voltage_Deviation"].min()


def test_invalid_criterion_raises():
    with pytest.raises(ValueError):
        optimize_tap_position(build_case(), criterion="invalid")


def test_result_contains_numeric_metrics():
    result = optimize_tap_position(build_case(), criterion="loss")

    assert pd.api.types.is_numeric_dtype(result["Total_Loss"])
    assert pd.api.types.is_numeric_dtype(result["Voltage_Deviation"])
    assert (result["Total_Loss"] >= 0.0).all()
    assert (result["Voltage_Deviation"] >= 0.0).all()
