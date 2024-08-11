from typing import List, Dict, Tuple
from pandas import DataFrame
import pandas as pd
from Quantify.monitors.trailing_monitor import TrailingMonitor
from Quantify.positions.position import Position
from Quantify.strats.base_strategy import BaseStrategy


class PortfolioMonitor:
    def __init__(
        self,
        list_of_final_symbols: List[str],
        dict_of_dfs: Dict[str, DataFrame],
        strat: BaseStrategy,
        exchangeName: str,
    ):
        self.list_of_final_symbols = list_of_final_symbols
        self.dict_of_dfs = dict_of_dfs
        self.strat = strat
        self.exchangeName = exchangeName

    def monitor_health(self) -> None:
        min_start_index = self.strat.timeframe.length
        assert min_start_index <= len(self.dict_of_dfs[self.list_of_final_symbols[0]])
        self.strat.set_data(
            list_of_tickers=self.list_of_final_symbols,
            dict_of_dataframes={
                k: v[:min_start_index] for k, v in self.dict_of_dfs.items()
            },
            exchangeName=self.exchangeName,
        )

        self.strat.instantiate_indicator_mgr()

        opps = self.strat.run()
        for op in opps:
            op.order_type = 1  # 1 is for long, -1 is for short, 0 is for neutral

        positions: List[Position] = [Position(op) for op in opps]

        self.strat.set_data(
            list_of_tickers=self.list_of_final_symbols,
            dict_of_dataframes=self.dict_of_dfs,
            exchangeName=self.exchangeName,
        )

        health_monitor = TrailingMonitor(
            self.strat.sid, "Trailing Health Check", self.strat
        )
        dict_score_dfs: Dict[str, Tuple[pd.DataFrame, Position]] = (
            health_monitor.multiple_health_check(positions)
        )

        for pos in positions:
            last_row = dict_score_dfs[pos.ticker][0].iloc[-1]

            pos.metadata["score"] = last_row["score"]
            pos.metadata["health_score"] = last_row["health_score"]
            pos.metadata["exit_signal"] = last_row["exit_signal"]

            print(pos)
