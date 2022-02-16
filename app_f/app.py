import os, sys

sys.path.append(os.getcwd())
import pandas as pd

pd.options.plotting.backend = "plotly"

from tools.forward_tester import ForwardTester
from tools.live_tester import LiveTester
from tools.base_tester import BaseTester
from DataManager.utils.timehandler import TimeHandler
from datetime import datetime
from constants.datamanager_settings import setup_datamgr_settings
from constants.strategy_defs import get_strategy_definitons

from strats.base_strategy import BaseStrategy

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

setup_datamgr_settings()


def setup_data(start_timestamp: datetime, end_timestamp: datetime, limit, exchangeName, update_before):
    global dict_of_dfs
    global list_of_final_symbols

    # Now import DataManager
    from DataManager.datamgr import data_manager
    this_manager = data_manager.DataManager(limit=limit, update_before=update_before, exchangeName=exchangeName,
                                            isDelisted=False)
    start_timestamp = TimeHandler.get_string_from_datetime(start_timestamp)
    end_timestamp = TimeHandler.get_string_from_datetime(end_timestamp)
    dict_of_dfs = this_manager.get_stock_data(start_timestamp,
                                              end_timestamp,
                                              api='Alpaca')
    list_of_final_symbols = this_manager.list_of_symbols
    return list_of_final_symbols, dict_of_dfs


def main():
    # Fetch data for entire test frame & manage slices
    start_timestamp = datetime(2021, 6, 1)
    end_timestamp = datetime(2021, 12, 27)
    exchangeName = 'NYSE'
    limit = 5
    update_before = False

    setup_data(start_timestamp=start_timestamp, end_timestamp=end_timestamp,
               limit=limit, exchangeName=exchangeName, update_before=update_before)

    strat: BaseStrategy = strat_id_to_class[1]  # Set strategy here

    tester_f: BaseTester = ForwardTester(list_of_final_symbols, dict_of_dfs, exchangeName, strat, 5)
    tester_f.execute_strat(graph_positions=True)

    # tester_l: BaseTester = LiveTester(list_of_final_symbols, dict_of_dfs, exchangeName, strat, 5)
    # tester_l.execute_strat()

    print()


if __name__ == '__main__':
    main()
