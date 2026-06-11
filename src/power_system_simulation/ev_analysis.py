import math

import numpy as np
import pandas as pd
from power_grid_model import ComponentType

from power_system_simulation.case import PowerSystemCase
from power_system_simulation.grid_graph import build_graph_processor
from power_system_simulation.power_flow_processing import PowerFlowProcessor
from power_system_simulation.validation import validate_case


# Helper function to determine feeder membership
# Uses graph functionalities from Assignment 1 (find downstream vertices)
def _houses_per_feeder(case: PowerSystemCase) -> dict[int, list[int]]:
    """Map each feeder line ID to the list of sym_load IDs in that feeder."""
    graph = build_graph_processor(case.input_data)
    sym_load = case.input_data[ComponentType.sym_load]
    feeder_to_houses: dict[int, list[int]] = {}
    for feeder_id in case.lv_feeder_ids:
        downstream_nodes = set(graph.find_downstream_vertices(feeder_id))
        houses = [
            int(load_id)
            for load_id, node in zip(
                sym_load["id"],
                sym_load["node"],
                strict=True,
            )
            if int(node) in downstream_nodes
        ]
        feeder_to_houses[int(feeder_id)] = houses
    return feeder_to_houses


def run_ev_penetration_analysis(
    case: PowerSystemCase,
    penetration_level: float,
    random_seed: int | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    /* General */
    Assign EV charging profiles (randomly) to households and then run a time-series
    power flow calculation.

    Should use Assignment 1 graph functionality to determine feeder membership
    and Assignment 2 power flow functionality to run the calcs on the grid.

    /* Arguments */:
        case: The LV grid and its load/EV profile data.
        penetration_level: Fraction in [0, 1] of houses that should get an EV.
        random_seed: Seed for reproducible selection. Pass a fixed value in
            tests so the same houses and profiles are chosen every run; pass
            None for true randomness in normal use.

    Returns:
        (voltage_summary, line_summary): the two Assignment 2 aggregation
        tables computed on the grid after EVs are added.

    Note:
        Design decision: if a feeder has fewer
        houses than the per-feeder EV target, the target is clamped to the
        number of available houses rather than raising it.
    """
    validate_case(case)

    if not 0 <= penetration_level <= 1:
        raise ValueError("penetration_level must be between 0 and 1.")

    if case.ev_active_power_profiles is None:
        raise ValueError("EV penetration analysis requires ev_active_power_profiles.")

    # Just double checking for valid input
    if case.ev_active_power_profiles is None:  # ← guard first
        raise ValueError("EV penetration analysis requires ev_active_power_profiles.")

    # Random number generation, fixed seed reproduces the entire run (house selection AND profile assignment)
    rng = np.random.default_rng(random_seed)

    # Which houses belong to which feeder (assignment 1) - use helper function to determine membership
    feeder_to_houses = _houses_per_feeder(case)

    # Find how many EVs per feeder (round_down of the spec formula)
    n_houses = len(case.input_data[ComponentType.sym_load])
    n_feeders = len(case.lv_feeder_ids)
    evs_per_feeder = math.floor(penetration_level * n_houses / n_feeders)

    # Within each feeder, randomly pick that many houses
    # replace=False: no house picked twice within a feeder.
    # min(...) clamp: if the feeder has fewer houses than the target,
    # take all of them instead of letting rng.choice crash.
    selected_houses: list[int] = []
    for houses in feeder_to_houses.values():
        k = min(evs_per_feeder, len(houses))  # clamp if feeder is small
        chosen = rng.choice(houses, size=k, replace=False)
        selected_houses.extend(int(h) for h in chosen)

    if not selected_houses:
        processor = PowerFlowProcessor(
            case.input_data,
            case.active_power_profile,
            case.reactive_power_profile,
        )
        processor.run_time_series()
        return processor.get_voltage_summary(), processor.get_line_summary()

    # Assign a unique EV profile to each selected house
    ev_pool = case.ev_active_power_profiles
    profile_columns = rng.choice(ev_pool.columns, size=len(selected_houses), replace=False)

    # Add each EV's active power onto its house. Working on a copy so the
    # original data is never mutated. Reactive power is left untouched
    # because EV reactive power is zero per the spec.
    modified_active = case.active_power_profile.copy()
    for house_id, profile_col in zip(
        selected_houses,
        profile_columns,
        strict=True,
    ):
        modified_active[house_id] += ev_pool[profile_col].to_numpy()

    # Run the time-series power flow (assignment 2) and return the
    # two aggregation tables.
    processor = PowerFlowProcessor(case.input_data, modified_active, case.reactive_power_profile)
    processor.run_time_series()
    return processor.get_voltage_summary(), processor.get_line_summary()
