from typing import List, Dict, Tuple
from pandas import DataFrame
from DataManager.utils.timehandler import TimeHandler
import pandas as pd
from tqdm import tqdm
from Quantify.constants.utils import find_loc
from Quantify.monitors.trailing_monitor import TrailingMonitor
from Quantify.positions.position import Position
from Quantify.strats.base_strategy import BaseStrategy
from Quantify.tools.base_tester import BaseTester


class ForwardTester(BaseTester):
    def __init__(
        self,
        list_of_final_symbols: List[str],
        dict_of_dfs: Dict[str, DataFrame],
        exchangeName: str,
        strat: BaseStrategy,
        num_top: int,
        percent_l=0.7,
    ):
        super().__init__(
            list_of_final_symbols, dict_of_dfs, exchangeName, strat, num_top, percent_l
        )

    def execute_strat(
        self, graph_positions=False, print_terminal=False
    ) -> List[Position]:
        self.print_terminal = print_terminal
        min_start_index = self.strat.timeframe.length
        self.strat.set_data(
            list_of_tickers=self.list_of_final_symbols,
            dict_of_dataframes={
                k: v[:min_start_index] for k, v in self.dict_of_dfs.items()
            },
            exchangeName=self.exchangeName,
        )

        self.strat.instantiate_indicator_mgr()

        opps = self.strat.run()
        positions: List[Position] = [
            Position(op) for op in self.get_good_mix_of_opps(opps)
        ]

        if print_terminal:
            print("-" * 50)
            print("Started Trading Period. Below are current positions")

            for pos in positions:
                print(pos)

        min_df_len = min([len(df) for df in self.dict_of_dfs.values()])
        assert min_df_len >= min_start_index

        current_dict_dfs, dict_score_dfs = self.advance_forward(
            min_start_index, min_df_len, positions
        )

        if print_terminal:
            print("-" * 50)
            print("Ended Trading Period. Below are current positions")

        self.handle_remaining_positions(current_dict_dfs, positions)

        if graph_positions:
            self.graph_positions(dict_score_dfs, min_start_index)

        return positions

    def advance_forward(
        self, start_index, end_index, positions
    ) -> Tuple[Dict[str, DataFrame], Dict[str, DataFrame]]:
        current_dict_dfs, dict_score_dfs = self.dict_of_dfs, dict()
        self.strat.set_data(
            list_of_tickers=self.list_of_final_symbols,
            dict_of_dataframes=current_dict_dfs,
            exchangeName=self.exchangeName,
        )
        health_monitor = TrailingMonitor(
            self.strat.sid, "Trailing Health Check", self.strat
        )
        dict_score_dfs = health_monitor.multiple_health_check(positions)

        for i in tqdm(
            range(start_index, end_index),
            desc=f"Forward Testing for {end_index + 1} days",
        ):
            any_is_active = False
            for ticker, tuple_df_pos in dict_score_dfs.items():
                score_df, this_pos = tuple_df_pos
                if (
                    not score_df.empty
                    and score_df["exit_signal"].loc[i]
                    and this_pos.is_active
                ):
                    this_pos.is_active = False
                    current_df = current_dict_dfs[ticker].loc[i]
                    exit_timestamp, exit_price = (
                        TimeHandler.get_clean_datetime_from_string(
                            current_df["timestamp"]
                        ),
                        current_df["close"],
                    )

                    this_pos.exit_timestamp = exit_timestamp
                    this_pos.exit_price = exit_price
                any_is_active = any_is_active or this_pos.is_active

            if not any_is_active:
                break

        self.strat.zero_data()
        return current_dict_dfs, dict_score_dfs

    def handle_remaining_positions(self, current_dict_dfs, positions):
        for pos in positions:
            if pos.is_active:
                pos.is_active = False
                current_df = current_dict_dfs[pos.ticker].iloc[-1]
                exit_timestamp, exit_price = (
                    TimeHandler.get_clean_datetime_from_string(current_df["timestamp"]),
                    current_df["close"],
                )
                pos.exit_timestamp = exit_timestamp
                pos.exit_price = exit_price

            pos.health_df = current_dict_dfs[pos.ticker]

            if self.print_terminal:
                print(pos)

    def graph_positions(self, dict_score_dfs, min_start_index):
        for ticker, tuple_df_pos in dict_score_dfs.items():
            score_df, this_pos = tuple_df_pos
            to_graph = pd.concat(
                [
                    self.dict_of_dfs[ticker][["close", "timestamp"]][
                        min_start_index - 1:
                    ],
                    score_df[["score", "health_score"]],
                ],
                axis=1,
            )

            list_dates = [this_pos.timestamp, this_pos.exit_timestamp]
            list_dates = list(map(TimeHandler.get_string_from_datetime, list_dates))

            to_graph["graph_score"] = to_graph["score"] * 10 + to_graph["close"].mean()
            to_graph["graph_health_score"] = (
                to_graph["health_score"] * 10 + to_graph["close"].mean()
            )

            fig = to_graph.plot(
                x="timestamp",
                y=[
                    to_graph["graph_score"],
                    to_graph["close"],
                    to_graph["graph_health_score"],
                ],
                title=f"Stock Ticker: {ticker}",
            )

            to_graph["cleaned_timestamp"] = to_graph["timestamp"].apply(
                TimeHandler.get_clean_string_from_string
            )
            list_locs = find_loc(to_graph, list_dates)

            self.add_graph_annotations(
                fig, to_graph.loc[list_locs[0]], this_pos, "Enter"
            )
            self.add_graph_annotations(
                fig, to_graph.loc[list_locs[1]], this_pos, "Exit"
            )
            fig.update_layout(showlegend=False)
            fig.show()

    def add_graph_annotations(self, input_fig, list_locs, curr_position, position_do):
        input_fig.add_annotation(
            x=list_locs["timestamp"].iloc[0],
            y=list_locs["close"].iloc[0],
            text=f"{position_do} date (type: {curr_position.order_type})",
            showarrow=True,
            arrowhead=1,
        )
