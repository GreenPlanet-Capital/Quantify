from pandas import DataFrame
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from Quantify.indicators.utils import IndicUtils as IndicUtils
from Quantify.constants import utils as generic_utils
from Quantify.indicators.indicator_manager import IndicatorManager
from Quantify.constants.timeframe import TimeFrame
from Quantify.indicators.macd import Macd
from Quantify.indicators.rsi import Rsi
from Quantify.indicators.bollinger_bands import BollingerBands
from Quantify.strats.base_strategy import BaseStrategy


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
        # Shifting RSI down by one and constricting
        input_df['shifted rsi'] = input_df['rsi'].shift(1)
        input_df['c_shifted_rsi'] = input_df.apply(lambda row: IndicUtils.constrain(row['shifted rsi'], 20, 80), axis=1)
        input_df['zc_shifted_rsi'] = input_df.apply(lambda row: IndicUtils.nan_out_between_range(row['c_shifted_rsi'], 40, 60), axis=1)
        
        # Calculate +1 for buy and -1 for sell
        input_df['buy/sell signal'] = 0
        input_df['buy/sell signal'] = input_df['macd'].apply(generic_utils.buy_sell_mva)

        # Calculate different values for rsi based on buy and sell
        input_df['rsi_health_score'] = input_df.apply(lambda row: IndicUtils.account_for_buy_sell_signal(row['shifted rsi']/100, row['buy/sell signal']), axis=1)
        input_df['rsi_score'] = input_df.apply(lambda row: IndicUtils.account_for_buy_sell_signal(row['zc_shifted_rsi']/100, row['buy/sell signal']), axis=1)
        input_df['rsi_score'] = input_df['rsi_score'].fillna(0)
        
        # Focusing BB to only the middle range of 0.4 to 0.6
        # TODO
        
        # Calculate score
        score_df = DataFrame()

        #TODO Account for hard carry
        score_df['score'] = 0.50 * input_df['rsi_score'] + \
                            0.35 * input_df['normalized difference'] * input_df['normalized macd'] + \
                            0.15 * input_df['diff_bb']
        score_df['timestamp'] = input_df['timestamp']
        return score_df
