from pandas import DataFrame
from Quantify.indicators.base_indicator import BaseIndicator
import matplotlib.pyplot as plt
from Quantify.constants.utils import normalize_values


class BollingerBands(BaseIndicator):
    def __init__(self, num_periods, lookback_bb) -> None:
        super().__init__()
        self.num_periods = num_periods
        self.lookback_bb = lookback_bb

    def run(self, input_dataframe: DataFrame):
        super().run(input_dataframe)
        boll_bands = DataFrame()

        # Define std & sma
        standard_dev = input_dataframe['close'].rolling(window=self.num_periods).std()
        simple_moving_avg = input_dataframe['close'].rolling(window=self.num_periods).mean()

        # Calculate bands
        upper_bands = simple_moving_avg + standard_dev * 2
        lower_bands = simple_moving_avg - standard_dev * 2

        # Add to df
        boll_bands['upper_bb'] = upper_bands
        boll_bands['lower_bb'] = lower_bands

        boll_bands['diff_bb'] = 1 - normalize_values(upper_bands[-self.lookback_bb:] -
                                                     lower_bands[-self.lookback_bb:], 0, 1)
        boll_bands['sma_bb'] = simple_moving_avg

        self.insert_all_into_df(input_dataframe, boll_bands, ['upper_bb', 'lower_bb', 'diff_bb', 'sma_bb'])

    def graph(self, input_df: DataFrame):
        input_df['close'].plot(label='Close prices', color='skyblue')
        input_df['upper_bb'].plot(label='Upper BB', linestyle='--', linewidth=1, color='black')
        input_df['sma_bb'].plot(label='Middle BB', linestyle='--', linewidth=1.2, color='grey')
        input_df['lower_bb'].plot(label='Lower BB', linestyle='--', linewidth=1, color='black')
        plt.legend(loc='upper left')
        plt.title('Stock Bollinger Bands')
        plt.show()
