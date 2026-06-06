from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest
from power_grid_model import ComponentType

from power_system_simulation.power_flow_processing import (
    CalculationNotPerformedError,
    LoadProfilesMismatchError,
    PowerFlowProcessor,
    create_sym_load_update_data,
    validate_matching_profiles,
)


def test_validate_matching_profiles_raises_for_different_timestamps():
    active = pd.DataFrame(
        [[1.0, 2.0]],
        index=pd.to_datetime(["2024-01-01 00:00"]),
        columns=[8, 9],
    )
    reactive = pd.DataFrame(
        [[1.0, 2.0]],
        index=pd.to_datetime(["2024-01-01 01:00"]),
        columns=[8, 9],
    )

    with pytest.raises(LoadProfilesMismatchError):
        validate_matching_profiles(active, reactive)


def test_validate_matching_profiles_raises_for_different_load_ids():
    active = pd.DataFrame(
        [[1.0, 2.0]],
        index=pd.to_datetime(["2024-01-01 00:00"]),
        columns=[8, 9],
    )
    reactive = pd.DataFrame(
        [[1.0, 2.0]],
        index=pd.to_datetime(["2024-01-01 00:00"]),
        columns=[8, 10],
    )

    with pytest.raises(LoadProfilesMismatchError):
        validate_matching_profiles(active, reactive)


@patch("power_system_simulation.power_flow_processing.PowerGridModel")
@patch("power_system_simulation.power_flow_processing.assert_valid_input_data")
@patch("power_system_simulation.power_flow_processing.create_sym_load_update_data")
def test_get_voltage_summary_raises_before_calculation(
    mock_create_update_data,
    mock_assert_valid_input_data,
    mock_power_grid_model,
):
    active = pd.DataFrame(
        [[1.0]],
        index=pd.to_datetime(["2024-01-01 00:00"]),
        columns=[8],
    )
    reactive = active.copy()

    processor = PowerFlowProcessor({}, active, reactive)

    with pytest.raises(CalculationNotPerformedError):
        processor.get_voltage_summary()


@patch("power_system_simulation.power_flow_processing.PowerGridModel")
@patch("power_system_simulation.power_flow_processing.assert_valid_input_data")
@patch("power_system_simulation.power_flow_processing.create_sym_load_update_data")
def test_get_line_summary_raises_before_calculation(
    mock_create_update_data,
    mock_assert_valid_input_data,
    mock_power_grid_model,
):
    active = pd.DataFrame(
        [[1.0]],
        index=pd.to_datetime(["2024-01-01 00:00"]),
        columns=[8],
    )
    reactive = active.copy()

    processor = PowerFlowProcessor({}, active, reactive)

    with pytest.raises(CalculationNotPerformedError):
        processor.get_line_summary()


def test_create_sym_load_update_data():
    active = pd.DataFrame(
        [[100.0, 200.0], [300.0, 400.0]],
        index=pd.to_datetime(["2024-01-01 00:00", "2024-01-01 01:00"]),
        columns=[8, 9],
    )
    reactive = pd.DataFrame(
        [[10.0, 20.0], [30.0, 40.0]],
        index=active.index,
        columns=active.columns,
    )

    result = create_sym_load_update_data(active, reactive)
    load_update = result[ComponentType.sym_load]

    np.testing.assert_array_equal(load_update["id"], np.array([[8, 9], [8, 9]]))
    np.testing.assert_array_equal(load_update["p_specified"], active.to_numpy())
    np.testing.assert_array_equal(load_update["q_specified"], reactive.to_numpy())


def test_get_voltage_summary():
    active = pd.DataFrame(
        [[1.0], [2.0]],
        index=pd.to_datetime(["2024-01-01 00:00", "2024-01-01 01:00"]),
        columns=[8],
    )

    processor = PowerFlowProcessor.__new__(PowerFlowProcessor)
    processor.active_power_profile = active
    processor.output_data = {
        ComponentType.node: np.array(
            [
                [(1, 1.01), (2, 0.99), (3, 1.00)],
                [(1, 0.98), (2, 1.03), (3, 1.01)],
            ],
            dtype=[("id", "i4"), ("u_pu", "f8")],
        )
    }

    result = processor.get_voltage_summary()

    expected = pd.DataFrame(
        {
            "Max_Voltage": [1.01, 1.03],
            "Max_Voltage_Node": np.array([1, 2], dtype=np.int32),
            "Min_Voltage": [0.99, 0.98],
            "Min_Voltage_Node": np.array([2, 1], dtype=np.int32),
        },
        index=active.index,
    )

    pd.testing.assert_frame_equal(result, expected)


def test_get_line_summary():
    active = pd.DataFrame(
        [[1.0], [2.0], [3.0]],
        index=pd.to_datetime(
            [
                "2024-01-01 00:00",
                "2024-01-01 01:00",
                "2024-01-01 02:00",
            ]
        ),
        columns=[8],
    )

    processor = PowerFlowProcessor.__new__(PowerFlowProcessor)
    processor.active_power_profile = active
    processor.output_data = {
        ComponentType.line: np.array(
            [
                [(5, 0.2, 1000.0, 1000.0), (6, 0.5, 2000.0, 1000.0)],
                [(5, 0.4, 3000.0, 1000.0), (6, 0.3, 4000.0, 1000.0)],
                [(5, 0.1, 5000.0, 1000.0), (6, 0.7, 6000.0, 1000.0)],
            ],
            dtype=[
                ("id", "i4"),
                ("loading", "f8"),
                ("p_from", "f8"),
                ("p_to", "f8"),
            ],
        )
    }

    result = processor.get_line_summary()

    expected = pd.DataFrame(
        {
            "Total_Loss": [8.0, 10.0],
            "Max_Loading": [0.4, 0.7],
            "Max_Loading_Timestamp": pd.to_datetime(["2024-01-01 01:00", "2024-01-01 02:00"]),
            "Min_Loading": [0.1, 0.3],
            "Min_Loading_Timestamp": pd.to_datetime(["2024-01-01 02:00", "2024-01-01 01:00"]),
        },
        index=pd.Index(np.array([5, 6], dtype=np.int32), name="Line_ID"),
    )

    pd.testing.assert_frame_equal(result, expected)


@patch("power_system_simulation.power_flow_processing.assert_valid_batch_data")
def test_run_time_series(mock_assert_valid_batch_data):
    processor = PowerFlowProcessor.__new__(PowerFlowProcessor)

    processor.pgm_input_data = {"input": "data"}
    processor.update_pgm_data = {"update": "data"}
    processor.pgm_model = Mock()
    processor.pgm_model.calculate_power_flow.return_value = {"result": "data"}

    result = processor.run_time_series()

    mock_assert_valid_batch_data.assert_called_once()
    processor.pgm_model.calculate_power_flow.assert_called_once()
    assert result == {"result": "data"}
    assert processor.output_data == {"result": "data"}
