from typing import List

from pandas import DataFrame
from indicators.macd import Macd
from indicators.rsi import Rsi
from opportunity.opportunity import Opportunity
from strats.base_strategy import BaseStrategy

class Macd_Rsi(BaseStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.rsi = Rsi()
        self.macd = Macd()
    
    def run(self) -> List[Opportunity]:
        """
        Requires self.list_of_tickers and self.dict_of_dataframes to be set
        Modifies the original dict of dataframes and includes outputs from the indicators used
        Returns a List of Opportunity objects or an empty List
        """
        super().run()
        
        for ticker in self.list_of_tickers[:1]:
            self.rsi.set_dataframe(self.dict_of_dataframes[ticker])
            self.macd.set_dataframe(self.dict_of_dataframes[ticker])
            
            rsi: DataFrame = self.rsi.run()
            print (rsi)
            self.macd.run()

        

        self._zero_data()
        

