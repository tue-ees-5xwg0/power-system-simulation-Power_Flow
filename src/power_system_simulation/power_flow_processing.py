"""Power grid calculation module using power-grid-model."""


from power_grid_model import (
    CalculationMethod,
    CalculationType,
    ComponentType,
    DatasetType,
    PowerGridModel,
    initialize_array,
)
from power_grid_model.validation import (
    assert_valid_batch_data,
    assert_valid_input_data,
)

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
        assert_valid_input_data(input_data=pgm_input_data, calculation_type=CalculationType.power_flow)

        # Second, raise error in case of not matching timestamps and/or load IDs
        if not active_power_profile.index.equals(reactive_power_profile.index):
            raise LoadProfilesMismatchError("Active and reactive profiles have different timestamps.")
        if not active_power_profile.columns.equals(reactive_power_profile.columns):
            raise LoadProfilesMismatchError("Active and reactive profiles have different load IDs.")

        # Store input on self so other methods can access them later
        self.pgm_input_data = pgm_input_data
        self.active_power_profile = active_power_profile
        self.reactive_power_profile = reactive_power_profile

        # Construct PGM using the input data according to power-grid-model API
        self.pgm_model = PowerGridModel(input_data=pgm_input_data)

        # Create PGM batch update dataset with the active & reactive load profiles
        shape = (
            self.active_power_profile.shape
        )  # gives a tuple of (number of rows, number of columns), needed to init array later
        load_profile = initialize_array(
            DatasetType.update, ComponentType.sym_load, shape
        )  # used to allocate empty batch array

        load_profile["id"] = self.active_power_profile.columns.to_numpy()
        load_profile["p_specified"] = self.active_power_profile.to_numpy()
        load_profile["q_specified"] = self.reactive_power_profile.to_numpy()

        self.update_pgm_data = {ComponentType.sym_load: load_profile}

    def run_time_series(
        self,
        calculation_method=CalculationMethod.newton_raphson,  # from workshop we saw it gives correct results
    ):
        # First, validate input batch data using the power-grid-model API
        # assert_valid_batch_data raises ValidationException error
        assert_valid_batch_data(
            input_data=self.pgm_input_data, update_data=self.update_pgm_data, calculation_method=calculation_method
        )
        # Running the batch (time series) power flow calculation
        self.output_data = self.gpm_model.calculate_power_flow(
            update_data=self.update_pgm_data, calculation_method=calculation_method
        )
        return self.output_data
