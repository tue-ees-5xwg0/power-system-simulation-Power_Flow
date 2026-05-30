"""Power grid mcalculation module using power-grid-model."""

from .graph_processing import GraphProcessor
from .power_flow_processing import PowerFlowProcessor

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

def __init__(
        self, 
        pgm_input_data, 
        active_power_profile, 
        reactive_power_profile
):
        # First, validate input data using the power-grid-model API
        # assert_valid_input_data raises ValidationException error 
        assert_valid_input_data(input_data = pgm_input_data, calculation_type = CalculationType.power_flow)

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
        self.PGM_model = PowerGridModel(pgm_input_data)
