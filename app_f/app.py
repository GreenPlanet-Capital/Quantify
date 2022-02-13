import os, sys
sys.path.append(os.getcwd())
from DataManager.utils.timehandler import TimeHandler
from typing import List
from datetime import datetime
from constants.datamanager_settings import setup_datamgr_settings
from constants.strategy_defs import get_strategy_definitons
from positions.opportunity import Opportunity

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
def setup_data(start_timestamp: datetime, end_timestamp: datetime):

    global dict_of_dfs
    global list_of_final_symbols

    # Now import DataManager
    from DataManager.datamgr import data_manager
    this_manager = data_manager.DataManager(limit=10, update_before=False, exchangeName = 'NYSE', isDelisted=False)
    start_timestamp = TimeHandler.get_string_from_datetime(start_timestamp)
    end_timestamp = TimeHandler.get_string_from_datetime(end_timestamp)
    dict_of_dfs = this_manager.get_stock_data(start_timestamp, 
                                            end_timestamp,
                                            api='Alpaca')
    list_of_final_symbols = this_manager.list_of_symbols

def main():
    setup_data(start_timestamp='2021-06-01 00:00:00', end_timestamp='2021-12-08 00:00:00')
    print("Running Strategies:\n")
    strat: BaseStrategy = strat_id_to_class[0]
    strat.set_data(list_of_tickers=list_of_final_symbols, dict_of_dataframes=dict_of_dfs)
    opps: List[Opportunity] = strat.run()
    print()

if __name__ == '__main__':
    main()