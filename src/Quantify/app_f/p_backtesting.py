from tarfile import LENGTH_PREFIX
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA, GOOG
from numpy import ndarray
import pandas as pd
import ta
import numpy as np

from Quantify.app_f.get_data import *
from Quantify.constants.utils import buy_sell_mva, normalize_values
from Quantify.indicators.utils import IndicUtils


class MacdRsi(Strategy):
    def init(self, window_length=14, lower_ma=12, upper_ma=26, signal_length=9):
        price = self.data.Close.s

        self.rsi = pd.Series(self.I(ta.momentum.rsi, price, window_length, plot=False))
        self.rsi_normalized = normalize_values(
            normalize_values(self.rsi, -1, 1).abs(),
            0,
            1,
        )
        self.macd_diff = normalize_values(
            np.exp(
                -1e2
                * np.power(
                    pd.Series(
                        self.I(
                            ta.trend.macd_diff, price, lower_ma, upper_ma, plot=False
                        )
                    ),
                    2,
                )
            ),
            0,
            1,
        )

        self.macd = pd.Series(self.I(ta.trend.macd, price, window_length))

        self.normalized_macd = normalize_values(
            normalize_values(self.macd, -1, 1).abs(),
            0,
            1,
        )

        self.buy_sell_signal = self.macd.apply(buy_sell_mva)

        self.rsi_score = np.where(
            self.buy_sell_signal == 1, 1 - self.rsi / 100, self.rsi
        )

        self.pre_score = (
            0.3 * self.rsi_score + 0.35 * self.macd_diff + 0.35 * self.normalized_macd
        )
        self.pre_score = normalize_values(
            self.pre_score,
            0,
            1,
        )
        self.score = self.I(lambda: self.pre_score, name="Score")

        self.health_score = 0.60 * self.rsi_score + 0.40 * (
            1 - self.normalized_macd.replace({0: np.nan})
        ).fillna(0)
        self.health_score = normalize_values(
            self.health_score,
            0,
            1,
        )
        self.health_score = self.I(lambda: self.health_score, name="Health Score")
        self.high_score = np.full(shape=len(self.data), fill_value=0.50)
        self.low_score = np.full(shape=len(self.data), fill_value=0.10)

    def next(self):
        # print(self.position)
        if crossover(self.score, self.high_score) and not self.position.is_long:
            print(self.buy_sell_signal.iloc[-1])
            if self.buy_sell_signal.iloc[-1] == 1:
                print("buy")
                self.buy(size=10)
            else:
                print("sell")
                self.sell(size=10)
        elif self.position.size != 0 and crossover(self.low_score, self.health_score):
            print("close")
            self.trades[-1].close()


# list_of_final_symbols, dict_of_dfs = get_data()

# print(f"{list_of_final_symbols=}")

# ticker, TICKER_DF = list(dict_of_dfs.items())[0] # pick one stock

# TICKER_DF = TICKER_DF.rename(columns = {'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})

# TICKER_DF = TICKER_DF.set_index(pd.to_datetime(TICKER_DF['timestamp'])).drop('timestamp', axis=1)

bt = Backtest(GOOG, MacdRsi, commission=0.002, exclusive_orders=True)
stats = bt.run()
# print(stats)
bt.plot()
