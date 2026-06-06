from power_system_simulation.case import PowerSystemCase


def run_ev_penetration_analysis(
    case: PowerSystemCase,
    penetration_level: float,
    random_seed: int | None = None,
):
    """
    Assign EV charging profiles to households and then run a time-series
    power flow calculation.

    Should use Assignment 1 graph functionality to determine feeder membership
    and Assignment 2 power flow functionality to run the calcs on the grid.

    Should return:
    tuple[pd.DataFrame, pd.DataFrame]
        Voltage summary and line summary tables.
    """
    raise NotImplementedError
