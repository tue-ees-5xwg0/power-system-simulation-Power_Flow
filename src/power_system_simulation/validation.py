"""Validation utilities for Assignment 3."""

from power_grid_model import CalculationType, ComponentType
from power_grid_model.validation import assert_valid_input_data

from power_system_simulation.case import PowerSystemCase
from power_system_simulation.grid_graph import build_graph_processor
from power_system_simulation.power_flow_processing import (
    validate_matching_profiles,
)


class InvalidSourceError(Exception):
    """Raised when the grid does not contain exactly one source."""

    pass


class InvalidTransformerError(Exception):
    """Raised when the grid does not contain exactly one transformer."""

    pass


class InvalidFeederError(Exception):
    """Raised when LV feeder IDs are invalid."""

    pass


class InvalidProfileError(Exception):
    """Raised when load profiles are invalid."""

    pass


class InvalidEVProfileError(Exception):
    """Raised when EV charging profiles are invalid."""

    pass


def validate_case(case: PowerSystemCase) -> None:
    """
    Validate all Assignment 3 input requirements that do not depend on
    Assignment 1 functionality.
    """
    _validate_pgm_input(case)
    _validate_source_and_transformer(case)
    _validate_feeder_ids(case)
    _validate_graph_topology(case)
    _validate_load_profiles(case)
    _validate_ev_profiles(case)


def _validate_pgm_input(case: PowerSystemCase) -> None:
    """Validate PGM input data using the Power Grid Model API."""
    assert_valid_input_data(
        input_data=case.input_data,
        calculation_type=CalculationType.power_flow,
    )


def _validate_source_and_transformer(case: PowerSystemCase) -> None:
    """Validate that the grid contains exactly one source and transformer."""
    if len(case.input_data.get(ComponentType.source, [])) != 1:
        raise InvalidSourceError("The grid must contain exactly one source.")

    if len(case.input_data.get(ComponentType.transformer, [])) != 1:
        raise InvalidTransformerError("The grid must contain exactly one transformer.")


def _validate_feeder_ids(case: PowerSystemCase) -> None:
    """
    Validate LV feeder IDs.

    Every feeder ID must:
        - be a valid line ID
        - start from the transformer LV node
    """
    lines = case.input_data.get(ComponentType.line, [])
    transformer = case.input_data[ComponentType.transformer][0]

    valid_line_ids = set(lines["id"]) if len(lines) else set()
    transformer_lv_node = transformer["to_node"]

    for feeder_id in case.lv_feeder_ids:
        if feeder_id not in valid_line_ids:
            raise InvalidFeederError(f"Feeder ID {feeder_id} is not a valid line ID.")

        feeder_line = lines[lines["id"] == feeder_id][0]

        if feeder_line["from_node"] != transformer_lv_node:
            raise InvalidFeederError(f"Feeder line {feeder_id} does not start at the transformer LV node.")


def _validate_graph_topology(case: PowerSystemCase) -> None:
    """Check the base grid is fully connected and has no cycles (Assignment 1)."""
    build_graph_processor(case.input_data)


def _validate_load_profiles(case: PowerSystemCase) -> None:
    """
    Validate active and reactive load profiles.

    Checks:
        - matching timestamps
        - matching sym_load IDs
        - profile IDs exist in the grid
    """
    try:
        validate_matching_profiles(
            case.active_power_profile,
            case.reactive_power_profile,
        )
    except Exception as exc:
        raise InvalidProfileError(str(exc)) from exc

    valid_load_ids = set(case.input_data[ComponentType.sym_load]["id"])

    profile_load_ids = set(case.active_power_profile.columns)

    if not profile_load_ids.issubset(valid_load_ids):
        raise InvalidProfileError("Load profile contains invalid sym_load IDs.")


def _validate_ev_profiles(case: PowerSystemCase) -> None:
    """
    Validate EV charging profiles.

    Checks:
        - timestamps match load profiles
        - enough EV profiles are available
    """
    if case.ev_active_power_profiles is None:
        return

    if not case.ev_active_power_profiles.index.equals(case.active_power_profile.index):
        raise InvalidEVProfileError("EV profile timestamps do not match load profile timestamps.")

    number_of_ev_profiles = case.ev_active_power_profiles.shape[1]

    number_of_loads = len(case.input_data[ComponentType.sym_load])

    if number_of_ev_profiles < number_of_loads:
        raise InvalidEVProfileError("The number of EV profiles must be at least the number of sym_loads.")
