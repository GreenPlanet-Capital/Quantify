import os, sys
from re import L
sys.path.append(os.getcwd())

import inspect

from strats.base_strategy import BaseStrategy
from strats.macd_rsi import Macd_Rsi

strat_name_to_id = dict()
strat_id_to_class = dict()

def setup_strategies():
    global strat_name_to_id
    global strat_id_to_class

    strat_name_to_id = {
    "MACD_RSI": 0
    }
    class Strategies:
        def macd_rsi(self):
            return Macd_Rsi()

    assert len(strat_name_to_id) == \
        len(inspect.getmembers(Strategies, inspect.isfunction)), "Lengths Mismatch: Add a strategy to both strat_name_to_id and the Strategies class"
    
    strats = Strategies()

    strat_id_to_class = { 
        id: getattr(strats, name.lower())()
        for name, id in strat_name_to_id.items()
    }

dict_of_dfs = dict()
list_of_final_symbols = []

def setup_data():

    global dict_of_dfs
    global list_of_final_symbols

    sys.path.append('DataManager') # Insert DataManager to path

    # Set env variable to absolute path of datamanager folder
    os.environ['DATAMGR_ABS_PATH'] = '/Users/atharvakale/scripts/RobinhoodPartner/DataManager'

    # Now import DataManager
    from DataManager.datamgr import data_manager
    this_manager = data_manager.DataManager(limit=10, update_before=False, exchangeName = 'NYSE', isDelisted=False)
    dict_of_dfs = this_manager.get_stock_data('2019-05-01 00:00:00', 
                                            '2019-06-01 00:00:00',
                                            api='Alpaca')
    list_of_final_symbols = this_manager.list_of_symbols
    print()

def main():
    setup_strategies()
    setup_data()
    strat: BaseStrategy = strat_id_to_class[strat_name_to_id['MACD_RSI']]
    strat.set_data(list_of_tickers=list_of_final_symbols, dict_of_dataframes=dict_of_dfs)
    strat.run()
    print()

if __name__ == '__main__':
    main()