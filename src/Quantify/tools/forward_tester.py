from typing import List, Dict, Tuple
from pandas import DataFrame
from DataManager.utils.timehandler import TimeHandler
import pandas as pd
from tqdm import tqdm
from Quantify.constants.graphhandler import GraphHandler
from Quantify.constants.utils import find_loc, normalize_values
from Quantify.monitors.trailing_monitor import TrailingMonitor
from Quantify.positions.opportunity import Opportunity
from Quantify.positions.position import Position
from Quantify.strats.base_strategy import BaseStrategy
from Quantify.tools.base_tester import BaseTester
from pprint import pprint


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
        self, graph_positions=False, print_terminal=False, amount_per_pos=100
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
        good_opps, last_op_idx = self.get_good_mix_of_opps(opps, self.num_top)
        positions: List[Position] = [Position(op) for op in good_opps]

        if print_terminal:
            print("-" * 50)
            print("Started Trading Period. Below are current positions")

            for pos in positions:
                print(pos)

        min_df_len = min([len(df) for df in self.dict_of_dfs.values()])
        assert min_df_len >= min_start_index

        current_dict_dfs, dict_score_dfs = self.advance_forward(
            min_start_index, min_df_len, positions, opps, last_op_idx
        )

        if print_terminal:
            print("-" * 50)
            print("Ended Trading Period. Below are current positions")

        self.handle_remaining_positions(current_dict_dfs, positions)

        stats = self.calculate_stats(positions, opps, amount_per_pos)
        pprint(stats)

        if graph_positions:
            GraphHandler.graph_positions(self.dict_of_dfs, dict_score_dfs, min_start_index)

        return positions

    def calculate_stats(
        self, positions: List[Position], opps: List[Opportunity], amount_per_pos: float
    ) -> float:
        stats = dict()

        total_profit = 0
        opps_scores = [op.metadata["score"] for op in opps]
        opps_scores = normalize_values(pd.Series(opps_scores), 0, 1).values

        opps_scores_dt = {op.ticker: score for op, score in zip(opps, opps_scores)}

        for pos in positions:
            shares = amount_per_pos / pos.default_price if pos.default_price > 0 else 0
            total_profit += (
                (pos.exit_price - pos.default_price)
                * pos.order_type
                * shares
                * opps_scores_dt[pos.ticker]
            )

        stats["pnl"] = total_profit
        stats["total_investment"] = amount_per_pos * self.num_top
        stats["port_return"] = total_profit / stats["total_investment"]

        return stats

    def advance_forward(
        self,
        start_index,
        end_index,
        positions: List[Position],
        opps: List[Opportunity],
        cur_opps_idx: int,
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
        dict_score_dfs: Dict[str, Tuple[pd.DataFrame, Position]] = (
            health_monitor.multiple_health_check(positions)
        )

        num_active = self.num_top

        for i in tqdm(
            range(start_index, end_index),
            desc=f"Forward Testing for {end_index - start_index + 1} days",
        ):
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

                    num_active -= 1

            while cur_opps_idx < len(opps) - 1 and num_active < self.num_top:
                next_good_opps, cur_opps_idx = self.get_good_mix_of_opps(
                    opps[cur_opps_idx + 1 :], self.num_top - num_active
                )
                for op in next_good_opps:
                    pos = Position(op)
                    pos.default_price = current_dict_dfs[pos.ticker].loc[i]["close"]
                    positions.append(pos)

                    dict_score_dfs[pos.ticker] = (health_monitor.health_check(pos), pos)
                    num_active += 1

        self.strat.zero_data()
        return current_dict_dfs, dict_score_dfs

    def handle_remaining_positions(
        self, current_dict_dfs: dict[str, pd.DataFrame], positions: List[Position]
    ):
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
