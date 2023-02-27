import numpy as np
import pandas as pd
from Quantify.app_f.data_retrieval import get_specific_data
from Quantify.tools.base_tester import BaseTester
from Quantify.constants.strategy_defs import get_strategy_definitons
from Quantify.strats.base_strategy import BaseStrategy
from Quantify.tools.live_tester import LiveTester
from Quantify.tools.forward_tester import ForwardTester


pd.options.plotting.backend = "plotly"

np.seterr(invalid="raise")

strat_id_to_name = dict()
strat_name_to_id = dict()
strat_id_to_class = dict()
strat_id_to_TimeFrame = dict()


def setup_strategies():
    global strat_id_to_name
    global strat_name_to_id
    global strat_id_to_class
    global strat_id_to_TimeFrame

    (
        strat_id_to_name,
        strat_id_to_class,
        strat_id_to_TimeFrame,
    ) = get_strategy_definitons()
    strat_name_to_id = {v: k for k, v in strat_id_to_name.items()}


setup_strategies()


def main():
    # Fetch data for entire test frame & manage slices
    exchangeName = "NASDAQ"
    n_best = 5
    percent_l = 0.5

    list_of_final_symbols, dict_of_dfs = get_specific_data(fetch_data=True)

    if len(list_of_final_symbols) == 0:
        print("Cancelling test...\n")
        print("No dataframes were found for the given dates")
        return

    strat: BaseStrategy = strat_id_to_class[1]  # Set strategy here

    # tester_f: BaseTester = ForwardTester(
    #     list_of_final_symbols,
    #     dict_of_dfs,
    #     exchangeName,
    #     strat,
    #     n_best,
    #     percent_l
    # )
    # tester_f.execute_strat(graph_positions=True, print_terminal=True)

    tester_l: BaseTester = LiveTester(
        list_of_final_symbols, dict_of_dfs, exchangeName, strat, n_best, percent_l
    )
    tester_l.execute_strat(print_terminal=True)

    print()


if __name__ == "__main__":
    main()
