from pandas import DataFrame
from constants.utils import normalize_values
from indicators.base_indicator import BaseIndicator


class Rsi(BaseIndicator):
    def __init__(self, window_length=14) -> None:
        super().__init__()
        self.window_length = window_length

    def run(self, input_dataframe: DataFrame):
        super().run(input_dataframe)

        assert len(input_dataframe[
                       'close']) >= self.window_length + 1, "Not enough entries in input dataframe to calculate RSI"

        rsi_df = DataFrame()

        # Calculate Price Differences
        rsi_df['diff'] = input_dataframe['close'].diff(1)

        # Calculate Avg. Gains/Losses
        rsi_df['gain'] = rsi_df['diff'].clip(lower=0).round(2)
        rsi_df['loss'] = rsi_df['diff'].clip(upper=0).abs().round(2)

        # Get initial Averages
        rsi_df['avg_gain'] = rsi_df['gain'].rolling(window=self.window_length,
                                                    min_periods=self.window_length).mean()[:self.window_length + 1]
        rsi_df['avg_loss'] = rsi_df['loss'].rolling(window=self.window_length,
                                                    min_periods=self.window_length).mean()[:self.window_length + 1]

        # TODO Optimize dataframe operations

        # Get WMS averages
        # Average Gains
        for i, row in enumerate(rsi_df['avg_gain'].iloc[self.window_length + 1:]):
            rsi_df['avg_gain'].iloc[i + self.window_length + 1] = \
                (rsi_df['avg_gain'].iloc[i + self.window_length] *
                 (self.window_length - 1) +
                 rsi_df['gain'].iloc[i + self.window_length + 1]) \
                / self.window_length

        # Average Losses
        for i, row in enumerate(rsi_df['avg_loss'].iloc[self.window_length + 1:]):
            rsi_df['avg_loss'].iloc[i + self.window_length + 1] = \
                (rsi_df['avg_loss'].iloc[i + self.window_length] *
                 (self.window_length - 1) +
                 rsi_df['loss'].iloc[i + self.window_length + 1]) \
                / self.window_length

        # Calculate RS Values
        rsi_df['rs'] = rsi_df['avg_gain'] / rsi_df['avg_loss']

        # Calculate RSI
        rsi_df['rsi'] = 100 - (100 / (1.0 + rsi_df['rs']))

        to_return_rsi_df = DataFrame()
        to_return_rsi_df['rsi'] = rsi_df['rsi']

        to_return_rsi_df['normalized rsi'] = normalize_values(normalize_values(to_return_rsi_df['rsi'], -1, 1).abs(), 0,
                                                              1)

        self.insert_all_into_df(input_dataframe, to_return_rsi_df, ['rsi', 'normalized rsi'])

