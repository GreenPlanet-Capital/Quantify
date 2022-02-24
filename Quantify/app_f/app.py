import os
import numpy as np
import pandas as pd
pd.options.plotting.backend = "plotly"
from Quantify.tools.forward_tester import ForwardTester
from Quantify.tools.live_tester import LiveTester
from Quantify.tools.base_tester import BaseTester
from DataManager.utils.timehandler import TimeHandler
from DataManager.datamgr import data_manager
from datetime import datetime
from Quantify.constants.strategy_defs import get_strategy_definitons
from Quantify.strats.base_strategy import BaseStrategy

np.seterr(invalid='raise')

strat_id_to_name = dict()
strat_name_to_id = dict()
strat_id_to_class = dict()
strat_id_to_TimeFrame = dict()


def setup_strategies():
    global strat_id_to_name
    global strat_name_to_id
    global strat_id_to_class
    global strat_id_to_TimeFrame

    strat_id_to_name, strat_id_to_class, strat_id_to_TimeFrame = get_strategy_definitons()
    strat_name_to_id = {v: k for k, v in strat_id_to_name.items()}


setup_strategies()

dict_of_dfs = dict()
list_of_final_symbols = []

def setup_data(start_timestamp: datetime, end_timestamp: datetime, limit, exchangeName, update_before):
    global dict_of_dfs
    global list_of_final_symbols
    this_manager = data_manager.DataManager(limit=limit, update_before=update_before, exchangeName=exchangeName)
    
    start_timestamp = TimeHandler.get_string_from_datetime(start_timestamp)
    end_timestamp = TimeHandler.get_string_from_datetime(end_timestamp)
    dict_of_dfs = this_manager.get_stock_data(start_timestamp,
                                              end_timestamp,
                                              api='Alpaca',
                                              fill_data=5)
    list_of_final_symbols = this_manager.list_of_symbols
    return list_of_final_symbols, dict_of_dfs


def main():
    # Fetch data for entire test frame & manage slices
    start_timestamp = datetime(2021, 7, 6)
    end_timestamp = datetime(2022, 2, 22)
    exchangeName = 'NYSE'
    limit = None
    update_before = False
    n_best = 30
    percent_l=0.5

    setup_data(start_timestamp=start_timestamp, end_timestamp=end_timestamp,
               limit=limit, exchangeName=exchangeName, update_before=update_before)

    if len(list_of_final_symbols) == 0:
            print(f'Cancelling test...\n')
            print('No dataframes were found for the given dates')
            return

    strat: BaseStrategy = strat_id_to_class[1]  # Set strategy here

    tester_f: BaseTester = ForwardTester(
                        list_of_final_symbols, 
                        dict_of_dfs, 
                        exchangeName, 
                        strat, 
                        n_best,
                        percent_l=percent_l
                    )
    tester_f.execute_strat(graph_positions=True, print_terminal=True)

    # tester_l: BaseTester = LiveTester(list_of_final_symbols, dict_of_dfs, exchangeName, strat, n_best)
    # tester_l.execute_strat(print_terminal=True)

    print()


if __name__ == '__main__':
    main()
