from datetime import datetime
from DataManager.datamgr import data_manager
from DataManager.utils.timehandler import TimeHandler

start_timestamp = datetime(2021, 7, 6)
end_timestamp = datetime(2022, 7, 20)
exchangeName = "NASDAQ"
limit = 5
update_before = False
n_best = 5
percent_l = 0.5


def get_data():
    return setup_data(
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
        limit=limit,
        exchangeName=exchangeName,
        update_before=update_before,
    )


def setup_data(
    start_timestamp: datetime,
    end_timestamp: datetime,
    limit,
    exchangeName,
    update_before,
):

    this_manager = data_manager.DataManager(
        limit=limit, update_before=update_before, exchangeName=exchangeName
    )

    start_timestamp = TimeHandler.get_string_from_datetime(start_timestamp)
    end_timestamp = TimeHandler.get_string_from_datetime(end_timestamp)
    dict_of_dfs = this_manager.get_stock_data(
        start_timestamp, end_timestamp, api="Alpaca"
    )
    list_of_final_symbols = this_manager.list_of_symbols
    return list_of_final_symbols, dict_of_dfs
