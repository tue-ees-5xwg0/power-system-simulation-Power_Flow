"""Small valid test grid: 1 source, 1 transformer, 2 feeders.

    node_2 - line_30 - node_3 (sym_load_40)
    node_2 - line_31 - node_4 (sym_load_41)
    node_3 - line_32 - node_4   (open, so the base grid is a tree)

Feeder line IDs are [30, 31].
"""

import numpy as np
import pandas as pd
from power_grid_model import ComponentType, DatasetType, initialize_array

from power_system_simulation.case import PowerSystemCase

LOAD_IDS = [40, 41]
FEEDER_IDS = [30, 31]
TIMESTAMPS = pd.to_datetime(
    [
        "2024-01-01 00:00",
        "2024-01-01 01:00",
        "2024-01-01 02:00",
    ]
)


def build_input_data() -> dict:
    """Return a fresh, PGM-valid input-data dict for the example grid."""
    node = initialize_array(DatasetType.input, ComponentType.node, 4)
    node["id"] = [1, 2, 3, 4]
    node["u_rated"] = [10_500.0, 400.0, 400.0, 400.0]

    source = initialize_array(DatasetType.input, ComponentType.source, 1)
    source["id"] = [10]
    source["node"] = [1]
    source["status"] = [1]
    source["u_ref"] = [1.0]

    transformer = initialize_array(DatasetType.input, ComponentType.transformer, 1)
    transformer["id"] = [20]
    transformer["from_node"] = [1]
    transformer["to_node"] = [2]
    transformer["from_status"] = [1]
    transformer["to_status"] = [1]
    transformer["u1"] = [10_500.0]
    transformer["u2"] = [400.0]
    transformer["sn"] = [500_000.0]
    transformer["uk"] = [0.04]
    transformer["pk"] = [5_000.0]
    transformer["i0"] = [0.01]
    transformer["p0"] = [500.0]
    transformer["winding_from"] = [2]
    transformer["winding_to"] = [1]
    transformer["clock"] = [5]
    transformer["tap_side"] = [0]
    transformer["tap_pos"] = [0]
    transformer["tap_min"] = [-5]
    transformer["tap_max"] = [5]
    transformer["tap_nom"] = [0]
    transformer["tap_size"] = [250.0]

    line = initialize_array(DatasetType.input, ComponentType.line, 3)
    line["id"] = [30, 31, 32]
    line["from_node"] = [2, 2, 3]
    line["to_node"] = [3, 4, 4]
    line["from_status"] = [1, 1, 1]
    line["to_status"] = [1, 1, 0]  # line 32 open -> tree base state
    line["r1"] = [0.1, 0.1, 0.1]
    line["x1"] = [0.05, 0.05, 0.05]
    line["c1"] = [1e-7, 1e-7, 1e-7]
    line["tan1"] = [0.0, 0.0, 0.0]
    line["i_n"] = [200.0, 200.0, 200.0]

    sym_load = initialize_array(DatasetType.input, ComponentType.sym_load, 2)
    sym_load["id"] = LOAD_IDS
    sym_load["node"] = [3, 4]
    sym_load["status"] = [1, 1]
    sym_load["type"] = [0]
    sym_load["p_specified"] = [1000.0, 1000.0]
    sym_load["q_specified"] = [0.0, 0.0]

    return {
        ComponentType.node: node,
        ComponentType.source: source,
        ComponentType.transformer: transformer,
        ComponentType.line: line,
        ComponentType.sym_load: sym_load,
    }


def build_active_profile() -> pd.DataFrame:
    """Active-power profile (W) for every sym_load over the test period."""
    return pd.DataFrame(
        [[1000.0, 1200.0], [1500.0, 1300.0], [800.0, 1100.0]],
        index=TIMESTAMPS,
        columns=LOAD_IDS,
    )


def build_reactive_profile() -> pd.DataFrame:
    """Reactive-power profile (var) matching the active profile shape."""
    return pd.DataFrame(
        np.zeros((len(TIMESTAMPS), len(LOAD_IDS))),
        index=TIMESTAMPS,
        columns=LOAD_IDS,
    )


def build_ev_profiles(n_profiles: int = 5) -> pd.DataFrame:
    """Pool of EV active-power profiles keyed by sequence number (0..n-1)."""
    rng = np.random.default_rng(0)
    return pd.DataFrame(
        rng.uniform(0.0, 500.0, size=(len(TIMESTAMPS), n_profiles)),
        index=TIMESTAMPS,
        columns=list(range(n_profiles)),
    )


def build_case(with_ev: bool = False) -> PowerSystemCase:
    """Assemble a valid PowerSystemCase for the example grid."""
    return PowerSystemCase(
        input_data=build_input_data(),
        active_power_profile=build_active_profile(),
        reactive_power_profile=build_reactive_profile(),
        lv_feeder_ids=list(FEEDER_IDS),
        ev_active_power_profiles=build_ev_profiles() if with_ev else None,
    )
