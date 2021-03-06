from pandas import DataFrame

from Quantify.constants.timeframe import TimeFrame
from Quantify.constants.utils import buy_sell_mva
from Quantify.indicators.macd import Macd
from Quantify.indicators.rsi import Rsi
from Quantify.strats.base_strategy import BaseStrategy
from Quantify.indicators.indicator_manager import IndicatorManager


class Macd_Rsi(BaseStrategy):
    def __init__(self, sid, name, timeframe: TimeFrame, lookback) -> None:
        super().__init__(sid, name, timeframe, lookback)

    def instantiate_indicator_mgr(self):
        self.indicator_manager = IndicatorManager(
            [Rsi(), Macd(lower_ma=12, upper_ma=26, signal_length=9)],
            self.list_of_tickers,
        )

    def _score(self, input_df: DataFrame):
        # Shifting RSI down by one
        input_df["shifted rsi"] = input_df["rsi"].shift(1)
        input_df["buy/sell signal"] = 0

        # Calculate +1 for buy and -1 for sell
        input_df["buy/sell signal"] = input_df["macd"].apply(buy_sell_mva)

        # Calculate score
        score_df = DataFrame()
        score_df["score"] = (
            0.3 * input_df["shifted rsi"] / 100
            + 0.35 * input_df["normalized difference"]
            + 0.35 * input_df["normalized macd"]
        )
        score_df["timestamp"] = input_df["timestamp"]

        return score_df
