from typing import Literal

from power_system_simulation.case import PowerSystemCase


def optimize_tap_position(
    case: PowerSystemCase,
    criterion: Literal["loss", "voltage_deviation"] = "loss",
):
    """
    Find the optimal tap position from all available.

    Optimal tap should be selected based on either total energy loss or
    voltage deviation from 1.0 p.u. over the full simulation period (check assignment description).

    Should return:
    pd.DataFrame
        Summary of all evaluated tap positions and the optimal result.
    """
    raise NotImplementedError
