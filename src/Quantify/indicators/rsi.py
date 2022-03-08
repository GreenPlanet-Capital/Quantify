import numpy as np
from pandas import DataFrame
from Quantify.constants.utils import normalize_values
from Quantify.indicators.base_indicator import BaseIndicator
import pandas as pd


class Rsi(BaseIndicator):
    def __init__(self, window_length=14) -> None:
        super().__init__()
        self.window_length = window_length

    def run(self, input_dataframe: DataFrame):
        super().run(input_dataframe)

        assert (
            len(input_dataframe["close"]) >= self.window_length + 1
        ), "Not enough entries in input dataframe to calculate RSI"

        delta = input_dataframe["close"].diff()

        up = delta.copy()
        up[up < 0] = 0
        up = pd.Series.ewm(up, alpha=1 / self.window_length).mean()

        down = delta.copy()
        down[down > 0] = 0
        down *= -1
        down = pd.Series.ewm(down, alpha=1 / self.window_length).mean()

        rsi = np.where(
            up == 0, 0, np.where(down == 0, 100, 100 - (100 / (1 + up / down)))
        )

        to_return_rsi_df = DataFrame()
        to_return_rsi_df["rsi"] = rsi

        to_return_rsi_df["normalized rsi"] = normalize_values(
            normalize_values(to_return_rsi_df["rsi"], -1, 1).abs(), 0, 1
        )

        self.insert_all_into_df(
            input_dataframe, to_return_rsi_df, ["rsi", "normalized rsi"]
        )
