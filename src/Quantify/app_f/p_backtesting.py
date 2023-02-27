from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA, GOOG
import pandas as pd
import ta
import numpy as np
from Quantify.app_f.data_retrieval import get_specific_data
from Quantify.constants.utils import buy_sell_mva, normalize_values, buy_sell_rsi
from tqdm import tqdm


class MacdRsiBoll(Strategy):
    def init(self, window_length=14, lower_ma=12, upper_ma=26, signal_length=9):
        price = self.data.Close.s

        self.rsi = pd.Series(self.I(ta.momentum.rsi, price, window_length))
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

        self.macd = pd.Series((self.I(ta.trend.macd, price, window_length, plot=False)))

        self.normalized_macd = normalize_values(
            normalize_values(self.macd, -1, 1).abs(),
            0,
            1,
        )

        self.upper_boll = pd.Series(
            self.I(ta.volatility.bollinger_hband, price, window_length, plot=False)
        )
        self.lower_boll = pd.Series(
            self.I(ta.volatility.bollinger_lband, price, window_length, plot=False)
        )
        self.diff_boll = 1 - normalize_values(self.upper_boll - self.lower_boll, 0, 1)

        self.buy_sell_signal = self.I(
            lambda: self.rsi.apply(buy_sell_rsi), name="Buy/Sell Signal", plot=False
        )

        self.rsi_score = np.where(
            pd.Series(self.buy_sell_signal) == 1, 1 - self.rsi / 100, self.rsi
        )

        self.pre_score = (
            0.30 * self.rsi_normalized
            + 0.35 * (self.macd_diff * self.normalized_macd) ** 0.5
            + 0.35 * self.diff_boll
        )
        self.pre_score = normalize_values(
            self.pre_score,
            0,
            1,
        )
        self.score = self.I(lambda: self.pre_score, name="Score")

        self.health_score = 0.60 * self.rsi_normalized + 0.40 * (
            1 - self.normalized_macd.replace({0: np.nan})
        ).fillna(0)
        self.health_score = normalize_values(
            self.health_score,
            0,
            1,
        )
        self.health_score = self.I(lambda: self.health_score, name="Health Score")
        self.high_score = self.I(
            lambda: np.full(shape=len(self.data), fill_value=0.70),
            name="High Score",
            plot=False,
        )
        self.low_score = self.I(
            lambda: np.full(shape=len(self.data), fill_value=0.30),
            name="Low Score",
            plot=False,
        )

    def next(self):
        if crossover(self.score, self.high_score) and not self.position.is_long:
            if self.buy_sell_signal[-1] == 1:
                # print("buy")
                self.buy(size=self.score[-1], sl=0.075)
            else:
                # print("sell")
                self.sell(size=self.score[-1], sl=0.075, limit=0.065)

        elif self.position.size != 0 and self.health_score[-1] < self.low_score[-1]:
            # print("close")
            for t in self.trades:
                t.close()

        for t in self.trades:
            health_series = pd.Series(self.health_score[t.entry_bar :])
            current_peak_change_health = health_series.cummax()
            trailing_stop_health = current_peak_change_health * (1 - 0.30)
            exit_signal = health_series < trailing_stop_health

            if exit_signal.iloc[-1]:
                # print("close top loss")
                t.close()


if __name__ == "__main__":
    list_of_final_symbols, dict_of_dfs = get_specific_data(fetch_data=False)
    list_all_bt = []
    total_equity_return = 0

    for ticker, TICKER_DF in tqdm(dict_of_dfs.items()):
        TICKER_DF = TICKER_DF.rename(
            columns={
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume",
            }
        )

        TICKER_DF = TICKER_DF.set_index(pd.to_datetime(TICKER_DF["timestamp"])).drop(
            "timestamp", axis=1
        )

        bt = Backtest(TICKER_DF, MacdRsiBoll, commission=0.002, exclusive_orders=True)
        stats = bt.run()

        cur_return = stats["Equity Final [$]"] - 10000
        list_all_bt.append((cur_return, bt, ticker))
        total_equity_return += cur_return

    list_all_bt.sort(reverse=True, key=lambda d: d[0])
    top_n = 5

    print([obj[2] for obj in list_all_bt[:top_n]])
    print([obj[2] for obj in list_all_bt[-top_n:]])

    for stat_return, bt_return, ticker_return in list_all_bt[:top_n]:
        bt_return.plot(open_browser=False, filename=f"graph_files/{ticker_return}")

    for stat_return, bt_return, ticker_return in list_all_bt[-top_n:]:
        bt_return.plot(open_browser=False, filename=f"graph_files/{ticker_return}")

    print(f"{total_equity_return=}")
    print(f"{round(total_equity_return / (len(list_all_bt) * 10000) * 100, 2)}")

    # bt = Backtest(GOOG, MacdRsiBoll, commission=0.002, exclusive_orders=True)
    # bt.run()
    # bt.plot(open_browser=False, filename=f"graph_files/GOOG")
