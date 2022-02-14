import os, sys

import pandas as pd

pd.options.plotting.backend = "plotly"

sys.path.append(os.getcwd())
from DataManager.utils.timehandler import TimeHandler
from typing import List
from datetime import datetime
from constants.datamanager_settings import setup_datamgr_settings
from constants.strategy_defs import get_strategy_definitons
from positions.opportunity import Opportunity
from positions.position import Position

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
    this_manager = data_manager.DataManager(limit=7, update_before=False, exchangeName='NYSE', isDelisted=False)
    start_timestamp = TimeHandler.get_string_from_datetime(start_timestamp)
    end_timestamp = TimeHandler.get_string_from_datetime(end_timestamp)
    dict_of_dfs = this_manager.get_stock_data(start_timestamp,
                                              end_timestamp,
                                              api='Alpaca')
    list_of_final_symbols = this_manager.list_of_symbols


"""
# TODO: Forward Testing
Start with end timestamp, and increment
Enter x trades everyday given by strat at end time stamp
Health check for each previous trade done by the strategy (at the end time stamp + kth day)
    - go x days ahead & check health (Trailing score loss)
    - if returns 1, maintain position
    - if return -1, close position & add it to score of strat
Do this for n end timestamps
"""


def forward_tester():
    # Fetch data for entire test frame & manage slices
    setup_data(start_timestamp=datetime(2021, 6, 1), end_timestamp=datetime(2021, 12, 27))
    strat: BaseStrategy = strat_id_to_class[1]  # Set strategy here

    min_start_index = strat.timeframe.length
    num_top = 5

    strat.set_data(list_of_tickers=list_of_final_symbols,
                   dict_of_dataframes={k: v[:min_start_index] for k, v in dict_of_dfs.items()})
    positions: List[Position] = [Position(op) for op in strat.run()[:num_top]]

    print('-' * 50)
    print('Started Trading Period. Below are current positions')

    for pos in positions[:num_top]:
        print(pos)

    random_df_list = list(dict_of_dfs.values())[0]
    assert len(random_df_list) > min_start_index

    for i in range(min_start_index, len(random_df_list)):
        current_dict_dfs = {k: v[:i] for k, v in dict_of_dfs.items()}
        strat.set_data(list_of_tickers=list_of_final_symbols,
                       dict_of_dataframes=current_dict_dfs)

        dict_score_dfs = strat.multiple_health_check(positions)

        for ticker, tuple_df_pos in dict_score_dfs.items():
            score_df, this_pos = tuple_df_pos
            if score_df['exit_signal'].iloc[-1] and this_pos.is_active:
                this_pos.is_active = False
                current_df = current_dict_dfs[ticker].iloc[-1]
                exit_timestamp, exit_price = TimeHandler.get_datetime_from_string(current_df['timestamp']), \
                                             current_df['close']

                this_pos.exit_timestamp = exit_timestamp
                this_pos.exit_price = exit_price

    print('-' * 50)
    print('Ended Trading Period. Below are current positions')

    for pos in positions:
        if pos.is_active:
            pos.is_active = False
            current_df = current_dict_dfs[pos.ticker].iloc[-1]
            exit_timestamp, exit_price = TimeHandler.get_datetime_from_string(current_df['timestamp']), \
                                         current_df['close']

            pos.exit_timestamp = exit_timestamp
            pos.exit_price = exit_price

        print(pos)

    for ticker, tuple_df_pos in dict_score_dfs.items():
        score_df, this_pos = tuple_df_pos
        to_graph = pd.concat([score_df, dict_of_dfs[ticker][['close']][min_start_index - 1:]], axis=1)

        list_dates = [this_pos.timestamp, this_pos.exit_timestamp]
        list_dates = list(map(TimeHandler.get_string_from_datetime, list_dates))

        fig = to_graph.plot(x='timestamp', y=[to_graph['Score'] * 10 + to_graph['close'].mean(), to_graph['close']])
        list_locs = find_loc(to_graph, list_dates)

        fig.add_annotation(x=to_graph.loc[list_locs[0]]['timestamp'].iloc[0],
                           y=to_graph.loc[list_locs[0]]['close'].iloc[0],
                           text=f"Enter date (type: {this_pos.order_type})",
                           showarrow=True,
                           arrowhead=1)

        fig.add_annotation(x=to_graph.loc[list_locs[1]]['timestamp'].iloc[0],
                           y=to_graph.loc[list_locs[1]]['close'].iloc[0],
                           text=f"Exit date (type: {this_pos.order_type})",
                           showarrow=True,
                           arrowhead=1)

        fig.update_layout(showlegend=False)
        fig.show()


def find_loc(df, dates):
    marks = []
    for date in dates:
        marks.append(df.index[df['timestamp'] == date])
    return marks

def main():
    print("Running Forward Tester:\n")
    forward_tester()
    print()


if __name__ == '__main__':
    main()
