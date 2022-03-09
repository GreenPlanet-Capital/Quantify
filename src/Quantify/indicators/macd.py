import numpy as np
from pandas import DataFrame
from Quantify.constants.utils import normalize_values
from Quantify.indicators.base_indicator import BaseIndicator
import matplotlib.pyplot as plt


class Macd(BaseIndicator):
    def __init__(self, lower_ma, upper_ma, signal_length) -> None:
        super().__init__()
        self.lower_ma = lower_ma
        self.upper_ma = upper_ma
        self.signal_length = signal_length

    def run(self, input_dataframe: DataFrame):
        super().run(input_dataframe)

        exp1 = input_dataframe["close"].ewm(span=self.lower_ma, adjust=False).mean()
        exp2 = input_dataframe["close"].ewm(span=self.upper_ma, adjust=False).mean()
        macd = exp1 - exp2
        exp3 = macd.ewm(span=self.signal_length, adjust=False).mean()

        macd_and_signal_line = DataFrame()
        macd_and_signal_line["macd"] = macd
        macd_and_signal_line["macd signal line"] = exp3

        for i in range(0, self.upper_ma):
            macd_and_signal_line["macd"].iloc[i] = None
            macd_and_signal_line["macd signal line"].iloc[i] = None

        # Calculating indicator information and normalizing
        macd_and_signal_line["difference"] = (
            macd_and_signal_line["macd"] - macd_and_signal_line["macd signal line"]
        )
        macd_and_signal_line["difference"] = np.exp(
            -1e2 * np.power(macd_and_signal_line["difference"], 2)
        )

        macd_and_signal_line["normalized difference"] = normalize_values(
            macd_and_signal_line["difference"], 0, 1
        )
        macd_and_signal_line["normalized macd"] = normalize_values(
            normalize_values(macd_and_signal_line["macd"], -1, 1).abs(), 0, 1
        )

        macd_and_signal_line[
            ["normalized difference", "normalized macd"]
        ] = macd_and_signal_line[["normalized difference", "normalized macd"]].fillna(0)

        self.insert_all_into_df(
            input_dataframe,
            macd_and_signal_line,
            ["normalized macd", "macd", "macd signal line", "normalized difference"],
        )

    def graph(self, input_dataframe: DataFrame):
        input_dataframe["macd"].plot(label="macd", color="g")
        ax = input_dataframe["macd signal line"].plot(label="signal line", color="r")
        input_dataframe.plot(ax=ax, secondary_y=True, label="AAPL")

        ax.set_ylabel("macd")
        ax.right_ax.set_ylabel("Price $")
        ax.set_xlabel("Date")

        lines = ax.get_lines() + ax.right_ax.get_lines()
        ax.legend(lines, [ll.get_label() for ll in lines], loc="upper left")
        plt.show()
