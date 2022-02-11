import os, sys
sys.path.append(os.getcwd())

sys.path.append('DataManager') # Insert DataManager to path

# Set env variable to absolute path of datamanager folder
os.environ['DATAMGR_ABS_PATH'] = '/Users/atharvakale/scripts/RobinhoodPartner/DataManager'

# Now import DataManager
from DataManager.datamgr import data_manager
this_manager = data_manager.DataManager(limit=10, update_before=False, exchangeName = 'NYSE', isDelisted=False)
dict_of_dfs = this_manager.get_stock_data('2018-06-01 00:00:00', 
                                          '2019-06-01 00:00:00',
                                          api='Alpaca')
list_of_final_symbols = this_manager.list_of_symbols
print()