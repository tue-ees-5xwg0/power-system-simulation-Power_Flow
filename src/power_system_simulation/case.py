"""Data container for Assignment 3 input data."""

from dataclasses import dataclass

import pandas as pd


@dataclass
class PowerSystemCase:
    """
    Container for the LV grid and associated profile data.

    This class groups all Assignment 3 inputs into a single object
    that can be passed to the different analysis functions.
    """

    input_data: dict
    active_power_profile: pd.DataFrame
    reactive_power_profile: pd.DataFrame
    lv_feeder_ids: list[int]
    ev_active_power_profiles: pd.DataFrame | None = None
