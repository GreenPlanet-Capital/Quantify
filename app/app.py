import os, sys

from constants.strategy_defs import get_strategy_definitons
sys.path.append(os.getcwd())

from strats.base_strategy import BaseStrategy

strat_name_to_id = dict()
strat_id_to_class = dict()
strat_id_to_TimeFrame = dict()

def setup_strategies():
    global strat_name_to_id
    global strat_id_to_class
    global strat_id_to_TimeFrame

    strat_name_to_id, strat_id_to_class, strat_id_to_TimeFrame = get_strategy_definitons()

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