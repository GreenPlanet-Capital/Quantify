from typing import List
from DataManager.utils.timehandler import TimeHandler
import pandas as pd

from positions.position import Position
from strats.base_strategy import BaseStrategy


def forward_tester(list_of_final_symbols, dict_of_dfs, strat: BaseStrategy):
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
            if not score_df.empty and score_df['exit_signal'].iloc[-1] and this_pos.is_active:
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
        to_graph = pd.concat([dict_of_dfs[ticker][['close', 'timestamp']][min_start_index - 1:], score_df[['Score']]],
                             axis=1)

        list_dates = [this_pos.timestamp, this_pos.exit_timestamp]
        list_dates = list(map(TimeHandler.get_string_from_datetime, list_dates))

        fig = to_graph.plot(x='timestamp', y=[to_graph['Score'] * 10 + to_graph['close'].mean(), to_graph['close']],
                            title=f"Stock Ticker: {ticker}")

        def find_loc(df, dates):
            marks = []
            for date in dates:
                marks.append(df.index[df['timestamp'] == date])
            return marks
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