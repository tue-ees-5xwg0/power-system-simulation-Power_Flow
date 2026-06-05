from power_system_simulation.case import PowerSystemCase


def run_n_minus_one_analysis(
    case: PowerSystemCase,
    disconnected_line_id: int,
):
    """
    Runs N-1 contingency analysis for a given line.

    Should use Assignment 1 graph functionality to identify alternative
    restoration lines and Assignment 2 power flow functionality to
    evaluate each alternative topology.

    Should return:
    pd.DataFrame
        Summary table containing the results for all alternative
        topologies.
    """
    raise NotImplementedError
