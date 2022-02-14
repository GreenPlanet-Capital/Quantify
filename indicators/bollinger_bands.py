from pandas import DataFrame
from indicators.base_indicator import BaseIndicator
import matplotlib.pyplot as plt
from constants.utils import normalize_values


class BollingerBands(BaseIndicator):
    def __init__(self, num_periods, lookback_bb) -> None:
        super().__init__()
        self.num_periods = num_periods
        self.lookback_bb = lookback_bb

    def run(self):
        super().run()

        boll_bands = DataFrame()

        # Define std & sma
        standard_dev = self._dataframe['close'].rolling(window=self.num_periods).std()
        simple_moving_avg = self._dataframe['close'].rolling(window=self.num_periods).mean()

        # Calculate bands
        upper_bands = simple_moving_avg + standard_dev * 2
        lower_bands = simple_moving_avg - standard_dev * 2

        # Add to df
        boll_bands['upper_bb'] = upper_bands
        boll_bands['lower_bb'] = lower_bands

        boll_bands['diff_bb'] = 1 - normalize_values(upper_bands[-self.lookback_bb:] -
                                                     lower_bands[-self.lookback_bb:], 0, 1)
        boll_bands['sma'] = simple_moving_avg

        self.boll_bands = boll_bands
        self._zero_dataframe()
        return boll_bands

    def graph(self):
        self._dataframe['close'].plot(label='Close prices', color='skyblue')
        self.boll_bands['upper_bb'].plot(label='Upper BB', linestyle='--', linewidth=1, color='black')
        self.boll_bands['sma'].plot(label='Middle BB', linestyle='--', linewidth=1.2, color='grey')
        self.boll_bands['lower_bb'].plot(label='Lower BB', linestyle='--', linewidth=1, color='black')
        plt.legend(loc='upper left')
        plt.title('Stock Bollinger Bands')
        plt.show()
