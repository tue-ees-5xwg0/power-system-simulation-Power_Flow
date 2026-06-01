"""Power grid calculation module using power-grid-model."""

from pathlib import Path

import numpy as np
import pandas as pd
from power_grid_model import (
    CalculationMethod,
    CalculationType,
    ComponentType,
    DatasetType,
    PowerGridModel,
    initialize_array,
)
from power_grid_model.utils import json_deserialize_from_file
from power_grid_model.validation import (
    assert_valid_batch_data,
    assert_valid_input_data,
)


def read_pgm_json(path):
    """Read a PGM JSON file into PGM input data."""
    return json_deserialize_from_file(Path(path))


def read_load_profile(path):
    """Read a load profile parquet file into a DataFrame."""
    return pd.read_parquet(path)


def validate_matching_profiles(active_power_profile, reactive_power_profile):
    """Validate that active and reactive profiles have matching timestamps and load IDs."""
    if not active_power_profile.index.equals(reactive_power_profile.index):
        raise LoadProfilesMismatchError("Active and reactive profiles have different timestamps.")

    if not active_power_profile.columns.equals(reactive_power_profile.columns):
        raise LoadProfilesMismatchError("Active and reactive profiles have different load IDs.")


def create_sym_load_update_data(active_power_profile, reactive_power_profile):
    """Create a PGM batch update dataset for sym_load profiles."""
    validate_matching_profiles(active_power_profile, reactive_power_profile)

    load_profile = initialize_array(
        DatasetType.update,
        ComponentType.sym_load,
        active_power_profile.shape,
    )

    load_profile["id"] = active_power_profile.columns.to_numpy()
    load_profile["p_specified"] = active_power_profile.to_numpy()
    load_profile["q_specified"] = reactive_power_profile.to_numpy()

    return {ComponentType.sym_load: load_profile}


# ValidationException error caught by power-grid-model api
# Raised when invalid input data and when the batch dataset is invalid


class LoadProfilesMismatchError(Exception):
    """Raised when the two profiles do not have matching timestamps and/or load IDs."""

    pass


class CalculationNotPerformedError(Exception):
    """Raised when aggregation is requested before run_time_series() has been called."""

    pass


class PowerFlowProcessor:
    def __init__(
        self,
        pgm_input_data,
        active_power_profile,
        reactive_power_profile,
    ):
        # First, validate input data using the power-grid-model API
        # assert_valid_input_data raises ValidationException error
        assert_valid_input_data(
            input_data=pgm_input_data,
            calculation_type=CalculationType.power_flow,
        )

        # Store input on self so other methods can access them later
        self.pgm_input_data = pgm_input_data
        self.active_power_profile = active_power_profile
        self.reactive_power_profile = reactive_power_profile

        # Construct PGM using the input data according to power-grid-model API
        self.pgm_model = PowerGridModel(input_data=pgm_input_data)

        self.update_pgm_data = create_sym_load_update_data(
            active_power_profile,
            reactive_power_profile,
        )
        self.output_data = None

    def run_time_series(
        self,
        calculation_method=CalculationMethod.newton_raphson,  # from workshop we saw it gives correct results
    ):
        # First, validate input batch data using the power-grid-model API
        # assert_valid_batch_data raises ValidationException error
        assert_valid_batch_data(
            input_data=self.pgm_input_data,
            update_data=self.update_pgm_data,
            calculation_type=CalculationType.power_flow,
        )
        # Running the batch (time series) power flow calculation
        self.output_data = self.pgm_model.calculate_power_flow(
            update_data=self.update_pgm_data,
            calculation_method=calculation_method,
        )
        return self.output_data

    def get_voltage_summary(self):
        """Aggregate node voltage results per timestamp."""
        if self.output_data is None:
            raise CalculationNotPerformedError("Run run_time_series() before aggregating results.")

        node_results = self.output_data[ComponentType.node]
        timestamps = self.active_power_profile.index
        node_ids = node_results["id"][0]
        voltages = node_results["u_pu"]

        max_indices = voltages.argmax(axis=1)
        min_indices = voltages.argmin(axis=1)

        return pd.DataFrame(
            {
                "Max_Voltage": voltages.max(axis=1),
                "Max_Voltage_Node": node_ids[max_indices],
                "Min_Voltage": voltages.min(axis=1),
                "Min_Voltage_Node": node_ids[min_indices],
            },
            index=timestamps,
        )

    def get_line_summary(self):
        """Aggregate line loading and energy loss results per line."""
        if self.output_data is None:
            raise CalculationNotPerformedError("Run run_time_series() before aggregating results.")

        line_results = self.output_data[ComponentType.line]
        timestamps = self.active_power_profile.index

        line_ids = line_results["id"][0]
        loading = line_results["loading"]

        power_loss_w = line_results["p_from"] + line_results["p_to"]
        power_loss_kw = power_loss_w / 1000.0

        elapsed_hours = (timestamps - timestamps[0]).total_seconds().to_numpy() / 3600.0

        time_steps = np.diff(elapsed_hours)
        average_loss_kw = 0.5 * (power_loss_kw[:-1] + power_loss_kw[1:])
        total_loss_kwh = np.sum(average_loss_kw * time_steps[:, None], axis=0)

        max_indices = loading.argmax(axis=0)
        min_indices = loading.argmin(axis=0)

        return pd.DataFrame(
            {
                "Total_Loss": total_loss_kwh,
                "Max_Loading": loading.max(axis=0),
                "Max_Loading_Timestamp": timestamps[max_indices],
                "Min_Loading": loading.min(axis=0),
                "Min_Loading_Timestamp": timestamps[min_indices],
            },
            index=pd.Index(line_ids, name="Line_ID"),
        )
