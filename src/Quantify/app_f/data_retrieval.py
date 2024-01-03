from datetime import datetime
from DataManager.datamgr import data_manager
from DataManager.utils.timehandler import TimeHandler


def get_specific_data(list_specific_stocks=None, fetch_data=True):
    start_timestamp = datetime(2022, 8, 1)
    end_timestamp = datetime(2023, 5, 5)
    exchangeName = "NASDAQ"
    limit = None
    update_before = False

    return get_data(
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
        limit=limit,
        exchangeName=exchangeName,
        update_before=update_before,
        list_specific_stocks=list_specific_stocks,
        fetch_data=fetch_data,
    )


def get_data(
    start_timestamp: datetime,
    end_timestamp: datetime,
    limit,
    exchangeName,
    update_before,
    list_specific_stocks=None,
    fetch_data=True,
):
    this_manager = data_manager.DataManager(
        limit=limit, update_before=update_before, exchangeName=exchangeName
    )

    dict_of_dfs = dict()
    start_dt, end_dt = map(
        TimeHandler.get_string_from_datetime, [start_timestamp, end_timestamp]
    )

    if list_specific_stocks is None:
        dict_of_dfs = this_manager.get_stock_data(
            start_dt, end_dt, api="Alpaca", fetch_data=fetch_data
        )
    else:
        for stock in list_specific_stocks:
            start_dt, end_dt, _ = this_manager.validate_timestamps(start_dt, end_dt)
            dict_of_dfs[stock] = this_manager._daily_stocks.get_specific_stock_data(
                stock, start_dt, end_dt
            )

    list_of_final_symbols = list_specific_stocks or this_manager.list_of_symbols
    return list_of_final_symbols, dict_of_dfs
