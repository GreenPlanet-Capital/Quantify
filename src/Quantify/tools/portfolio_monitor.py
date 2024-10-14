from typing import List, Dict, Tuple, Union
from plotly.graph_objs import Figure
from pandas import DataFrame
import pandas as pd
from Quantify.monitors.trailing_monitor import TrailingMonitor
from Quantify.positions.position import Position
from Quantify.strats.base_strategy import BaseStrategy
from Quantify.constants.graphhandler import GraphHandler
from DataManager.utils.timehandler import TimeHandler


class PortfolioMonitor:
    def __init__(
        self,
        dict_of_dfs: Dict[str, DataFrame],
        strat: BaseStrategy,
        exchangeName: str,
    ):
        self.dict_of_dfs = dict_of_dfs
        self.strat = strat
        self.exchangeName = exchangeName

    def monitor_health(
        self,
        print_debug: bool = True,
        graph: bool = False,
        open_plot: bool = True,
        default_order_type: int = 1,
    ) -> Union[None, Figure]:
        min_start_index = self.strat.timeframe.length

        # make it more efficient by bundling similar dataframes together
        for symbol, df in self.dict_of_dfs.items():
            if min_start_index > len(df):
                print(f"Dataframe for {symbol} is too short for the strategy")
                continue

            self.strat.set_data(
                list_of_tickers=[symbol],
                dict_of_dataframes={symbol: df[:min_start_index]},
                exchangeName=self.exchangeName,
            )

            self.strat.instantiate_indicator_mgr()

            opps = self.strat.run()
            for op in opps:
                op.order_type = default_order_type

            positions: List[Position] = [Position(op) for op in opps]

            self.strat.set_data(
                list_of_tickers=[symbol],
                dict_of_dataframes={symbol: df},
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

                pos.exit_timestamp = TimeHandler.get_datetime_from_string(
                    last_row["timestamp"]
                )

                pos.exit_price = last_row["close"]

                if print_debug:
                    print(pos)

                if graph:
                    fig = GraphHandler.graph_positions(
                        self.dict_of_dfs,
                        dict_score_dfs,
                        show_enter_exit=True,
                        open_plot=open_plot,
                    )
                    if not open_plot:
                        return fig
