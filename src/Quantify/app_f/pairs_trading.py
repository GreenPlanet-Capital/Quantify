from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import numpy as np
import statsmodels.api as sm
from backtesting.test import SMA, GOOG
import pandas as pd
import yfinance as yf

pair = "XLI", "XLK"

data = yf.download(
    tickers=pair,
    period="1y",
    interval="1d",
    group_by="ticker",
    auto_adjust=True,
    prepost=True,
    threads=True,
    proxy=None,
)

ticker_1_df = data[pair[0]]
ticker_2_df = data[pair[1]]

ticker_1_df[pair[1]] = ticker_2_df.Close
ticker_2_df[pair[0]] = ticker_1_df.Close


class SmaCross(Strategy):
    sensitivity = 1
    other_symbol = ""
    beta_lookback = None

    def init(self):
        pass

    def next(self):
        my_price = (
            self.data.Close[-self.beta_lookback :]
            if len(self.data.Close) >= self.beta_lookback
            else self.data.Close
        )
        other_tic_price = (
            self.data.df[self.other_symbol].iloc[-self.beta_lookback :]
            if len(self.data.Close) >= self.beta_lookback
            else self.data.df[self.other_symbol]
        )
        b = sm.OLS(
            my_price,
            other_tic_price,
        ).fit()  # add checks for non-linear models
        b = b.params[0]
        spread = my_price - b * other_tic_price
        mean_spread = np.mean(spread)
        std_dev = np.std(spread)
        higher_limit = mean_spread + self.sensitivity * std_dev
        lower_limit = mean_spread - self.sensitivity * std_dev

        if self.position.size >= 0 and spread[-1] > higher_limit:  # aapl
            self.sell()
        elif self.position.size <= 0 and spread[-1] < lower_limit:
            self.buy()


# spread -> if spread > sensitivity1
#
for this_df, other_symbol in [(ticker_2_df, pair[0]), (ticker_1_df, pair[1])]:
    bt = Backtest(this_df, SmaCross, commission=0.002, exclusive_orders=True)
    stats = bt.run(sensitivity=1, other_symbol=other_symbol, beta_lookback=150)
    bt.plot()
