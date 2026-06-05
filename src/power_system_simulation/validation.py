"""Validation utilities for Assignment 3 input data."""

from power_grid_model import CalculationType, ComponentType
from power_grid_model.validation import assert_valid_input_data

from power_system_simulation.case import PowerSystemCase
from power_system_simulation.power_flow_processing import validate_matching_profiles


def validate_case(case: PowerSystemCase) -> None:
    """Validate all generic Assignment 3 input requirements."""
    assert_valid_input_data(
        input_data=case.input_data,
        calculation_type=CalculationType.power_flow,
    )

    _validate_single_source_and_transformer(case)
    _validate_feeder_ids(case)
    _validate_profiles(case)


def _validate_single_source_and_transformer(case: PowerSystemCase) -> None:
    if len(case.input_data[ComponentType.source]) != 1:
        raise ValueError("The grid must contain exactly one source.")

    if len(case.input_data[ComponentType.transformer]) != 1:
        raise ValueError("The grid must contain exactly one transformer.")


def _validate_feeder_ids(case: PowerSystemCase) -> None:
    lines = case.input_data[ComponentType.line]
    transformers = case.input_data[ComponentType.transformer]

    line_ids = set(lines["id"])
    transformer_to_node = transformers["to_node"][0]

    for feeder_id in case.lv_feeder_ids:
        if feeder_id not in line_ids:
            raise ValueError(f"Feeder ID {feeder_id} is not a valid line ID.")

        feeder = lines[lines["id"] == feeder_id][0]
        if feeder["from_node"] != transformer_to_node:
            raise ValueError(
                f"Feeder line {feeder_id} does not start at the transformer LV node."
            )


def _validate_profiles(case: PowerSystemCase) -> None:
    validate_matching_profiles(
        case.active_power_profile,
        case.reactive_power_profile,
    )

    sym_load_ids = set(case.input_data[ComponentType.sym_load]["id"])
    profile_ids = set(case.active_power_profile.columns)

    if not profile_ids.issubset(sym_load_ids):
        raise ValueError("Load profile columns must be valid sym_load IDs.")

    if case.ev_active_power_profiles is not None:
        if not case.ev_active_power_profiles.index.equals(case.active_power_profile.index):
            raise ValueError("EV profile timestamps must match load profile timestamps.")

        if case.ev_active_power_profiles.shape[1] < len(sym_load_ids):
            raise ValueError(
                "Number of EV profiles must be at least the number of sym_loads."
            )
