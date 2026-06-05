"""Tests for the Assignment 3 input-data validity checks."""

import pandas as pd
import pytest
from grid_fixtures import build_case, build_ev_profiles
from power_grid_model import ComponentType, DatasetType, initialize_array

from power_system_simulation.graph_processing import (
    GraphCycleError,
    GraphNotFullyConnectedError,
)
from power_system_simulation.validation import (
    InvalidEVProfileError,
    InvalidFeederError,
    InvalidProfileError,
    InvalidSourceError,
    InvalidTransformerError,
    validate_case,
)


def test_validate_case_accepts_valid_grid():
    validate_case(build_case())


def test_validate_case_accepts_valid_grid_with_ev():
    validate_case(build_case(with_ev=True))


def test_two_sources_raise():
    case = build_case()
    source = initialize_array(DatasetType.input, ComponentType.source, 2)
    source["id"] = [10, 11]
    source["node"] = [1, 1]
    source["status"] = [1, 1]
    source["u_ref"] = [1.0, 1.0]
    case.input_data[ComponentType.source] = source

    with pytest.raises(InvalidSourceError):
        validate_case(case)


def test_missing_transformer_raises():
    case = build_case()
    del case.input_data[ComponentType.transformer]

    with pytest.raises(InvalidTransformerError):
        validate_case(case)


def test_invalid_feeder_id_raises():
    case = build_case()
    case.lv_feeder_ids = [30, 999]

    with pytest.raises(InvalidFeederError):
        validate_case(case)


def test_feeder_not_starting_at_transformer_node_raises():
    case = build_case()
    case.lv_feeder_ids = [30, 32]  # line 32 starts at node 3, not the transformer node

    with pytest.raises(InvalidFeederError):
        validate_case(case)


def test_not_fully_connected_raises():
    case = build_case()
    case.input_data[ComponentType.line]["to_status"] = [1, 0, 0]  # node 4 has no path left

    with pytest.raises(GraphNotFullyConnectedError):
        validate_case(case)


def test_cycle_in_base_state_raises():
    case = build_case()
    case.input_data[ComponentType.line]["to_status"] = [1, 1, 1]  # close the ring

    with pytest.raises(GraphCycleError):
        validate_case(case)


def test_load_profile_timestamp_mismatch_raises():
    case = build_case()
    case.reactive_power_profile.index = pd.to_datetime(["2025-01-01 00:00", "2025-01-01 01:00", "2025-01-01 02:00"])

    with pytest.raises(InvalidProfileError):
        validate_case(case)


def test_load_profile_id_mismatch_raises():
    case = build_case()
    case.reactive_power_profile.columns = [40, 99]

    with pytest.raises(InvalidProfileError):
        validate_case(case)


def test_load_profile_invalid_sym_load_id_raises():
    case = build_case()
    case.active_power_profile.columns = [40, 99]
    case.reactive_power_profile.columns = [40, 99]

    with pytest.raises(InvalidProfileError):
        validate_case(case)


def test_ev_profile_timestamp_mismatch_raises():
    case = build_case(with_ev=True)
    case.ev_active_power_profiles.index = pd.to_datetime(["2025-01-01 00:00", "2025-01-01 01:00", "2025-01-01 02:00"])

    with pytest.raises(InvalidEVProfileError):
        validate_case(case)


def test_too_few_ev_profiles_raises():
    case = build_case()
    case.ev_active_power_profiles = build_ev_profiles(n_profiles=1)

    with pytest.raises(InvalidEVProfileError):
        validate_case(case)
