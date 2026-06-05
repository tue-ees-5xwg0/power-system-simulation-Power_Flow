"""Data container for Assignment 3 input data."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from power_system_simulation.power_flow_processing import read_load_profile, read_pgm_json


@dataclass
class PowerSystemCase:
    """Container for LV grid input data and associated profiles."""

    input_data: dict
    active_power_profile: pd.DataFrame
    reactive_power_profile: pd.DataFrame
    lv_feeder_ids: list[int]
    ev_active_power_profiles: pd.DataFrame | None = None

    @classmethod
    def from_files(
        cls,
        input_data_path: str | Path,
        active_power_profile_path: str | Path,
        reactive_power_profile_path: str | Path,
        meta_data_path: str | Path,
        ev_active_power_profile_path: str | Path | None = None,
    ) -> PowerSystemCase:
        """Create a case from PGM JSON, parquet profiles, and metadata."""
        input_data = read_pgm_json(input_data_path)
        active_power_profile = read_load_profile(active_power_profile_path)
        reactive_power_profile = read_load_profile(reactive_power_profile_path)

        meta_data = pd.read_json(meta_data_path, typ="series")
        lv_feeder_ids = list(meta_data["lv_feeders"])

        ev_profiles = None
        if ev_active_power_profile_path is not None:
            ev_profiles = read_load_profile(ev_active_power_profile_path)

        return cls(
            input_data=input_data,
            active_power_profile=active_power_profile,
            reactive_power_profile=reactive_power_profile,
            lv_feeder_ids=lv_feeder_ids,
            ev_active_power_profiles=ev_profiles,
        )
