from typing import Dict, List

from pandas import DataFrame
from tqdm import tqdm
import pandas as pd

from constants.utils import buy_sell_mva
from indicators.indicator_manager import IndicatorManager

pd.options.mode.chained_assignment = None  # default='warn'
from DataManager.utils.timehandler import TimeHandler
from constants.timeframe import TimeFrame
from indicators.macd import Macd
from indicators.rsi import Rsi
from indicators.bollinger_bands import BollingerBands
from positions.opportunity import Opportunity
from positions.position import Position
from strats.base_strategy import BaseStrategy


class Macd_Rsi_Boll(BaseStrategy):
    def __init__(self, sid, name, timeframe: TimeFrame, lookback) -> None:
        self.lookback = lookback
        super().__init__(sid, name, timeframe, lookback)

    def instantiate_indicator_mgr(self):
        self.indicator_manager = IndicatorManager([Rsi(window_length=14),
                                                   Macd(lower_ma=12, upper_ma=26, signal_length=9),
                                                   BollingerBands(num_periods=20, lookback_bb=self.lookback)],
                                                  self.list_of_tickers)

    def _score(self, input_df: DataFrame):
        # Shifting RSI down by one
        input_df['shifted rsi'] = input_df['rsi'].shift(1)
        input_df['buy/sell signal'] = 0

        # Calculate +1 for buy and -1 for sell
        input_df['buy/sell signal'] = input_df['macd'].apply(buy_sell_mva)

        # Calculate score
        score_df = DataFrame()

        score_df['score'] = 0.25 * input_df['shifted rsi'] / 100 + \
                                 0.25 * input_df['normalized difference'] + 0.25 * \
                                           input_df['normalized macd'] + \
                                 0.25 * input_df['diff_bb']
        score_df['timestamp'] = input_df['timestamp']
        return score_df
