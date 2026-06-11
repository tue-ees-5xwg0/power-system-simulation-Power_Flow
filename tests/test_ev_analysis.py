"""Tests for Assignment 3 EV penetration analysis."""

import pandas as pd
import pytest
from grid_fixtures import build_case

from power_system_simulation.ev_analysis import (
    _houses_per_feeder,
    run_ev_penetration_analysis,
)


def test_houses_per_feeder_maps_loads_correctly():
    result = _houses_per_feeder(build_case(with_ev=True))

    assert result == {
        30: [40],
        31: [41],
    }


def test_ev_analysis_requires_ev_profiles():
    with pytest.raises(ValueError):
        run_ev_penetration_analysis(
            build_case(with_ev=False),
            penetration_level=0.5,
            random_seed=0,
        )


def test_ev_analysis_rejects_invalid_penetration_level():
    with pytest.raises(ValueError):
        run_ev_penetration_analysis(
            build_case(with_ev=True),
            penetration_level=1.5,
            random_seed=0,
        )


def test_ev_analysis_returns_assignment_2_tables():
    voltage_summary, line_summary = run_ev_penetration_analysis(
        build_case(with_ev=True),
        penetration_level=1.0,
        random_seed=0,
    )

    assert isinstance(voltage_summary, pd.DataFrame)
    assert isinstance(line_summary, pd.DataFrame)

    assert list(voltage_summary.columns) == [
        "Max_Voltage",
        "Max_Voltage_Node",
        "Min_Voltage",
        "Min_Voltage_Node",
    ]

    assert list(line_summary.columns) == [
        "Total_Loss",
        "Max_Loading",
        "Max_Loading_Timestamp",
        "Min_Loading",
        "Min_Loading_Timestamp",
    ]


def test_ev_analysis_zero_penetration_runs_without_ev_assignment():
    voltage_summary, line_summary = run_ev_penetration_analysis(
        build_case(with_ev=True),
        penetration_level=0.0,
        random_seed=0,
    )

    assert not voltage_summary.empty
    assert not line_summary.empty


def test_ev_analysis_is_reproducible_with_fixed_seed():
    result_1 = run_ev_penetration_analysis(
        build_case(with_ev=True),
        penetration_level=1.0,
        random_seed=42,
    )

    result_2 = run_ev_penetration_analysis(
        build_case(with_ev=True),
        penetration_level=1.0,
        random_seed=42,
    )

    pd.testing.assert_frame_equal(result_1[0], result_2[0])
    pd.testing.assert_frame_equal(result_1[1], result_2[1])


def test_ev_analysis_does_not_mutate_original_active_profile():
    case = build_case(with_ev=True)
    original_active_profile = case.active_power_profile.copy()

    run_ev_penetration_analysis(
        case,
        penetration_level=1.0,
        random_seed=0,
    )

    pd.testing.assert_frame_equal(
        case.active_power_profile,
        original_active_profile,
    )
