from datetime import datetime
import numpy as np
import pandas as pd
from Quantify.app_f.data_retrieval import get_data
from Quantify.tools.base_tester import BaseTester
from Quantify.constants.strategy_defs import get_strategy_definitons
from Quantify.strats.base_strategy import BaseStrategy
from Quantify.tools.live_tester import LiveTester
from Quantify.tools.forward_tester import ForwardTester
from Quantify.tools.portfolio_monitor import PortfolioMonitor
from Quantify.integrations.robinhood import RobinhoodIntegration
from Quantify.integrations.base import BaseIntegration


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
    start_timestamp = datetime(2024, 1, 1)
    end_timestamp = datetime(2024, 7, 31)

    limit = None
    update_before = False

    n_best = 5
    percent_l = 1

    strat_id = 1  # Set strategy here
    strat: BaseStrategy = strat_id_to_class[strat_id]
    integration: BaseIntegration = RobinhoodIntegration(strat_id)

    positions = integration.get_open_positions()

    specific_stocks = [pos.ticker for pos in positions]
    start_timestamp = min([pos.timestamp for pos in positions])

    list_of_final_symbols, dict_of_dfs = get_data(
        start_timestamp,
        end_timestamp,
        limit,
        exchangeName,
        update_before,
        list_specific_stocks=specific_stocks,
        fetch_data=False,
        ensure_full_data=False,
    )

    if len(list_of_final_symbols) == 0:
        print("Cancelling test...\n")
        print("No dataframes were found for the given dates")
        return

    # tester_f: BaseTester = ForwardTester(
    #     list_of_final_symbols, dict_of_dfs, exchangeName, strat, n_best, percent_l
    # )
    # tester_f.execute_strat(
    #     graph_positions=False, print_terminal=False, amount_per_pos=100
    # )

    # tester_l: BaseTester = LiveTester(
    #     list_of_final_symbols, dict_of_dfs, exchangeName, strat, n_best, percent_l
    # )
    # tester_l.execute_strat(print_terminal=True)]

    port_mon = PortfolioMonitor(dict_of_dfs, strat, exchangeName)
    port_mon.monitor_health(print_debug=True, graph=False)

    print()


if __name__ == "__main__":
    main()
