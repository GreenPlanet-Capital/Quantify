from typing import List

import pandas as pd
from constants.timeframe import TimeFrame
from constants.utils import normalize_values
from indicators.macd import Macd
from indicators.rsi import Rsi
from opportunity.opportunity import Opportunity
from strats.base_strategy import BaseStrategy

class Macd_Rsi(BaseStrategy):
    def __init__(self, timeframe: TimeFrame, lookback) -> None:
        super().__init__(timeframe, lookback)
        self.rsi = Rsi()
        self.macd = Macd(lower_ma=12, upper_ma=26, signal_length=9)
    
    def run(self) -> List[Opportunity]:
        """
        Requires self.list_of_tickers and self.dict_of_dataframes to be set
        Returns a List of Opportunity objects or an empty List
        """
        super().run()

        ticker_to_indicators_df = dict()
        
        for ticker in self.list_of_tickers[:1]:
            self.rsi.set_dataframe(self.dict_of_dataframes[ticker])
            self.macd.set_dataframe(self.dict_of_dataframes[ticker])
            
            ticker_to_indicators_df[ticker] = self._score()

        
        self._zero_data()



    def _score(self) -> pd.DataFrame:
        rsi: pd.DataFrame = self.rsi.run()
        macd: pd.DataFrame = self.macd.run()
        indicators_df = pd.concat([rsi, macd], axis=1)

        indicators_df['difference'] = indicators_df['MACD'] - indicators_df['MACD Signal Line']
        
        indicators_df['Normalized difference'] = 1 - normalize_values(normalize_values(indicators_df['difference'], -1, 1).abs(), 0, 1)
        indicators_df['Normalized MACD'] = normalize_values(normalize_values(indicators_df['MACD'], -1, 1).abs(), 0, 1)
        indicators_df['Normalized RSI'] = normalize_values(normalize_values(indicators_df['rsi'], -1, 1).abs(), 0, 1)
        indicators_df['Shifted Normal RSI'] = indicators_df['Normalized RSI'].shift(1)
        indicators_df['Buy/Sell Signal'] = 0
        # Calculate +1 for buy and -1 for sell
        for i, row in indicators_df.iterrows():
            if (i==0):
                continue
            print()
            macd_val = indicators_df.iloc[i-1]['MACD']
            macd_signal_val = indicators_df.iloc[i-1]['MACD Signal Line']

            if macd_val > macd_signal_val:
                signal = -1
            elif macd_val < macd_signal_val:
                signal = 1
            else:
                signal = 0

            indicators_df.at[i,'Buy/Sell Signal'] = signal

        # Calculate score
        indicators_df['Score'] = 0.5*indicators_df['Shifted Normal RSI'] + \
                                0.5*indicators_df['Normalized difference']*indicators_df['Normalized MACD']
        
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        print(indicators_df[['Score', 'Buy/Sell Signal']])

        return indicators_df
        

        
        

