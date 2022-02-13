import numpy as np
from pandas import DataFrame, Series
from constants.utils import normalize_values
from indicators.base_indicator import BaseIndicator
import matplotlib.pyplot as plt

class Macd(BaseIndicator):
    def __init__(self, lower_ma, upper_ma, signal_length) -> None:
        super().__init__()
        self.lower_ma = lower_ma
        self.upper_ma = upper_ma
        self.signal_length = signal_length

    def run(self):
        super().run()

        exp1 = self._dataframe['close'].ewm(span=self.lower_ma, adjust=False).mean()
        exp2 = self._dataframe['close'].ewm(span=self.upper_ma, adjust=False).mean()
        macd = exp1 - exp2
        exp3 = macd.ewm(span=self.signal_length, adjust=False).mean()

        macd_and_signal_line = DataFrame()
        macd_and_signal_line['MACD'] = macd
        macd_and_signal_line['MACD Signal Line'] = exp3

        for i in range(0, self.upper_ma):
            macd_and_signal_line['MACD'].iloc[i]=None
            macd_and_signal_line['MACD Signal Line'].iloc[i]=None

        #Calculating indicator information and normalizing
        macd_and_signal_line['difference'] = macd_and_signal_line['MACD'] - macd_and_signal_line['MACD Signal Line']
        macd_and_signal_line['Normalized difference'] = 1 - normalize_values(normalize_values(macd_and_signal_line['difference'], -1, 1).abs(), 0, 1)
        macd_and_signal_line['Normalized MACD'] = normalize_values(normalize_values(macd_and_signal_line['MACD'], -1, 1).abs(), 0, 1)
        
        
        
        self.macd_and_signal_line = macd_and_signal_line
        self._zero_dataframe()
        return macd_and_signal_line
        

    def graph(self, close_price_df: DataFrame):
        self.macd_and_signal_line['MACD'].plot(label='MACD', color='g')
        ax = self.macd_and_signal_line['MACD Signal Line'].plot(label='Signal Line', color='r')
        close_price_df.plot(ax=ax, secondary_y=True, label='AAPL')
        ax.set_ylabel('MACD')
        ax.right_ax.set_ylabel('Price $')
        ax.set_xlabel('Date')
        lines = ax.get_lines() + ax.right_ax.get_lines()
        ax.legend(lines, [l.get_label() for l in lines], loc='upper left')
        plt.show()