from datetime import datetime
from DataManager.datamgr import data_manager
from DataManager.utils.timehandler import TimeHandler


def get_data(
    start_timestamp: datetime,
    end_timestamp: datetime,
    limit,
    exchangeName,
    update_before,
    list_specific_stocks=None,
    fetch_data=True,
    ensure_full_data=True
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
            start_dt, end_dt, api="Alpaca", fetch_data=fetch_data, ensure_full_data=ensure_full_data
        )
    else:
        this_manager._basket_of_symbols = list_specific_stocks # Hack: fix later
        dict_of_dfs = this_manager.get_stock_data(
            start_dt, end_dt, api="Alpaca", fetch_data=fetch_data, ensure_full_data=ensure_full_data
        )

    list_of_final_symbols = this_manager.list_of_symbols
    return list_of_final_symbols, dict_of_dfs
