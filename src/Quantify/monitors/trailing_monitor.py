import numpy as np
from DataManager.utils.timehandler import TimeHandler
from pandas import DataFrame

from Quantify.monitors.base_monitor import BaseMonitor
from Quantify.positions.position import Position
from Quantify.strats.base_strategy import BaseStrategy


class TrailingMonitor(BaseMonitor):
    def __init__(self, sid: int, name: str, strat: BaseStrategy):
        super(TrailingMonitor, self).__init__(sid, name, strat)

    def health_check(self, cur_position: Position) -> DataFrame:
        super().health_check(cur_position)

        ticker, transaction_date = cur_position.ticker, cur_position.timestamp
        self.strat.indicator_manager.retrieve_single_score(
            ticker, self.strat.dict_of_dataframes, self.strat._score
        )

        df_all_scores = self.strat.dict_of_dataframes[ticker].copy()

        df_all_scores["health_score"] = 0.60 * df_all_scores[
            "rsi_health_score"
        ] + 0.40 * (1 - df_all_scores["normalized macd"].replace({0: np.nan})).fillna(0)

        df_after_opp = df_all_scores[
            df_all_scores["timestamp"].apply(TimeHandler.get_datetime_from_string)
            > transaction_date
        ]

        # Trailing Stop Loss (7.5%)
        df_after_opp["daily_percent_change_price"] = (
            df_after_opp["close"].pct_change().fillna(0)
        )
        df_after_opp["total_percent_change_price"] = (
            df_after_opp["daily_percent_change_price"].add(1).cumprod().sub(1)
        )

        if cur_position.order_type == 1:
            df_after_opp["current_peak_change_price"] = df_after_opp["close"].cummax()
        else:
            df_after_opp["current_peak_change_price"] = df_after_opp["close"].cummin()

        df_after_opp["trailing_stop_price"] = df_after_opp[
            "current_peak_change_price"
        ] * (1 + (-cur_position.order_type * 0.075))

        # Stop Health Score (30%)
        df_after_opp["current_peak_change_health"] = df_after_opp[
            "health_score"
        ].cummax()
        df_after_opp["trailing_stop_health"] = df_after_opp[
            "current_peak_change_health"
        ] * (1 - 0.30)

        # Exit Signal
        df_after_opp["exit_signal"] = (
            df_after_opp["health_score"] < df_after_opp["trailing_stop_health"]
        )

        if cur_position.order_type == 1:
            df_after_opp["exit_signal"] |= (
                df_after_opp["close"] < df_after_opp["trailing_stop_price"]
            )
        else:
            df_after_opp["exit_signal"] |= (
                df_after_opp["close"] > df_after_opp["trailing_stop_price"]
            )

        # Current stats
        df_after_opp["daily_percent_change_health"] = (
            df_after_opp["health_score"].pct_change().fillna(0)
        )
        df_after_opp["daily_percent_change_health"][
            df_after_opp["daily_percent_change_health"] == np.inf
        ] = 1
        df_after_opp["total_percent_change_health"] = (
            df_after_opp["daily_percent_change_health"].add(1).cumprod().sub(1)
        )

        return df_after_opp
